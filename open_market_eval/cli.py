from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from .harness import run_agent
from .io import read_jsonl, write_json, write_jsonl
from .ledger import seal_files
from .report import render_markdown
from .scoring import score_forecasts
from .site import build_site
from .validation import validate_forecast, validate_question, validate_resolution


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
