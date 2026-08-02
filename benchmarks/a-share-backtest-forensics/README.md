# A-Share Backtest Forensics

> Can your agent detect when an A-share backtest is quietly using the future?

This development pack contains 10 synthetic but market-structure-specific audit cases. It tests eight failure classes without redistributing market data or making investment claims.

## Run the reference-format submission

```bash
python -m open_market_eval audit-demo
```

Score your own Agent output:

```bash
python -m open_market_eval score-audit \
  --submission path/to/audit_report.jsonl \
  --output runs/my-agent/audit-scorecard.json
```

## Submission contract

One JSON object per case:

```json
{"case_id":"bt-001","findings":[{"code":"same_close_execution","severity":"critical","evidence":"The signal is formed after the claimed fill."}]}
```

Allowed issue codes:

- `same_close_execution`
- `current_universe_projection`
- `adjusted_price_execution`
- `t_plus_one_violation`
- `tradability_constraints_ignored`
- `transaction_costs_omitted`
- `revision_leakage`
- `delisting_survivorship`

The scorer reports micro precision, recall, F1, and exact case accuracy. Clean control cases penalize agents that invent findings.

## Integrity level

This is a **public development pack**: cases and labels are visible, so its score is useful for engineering and regression tests, not for model-ranking claims. A future Arena round will publish cases before labels and seal submissions before resolution.
