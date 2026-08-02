from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from .harness import run_agent
from .io import read_jsonl, write_json, write_jsonl
from .ledger import seal_files, verify_seal
from .report import render_markdown
from .scoring import score_forecasts
from .site import build_site
from .validation import parse_time, validate_forecast, validate_question, validate_resolution


def _indexed(rows: list[dict], name: str) -> dict[str, dict]:
    result = {}
    for row in rows:
        key = row.get("id") if name == "questions" else row.get("question_id")
        if not key:
            raise ValueError(f"{name} row has no identifier")
        if key in result:
            raise ValueError(f"duplicate {name} identifier: {key}")
        result[key] = row
    return result


def validate_bundle(questions_path: str, forecasts_path: str, resolutions_path: str | None) -> None:
    questions = read_jsonl(questions_path)
    forecasts = read_jsonl(forecasts_path)
    question_index = _indexed(questions, "questions")
    for question in questions:
        validate_question(question)
    for forecast in forecasts:
        question = question_index.get(forecast.get("question_id"))
        if question is None:
            raise ValueError(f"unknown forecast question_id: {forecast.get('question_id')}")
        validate_forecast(forecast, question)
    if resolutions_path:
        for resolution in read_jsonl(resolutions_path):
            question = question_index.get(resolution.get("question_id"))
            if question is None:
                raise ValueError(f"unknown resolution question_id: {resolution.get('question_id')}")
            validate_resolution(resolution, question)


def verify_live_submissions(rounds_root: Path) -> int:
    count = 0
    submission_dirs = sorted(
        path for path in rounds_root.glob("*/submissions/*") if path.is_dir()
    )
    for submission_dir in submission_dirs:
        round_root = submission_dir.parents[1]
        questions_path = round_root / "questions.jsonl"
        forecasts_path = submission_dir / "forecasts.jsonl"
        seal_path = submission_dir / "seal.json"
        if not questions_path.exists() or not forecasts_path.exists() or not seal_path.exists():
            raise ValueError(f"incomplete submission: {submission_dir}")
        validate_bundle(str(questions_path), str(forecasts_path), None)
        verify_seal(
            json.loads(seal_path.read_text(encoding="utf-8")),
            [questions_path, forecasts_path],
        )
        count += 1
    return count


