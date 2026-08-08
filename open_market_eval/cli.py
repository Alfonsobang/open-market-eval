from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from .audit import render_audit_markdown, score_audit_submission
from .harness import run_agent, run_audit_agent
from .io import read_jsonl, write_json, write_jsonl
from .ledger import seal_files, verify_seal
from .preflight import audit_backtest_contract, render_preflight_markdown
from .report import render_markdown
from .retrieval import audit_research_packet, render_research_audit_markdown
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


def load_a_share_tracks(root: Path | None = None) -> list[dict]:
    project_root = root or Path(__file__).resolve().parents[1]
    path = project_root / "benchmarks" / "a-share-lab" / "tracks.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list) or not value:
        raise ValueError("A-share track catalog must be a non-empty list")
    return value


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
    print("Validated 6 time-safe forecasts")
    print(f"Seal: {manifest['combined_sha256'][:16]}...")
    print(f"Mean Brier: {score['mean_brier']:.4f}")
    print(f"Skill vs 0.5: {score['brier_skill_vs_0_5']:.1%}")
    print(f"Report: {output / 'scorecard.md'}")


def command_audit_demo(output: Path) -> None:
    root = Path(__file__).resolve().parents[1] / "benchmarks" / "a-share-backtest-forensics"
    output.mkdir(parents=True, exist_ok=True)
    submission_path = output / "audit_report.jsonl"
    shutil.copyfile(root / "example-submission.jsonl", submission_path)
    score = score_audit_submission(
        read_jsonl(submission_path), read_jsonl(root / "labels.jsonl")
    )
    write_json(output / "scorecard.json", score)
    (output / "scorecard.md").write_text(render_audit_markdown(score), encoding="utf-8")
    print(f"Scored {score['case_count']} A-share backtest audit cases")
    print(f"Precision: {score['precision']:.1%}")
    print(f"Recall: {score['recall']:.1%}")
    print(f"F1: {score['f1']:.1%}")
    print(f"Report: {output / 'scorecard.md'}")


