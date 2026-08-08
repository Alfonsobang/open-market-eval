from __future__ import annotations

import json
import shlex
import subprocess
from datetime import datetime, timezone
from typing import Any


def run_agent(command: str, questions: list[dict[str, Any]], forecaster: str) -> list[dict[str, Any]]:
    forecasts = []
    for question in questions:
        completed = subprocess.run(
            shlex.split(command),
            input=json.dumps(question),
            text=True,
            capture_output=True,
            check=False,
            timeout=120,
        )
        if completed.returncode:
            raise RuntimeError(
                f"agent failed for {question['id']}: {completed.stderr.strip()}"
            )
        try:
            answer = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"agent returned invalid JSON for {question['id']}") from exc
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        forecasts.append(
            {
                "question_id": question["id"],
                "forecaster": forecaster,
                "probability": answer["probability"],
                "created_at": answer.get("created_at", now),
                "evidence_cutoff": answer.get("evidence_cutoff", now),
                "thesis": answer.get("thesis", ""),
                "evidence": answer.get("evidence", []),
                "falsifiers": answer.get("falsifiers", []),
            }
        )
    return forecasts


def run_audit_agent(command: str, cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Run one backtest-audit case per process using the JSON-over-stdio contract."""
    submissions = []
    for case in cases:
        completed = subprocess.run(
            shlex.split(command),
            input=json.dumps(case, ensure_ascii=False),
            text=True,
            capture_output=True,
            check=False,
            timeout=120,
        )
        if completed.returncode:
            raise RuntimeError(
                f"audit agent failed for {case['id']}: {completed.stderr.strip()}"
            )
        try:
            answer = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"audit agent returned invalid JSON for {case['id']}"
            ) from exc
        findings = answer.get("findings") if isinstance(answer, dict) else None
        if not isinstance(findings, list):
            raise RuntimeError(
                f"audit agent response for {case['id']} must contain a findings list"
            )
        submissions.append({"case_id": case["id"], "findings": findings})
    return submissions
