# A-Share Agent Lab

The A-Share Agent Lab is a public experiment for evaluating AI-assisted China A-share research workflows. It is designed for two groups: developing A-share researchers who need a disciplined research process, and AI-investing enthusiasts who want to test agents without mistaking fluent output or a single backtest for evidence.

## Tracks

1. **Filing search:** retrieve direct, pre-cutoff evidence from official disclosures.
2. **Point-in-time fact QA:** extract the correct value, period, unit, entity scope, and report version.
3. **Event forecasting:** seal probabilistic forecasts before objectively resolvable events.
4. **Backtest audit:** detect look-ahead, survivorship, execution, universe, and cost errors.
5. **Research memo:** connect claims, evidence, counterevidence, unknowns, and falsifiers.

Run `python -m open_market_eval list-tracks` to inspect the machine-readable specifications in [`tracks.json`](tracks.json). Public-source policy and provenance notes are in [`sources.json`](sources.json).

## Design rules

- Public data only; no private research corpus, user data, or proprietary workflow.
- Every task declares an information cutoff and deterministic or independently reviewable output.
- Official filings and exchange sources take priority over aggregators.
- Backtests must model historical universe membership, T+1, suspensions, price limits, corporate actions, and transaction costs.
- Results evaluate research processes and are not investment recommendations.

The first release is a specification and pilot task catalog. It does not claim complete dataset coverage or model performance.
