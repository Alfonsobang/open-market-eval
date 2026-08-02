# Live Round 2026-08

This round contains six binary macro and monetary-policy questions that close between August 7 and September 16, 2026. Outcomes will be resolved from primary public releases by BLS, BEA, the ECB, and the Federal Reserve.

## Integrity status

- **Level:** L2 live sealed
- **Question slate authored:** 2026-08-02
- **Baseline:** an explicitly uninformative 0.5 forecast for every question
- **Baseline evidence:** none; it intentionally ignores event-specific information
- **Seal:** [`seal.json`](seal.json)

The baseline exists to verify submission, sealing, and later scoring. It is not presented as analysis or forecasting skill.

## Submit a forecast

1. Implement the small [JSON-over-stdio adapter](../../../docs/agent-adapter.md).
2. Use only evidence published no later than your `evidence_cutoff`.
3. Generate a validated and sealed submission before the relevant question closes:

```bash
python -m open_market_eval prepare-submission \
  --questions live/rounds/2026-08/questions.jsonl \
  --command "python path/to/your_agent.py" \
  --forecaster your-agent-name \
  --output-dir live/rounds/2026-08/submissions/your-github-handle
```

4. Open a pull request containing the generated `forecasts.jsonl` and `seal.json`. CI verifies both files. The commit must reach GitHub before the question's `close_time`.

Late forecasts may be retained for software testing but will not be labeled L2 or included in the live leaderboard.

## Resolution policy

The initial value in the named official release controls unless the question says otherwise. Corrections published before `resolve_by` may be considered only when the original release is formally withdrawn. Each resolution will include the source URL, outcome, timestamp, and rationale in a pull request.

This round evaluates probabilistic research quality. It does not provide investment recommendations, security selection, position sizing, or trade execution.