def command_demo(output: Path) -> None:
    source = Path(__file__).resolve().parents[1] / "benchmarks" / "synthetic-smoke"
    output.mkdir(parents=True, exist_ok=True)
    for name in ("questions.jsonl", "forecasts.jsonl", "resolutions.jsonl"):
        shutil.copyfile(source / name, output / name)
    validate_bundle(
        str(output / "questions.jsonl"),
        str(output / "forecasts.jsonl"),
        str(output / "resolutions.jsonl"),
    )
    manifest = seal_files([output / "questions.jsonl", output / "forecasts.jsonl"])
    write_json(output / "seal.json", manifest)
    score = score_forecasts(
        read_jsonl(output / "forecasts.jsonl"), read_jsonl(output / "resolutions.jsonl")
    )
    write_json(output / "scorecard.json", score)
    (output / "scorecard.md").write_text(render_markdown(score), encoding="utf-8")
    print(f"Validated 6 time-safe forecasts")
    print(f"Seal: {manifest['combined_sha256'][:16]}...")
    print(f"Mean Brier: {score['mean_brier']:.4f}")
    print(f"Skill vs 0.5: {score['brier_skill_vs_0_5']:.1%}")
    print(f"Report: {output / 'scorecard.md'}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="open-market-eval")
    subparsers = parser.add_subparsers(dest="action", required=True)
    demo = subparsers.add_parser("demo", help="run the sealed synthetic forecasting loop")
    demo.add_argument("--output", default="runs/demo", type=Path)
    validate = subparsers.add_parser("validate", help="validate temporal integrity and schemas")
    validate.add_argument("--questions", required=True)
    validate.add_argument("--forecasts", required=True)
    validate.add_argument("--resolutions")
    seal = subparsers.add_parser("seal", help="hash question and forecast ledgers")
    seal.add_argument("paths", nargs="+")
    seal.add_argument("--output", default="seal.json")
    score = subparsers.add_parser("score", help="score resolved binary forecasts")
    score.add_argument("--forecasts", required=True)
    score.add_argument("--resolutions", required=True)
    score.add_argument("--output", default="scorecard.json")
    agent = subparsers.add_parser("run-agent", help="invoke a JSON-over-stdio forecasting agent")
    agent.add_argument("--questions", required=True)
    agent.add_argument("--command", required=True)
    agent.add_argument("--forecaster", required=True)
    agent.add_argument("--output", default="forecasts.jsonl")
    submission = subparsers.add_parser(
        "prepare-submission", help="run an agent and create a validated, sealed live submission"
    )
    submission.add_argument("--questions", required=True)
    submission.add_argument("--command", required=True)
    submission.add_argument("--forecaster", required=True)
    submission.add_argument("--output-dir", required=True, type=Path)
    verify_live = subparsers.add_parser(
        "verify-live", help="validate every committed live-round submission and seal"
    )
    verify_live.add_argument("--root", default="live/rounds", type=Path)
    website = subparsers.add_parser("build-site", help="build the static public dashboard")
    website.add_argument("--output", default="site", type=Path)
    website.add_argument(
        "--questions", default="live/rounds/2026-08/questions.jsonl"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.action == "demo":
            command_demo(args.output)
        elif args.action == "validate":
            validate_bundle(args.questions, args.forecasts, args.resolutions)
            print("Validation passed")
        elif args.action == "seal":
            manifest = seal_files(args.paths)
            write_json(args.output, manifest)
            print(manifest["combined_sha256"])
        elif args.action == "score":
            result = score_forecasts(read_jsonl(args.forecasts), read_jsonl(args.resolutions))
            write_json(args.output, result)
            Path(args.output).with_suffix(".md").write_text(render_markdown(result), encoding="utf-8")
            print(f"Mean Brier: {result['mean_brier']:.6f}")
        elif args.action == "run-agent":
            forecasts = run_agent(args.command, read_jsonl(args.questions), args.forecaster)
            write_jsonl(args.output, forecasts)
            print(f"Wrote {len(forecasts)} forecasts to {args.output}")
        elif args.action == "prepare-submission":
            args.output_dir.mkdir(parents=True, exist_ok=True)
            forecasts_path = args.output_dir / "forecasts.jsonl"
            now = datetime.now(timezone.utc)
            questions = [
                question
                for question in read_jsonl(args.questions)
                if parse_time(question["close_time"], "close_time") >= now
            ]
            if not questions:
                raise ValueError("no open questions remain in this round")
            forecasts = run_agent(args.command, questions, args.forecaster)
            write_jsonl(forecasts_path, forecasts)
            validate_bundle(args.questions, str(forecasts_path), None)
            manifest = seal_files([args.questions, forecasts_path])
            write_json(args.output_dir / "seal.json", manifest)
            print(f"Validated and sealed {len(forecasts)} forecasts")
            print(f"Submission: {args.output_dir}")
            print(f"Seal: {manifest['combined_sha256']}")
        elif args.action == "verify-live":
            count = verify_live_submissions(args.root)
            print(f"Verified {count} live submission(s)")
        elif args.action == "build-site":
            root = Path(__file__).resolve().parents[1]
            smoke = root / "benchmarks" / "synthetic-smoke"
            result = score_forecasts(
                read_jsonl(smoke / "forecasts.jsonl"),
                read_jsonl(smoke / "resolutions.jsonl"),
            )
            questions_path = Path(args.questions)
            if not questions_path.is_absolute():
                questions_path = root / questions_path
            build_site(
                result,
                read_jsonl(questions_path),
                args.output,
                root / "docs" / "assets" / "open-market-eval-social-preview.png",
            )
            print(f"Site: {args.output / 'index.html'}")
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"error: {exc}")
        return 2
    return 0