def command_doctor(root: Path, output: Path | None = None) -> None:
    """Run the repository's public integrity paths without network access."""
    if sys.version_info < (3, 10):
        raise RuntimeError("Python 3.10 or newer is required")
    root = root.resolve()
    checks: list[dict[str, str]] = []

    smoke = root / "benchmarks" / "synthetic-smoke"
    questions = smoke / "questions.jsonl"
    forecasts = smoke / "forecasts.jsonl"
    resolutions = smoke / "resolutions.jsonl"
    validate_bundle(str(questions), str(forecasts), str(resolutions))
    question_count = len(read_jsonl(questions))
    checks.append(
        {
            "id": "forecast-loop",
            "detail": f"{question_count} synthetic forecasts validated",
        }
    )

    contract = json.loads(
        (root / "examples" / "backtests" / "conservative-a-share-contract.json").read_text(
            encoding="utf-8"
        )
    )
    preflight = audit_backtest_contract(contract)
    if not preflight["passed"]:
        raise ValueError("conservative backtest control did not pass")
    checks.append(
        {
            "id": "backtest-preflight",
            "detail": f"{preflight['checks_run']} checks passed",
        }
    )

    packet = json.loads(
        (root / "examples" / "research-packets" / "conservative-packet.json").read_text(
            encoding="utf-8"
        )
    )
    evidence = audit_research_packet(packet)
    if not evidence["passed"]:
        raise ValueError("conservative research-packet control did not pass")
    checks.append(
        {
            "id": "evidence-audit",
            "detail": f"{evidence['checks_run']} checks passed",
        }
    )

    harbor_root = root / "integrations" / "harbor"
    task_names = (
        "a-share-backtest-audit",
        "a-share-research-evidence",
        "market-forecast",
    )
    for task_name in task_names:
        task_root = harbor_root / task_name
        required = (
            task_root / "task.toml",
            task_root / "instruction.md",
            task_root / "environment" / "Dockerfile",
            task_root / "solution" / "solve.sh",
            task_root / "tests" / "test.sh",
        )
        if not all(path.is_file() for path in required):
            raise ValueError(f"incomplete Harbor task: {task_name}")
        config = (task_root / "task.toml").read_text(encoding="utf-8")
        if (
            'schema_version = "1.3"' not in config
            or 'network_mode = "no-network"' not in config
        ):
            raise ValueError(f"non-portable Harbor task configuration: {task_name}")
    checks.append(
        {
            "id": "harbor-tasks",
            "detail": f"{len(task_names)} portable no-network tasks found",
        }
    )

    round_root = root / "live" / "rounds" / "2026-08"
    live_questions = round_root / "questions.jsonl"
    baseline = round_root / "baselines" / "uninformative-0-5.jsonl"
    validate_bundle(str(live_questions), str(baseline), None)
    verify_seal(
        json.loads((round_root / "seal.json").read_text(encoding="utf-8")),
        [live_questions, baseline],
    )
    checks.append(
        {
            "id": "live-round-seal",
            "detail": "question slate and baseline seal verified",
        }
    )

    report = {
        "status": "ready",
        "checks": checks,
        "claim_boundary": "Repository integrity only; not investment performance or advice.",
    }
    if output is not None:
        write_json(output, report)
    for check in checks:
        print(f"[PASS] {check['id']}: {check['detail']}")
    print(f"Ready: {len(checks)}/{len(checks)} integrity paths passed")
    if output is not None:
        print(f"Report: {output}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="open-market-eval")
    subparsers = parser.add_subparsers(dest="action", required=True)
    demo = subparsers.add_parser("demo", help="run the sealed synthetic forecasting loop")
    demo.add_argument("--output", default="runs/demo", type=Path)
    audit_demo = subparsers.add_parser(
        "audit-demo", help="run the A-share backtest forensics development pack"
    )
    audit_demo.add_argument("--output", default="runs/audit-demo", type=Path)
    doctor = subparsers.add_parser(
        "doctor", help="verify every bundled evaluation path without network access"
    )
    doctor.add_argument("--root", default=Path(__file__).resolve().parents[1], type=Path)
    doctor.add_argument("--output", type=Path)
    audit_score = subparsers.add_parser(
        "score-audit", help="score an A-share backtest audit submission"
    )
    audit_score.add_argument("--submission", required=True)
    audit_score.add_argument(
        "--labels", default="benchmarks/a-share-backtest-forensics/labels.jsonl"
    )
    audit_score.add_argument("--output", default="runs/audit-scorecard.json")
    audit_agent = subparsers.add_parser(
        "run-audit-agent",
        help="run and score any JSON-over-stdio agent on Backtest Forensics",
    )
    audit_agent.add_argument(
        "--cases", default="benchmarks/a-share-backtest-forensics/cases.jsonl"
    )
    audit_agent.add_argument(
        "--labels", default="benchmarks/a-share-backtest-forensics/labels.jsonl"
    )
    audit_agent.add_argument("--command", required=True)
    audit_agent.add_argument("--agent-name", required=True)
    audit_agent.add_argument("--output-dir", default="runs/audit-agent", type=Path)
    preflight = subparsers.add_parser(
        "audit-spec", help="audit an A-share backtest contract before interpreting returns"
    )
    preflight.add_argument("--spec", required=True)
    preflight.add_argument("--output", default="runs/backtest-preflight.json")
    preflight.add_argument(
        "--strict", action="store_true", help="exit non-zero when findings are present"
    )
    research_audit = subparsers.add_parser(
        "audit-research-packet",
        help="audit a financial-search evidence packet for cutoff and citation integrity",
    )
    research_audit.add_argument("--packet", required=True)
    research_audit.add_argument("--output", default="runs/research-packet-audit.json")
    research_audit.add_argument(
        "--strict", action="store_true", help="exit non-zero when findings are present"
    )
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
    subparsers.add_parser("list-tracks", help="list A-share Agent Lab evaluation tracks")
    track = subparsers.add_parser("show-track", help="print one A-share track specification")
    track.add_argument("--track", required=True)
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
        elif args.action == "audit-demo":
            command_audit_demo(args.output)
        elif args.action == "doctor":
            command_doctor(args.root, args.output)
        elif args.action == "score-audit":
            result = score_audit_submission(
                read_jsonl(args.submission), read_jsonl(args.labels)
            )
            write_json(args.output, result)
            Path(args.output).with_suffix(".md").write_text(
                render_audit_markdown(result), encoding="utf-8"
            )
            print(f"Precision: {result['precision']:.1%}")
            print(f"Recall: {result['recall']:.1%}")
            print(f"F1: {result['f1']:.1%}")
        elif args.action == "run-audit-agent":
            args.output_dir.mkdir(parents=True, exist_ok=True)
            submission = run_audit_agent(args.command, read_jsonl(args.cases))
            submission_path = args.output_dir / "audit_report.jsonl"
            write_jsonl(submission_path, submission)
            result = score_audit_submission(submission, read_jsonl(args.labels))
            write_json(args.output_dir / "scorecard.json", result)
            (args.output_dir / "scorecard.md").write_text(
                render_audit_markdown(result), encoding="utf-8"
            )
            write_json(
                args.output_dir / "run.json",
                {
                    "agent_name": args.agent_name,
                    "command": args.command,
                    "case_count": len(submission),
                    "benchmark": result["benchmark"],
                    "claim_boundary": result["claim_boundary"],
                },
            )
            print(f"Scored {len(submission)} cases for {args.agent_name}")
            print(f"Precision: {result['precision']:.1%}")
            print(f"Recall: {result['recall']:.1%}")
            print(f"F1: {result['f1']:.1%}")
            print(f"Artifacts: {args.output_dir}")
        elif args.action == "audit-spec":
            contract = json.loads(Path(args.spec).read_text(encoding="utf-8"))
            result = audit_backtest_contract(contract)
            write_json(args.output, result)
            Path(args.output).with_suffix(".md").write_text(
                render_preflight_markdown(result), encoding="utf-8"
            )
            print(f"Checks: {result['checks_run']}")
            print(f"Findings: {result['finding_count']}")
            print(f"Critical: {result['critical_count']}")
            print(f"Report: {Path(args.output).with_suffix('.md')}")
            if args.strict and not result["passed"]:
                return 1
        elif args.action == "audit-research-packet":
            packet = json.loads(Path(args.packet).read_text(encoding="utf-8"))
            result = audit_research_packet(packet)
            write_json(args.output, result)
            Path(args.output).with_suffix(".md").write_text(
                render_research_audit_markdown(result), encoding="utf-8"
            )
            print(f"Checks: {result['checks_run']}")
            print(f"Findings: {result['finding_count']}")
            print(f"Critical: {result['critical_count']}")
            print(f"Report: {Path(args.output).with_suffix('.md')}")
            if args.strict and not result["passed"]:
                return 1
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
        elif args.action == "list-tracks":
            for track in load_a_share_tracks():
                print(f"{track['id']:<20} {track['status']:<8} {track['name_zh']} / {track['name_en']}")
        elif args.action == "show-track":
            tracks = {track["id"]: track for track in load_a_share_tracks()}
            if args.track not in tracks:
                raise ValueError(f"unknown A-share track: {args.track}")
            print(json.dumps(tracks[args.track], ensure_ascii=False, indent=2, sort_keys=True))
        elif args.action == "build-site":
            root = Path(__file__).resolve().parents[1]
            audit_root = root / "benchmarks" / "a-share-backtest-forensics"
            result = score_audit_submission(
                read_jsonl(audit_root / "example-submission.jsonl"),
                read_jsonl(audit_root / "labels.jsonl"),
            )
            questions_path = Path(args.questions)
            if not questions_path.is_absolute():
                questions_path = root / questions_path
            build_site(
                result,
                read_jsonl(questions_path),
                load_a_share_tracks(root),
                json.loads((root / "benchmarks" / "a-share-lab" / "sources.json").read_text(encoding="utf-8")),
                read_jsonl(audit_root / "cases.jsonl"),
                args.output,
                root / "docs" / "assets" / "a-share-arena-forensics.png",
            )
            print(f"Site: {args.output / 'index.html'}")
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"error: {exc}")
        return 2
    return 0
