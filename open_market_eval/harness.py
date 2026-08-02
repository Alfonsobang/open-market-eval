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
