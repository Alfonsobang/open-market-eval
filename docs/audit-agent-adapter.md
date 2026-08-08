# Backtest Audit Agent Adapter

OpenMarketEval can run any language or model stack through a small JSON-over-stdio contract. The harness starts the command once per case, writes one case object to stdin, and expects one answer object on stdout.

Do not place API keys or other secrets directly in `--command`: the exact command is written to `run.json` for reproducibility. Pass credentials through your local environment and never commit them.

## Required output

```json
{"findings":[{"code":"same_close_execution","severity":"critical","evidence":"The signal is formed after the claimed fill."}]}
```

Return `{"findings":[]}` when the case does not contain a supported defect. Each finding must use one of the issue codes documented in the [challenge pack](../benchmarks/a-share-backtest-forensics/README.md). Write diagnostic logs to stderr; stdout must contain only the JSON answer.

## Minimal Python adapter

```python
import json
import sys

case = json.load(sys.stdin)

# Replace this empty protocol baseline with your Agent call.
answer = {"findings": []}
json.dump(answer, sys.stdout)
```

## Run and score

```bash
python -m open_market_eval run-audit-agent \
  --command "python path/to/your_auditor.py" \
  --agent-name my-agent \
  --output-dir runs/my-agent
```

The output directory contains:

- `audit_report.jsonl`: raw normalized Agent findings.
- `run.json`: Agent name, exact command, benchmark identifier, and claim boundary.
- `scorecard.json`: machine-readable precision, recall, F1, exact-case accuracy, misses, and false positives.
- `scorecard.md`: review-ready report.

This is a public development pack with visible labels. Its score is suitable for adapter development and regression testing, not hidden-test model ranking or investment-performance claims.
