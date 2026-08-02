# Agent Adapter Contract

OpenMarketEval keeps model integration deliberately small. For each question, the harness starts your command, writes one JSON object to stdin, and reads one JSON object from stdout.

## Required output

```json
{"probability": 0.62}
```

`probability` must be between 0 and 1. The harness adds the forecaster name and current UTC timestamps when they are omitted.

## Recommended output

```json
{
  "probability": 0.62,
  "thesis": "One concise, falsifiable reason for the estimate.",
  "evidence": [
    {"url": "https://example.com/public-source", "published_at": "2026-08-01T12:00:00Z"}
  ],
  "falsifiers": ["Evidence that would materially lower the probability"]
}
```

Evidence must be public and published no later than `evidence_cutoff`. Write logs to stderr; stdout must contain only the JSON answer.

## Minimal Python adapter

```python
import json
import sys

question = json.load(sys.stdin)

# Replace this fixed probability with your model or research workflow.
answer = {
    "probability": 0.5,
    "thesis": f"Uninformative protocol check for {question['id']}.",
    "evidence": [],
    "falsifiers": ["Any decision-relevant public evidence"],
}
json.dump(answer, sys.stdout)
```

Use `run-agent` for local experiments and `prepare-submission` for a live round. The latter runs only open questions, validates the forecast rows, and seals the question and forecast ledgers.
