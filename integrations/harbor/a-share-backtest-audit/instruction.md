# A-share backtest forensics

Read `fixtures/case.json` and write `/logs/artifacts/audit_report.json`.

The report must contain `case_id` and a `findings` array. Each finding must contain one allowed `code`, a severity of `critical`, `high`, `medium`, or `low`, and a concrete evidence sentence grounded in the fixture.

Allowed codes:

- `same_close_execution`
- `current_universe_projection`
- `adjusted_price_execution`
- `t_plus_one_violation`
- `tradability_constraints_ignored`
- `transaction_costs_omitted`
- `revision_leakage`
- `delisting_survivorship`

Report only defects supported by the case. False positives are failures.
