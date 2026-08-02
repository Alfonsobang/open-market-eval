"""Minimal JSON-over-stdio adapter used to test the harness."""

import json
import sys
from datetime import datetime, timedelta, timezone


question = json.load(sys.stdin)
close_time = datetime.fromisoformat(question["close_time"].replace("Z", "+00:00"))
forecast_time = min(datetime.now(timezone.utc), close_time - timedelta(days=1))
forecast_time = forecast_time.isoformat().replace("+00:00", "Z")
json.dump(
    {
        "probability": 0.5,
        "created_at": forecast_time,
        "evidence_cutoff": forecast_time,
        "thesis": f"Uninformative baseline for {question['id']}.",
        "evidence": [],
        "falsifiers": ["Any decision-relevant public evidence"],
    },
    sys.stdout,
)
