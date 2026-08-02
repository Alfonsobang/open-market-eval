# Contributing

OpenMarketEval welcomes small, auditable contributions that improve market-event forecasting research.

## Good first contributions

- Add a question with unambiguous resolution criteria and public sources.
- Add an agent adapter that emits the forecast schema.
- Add a proper scoring rule, calibration diagnostic, or temporal-integrity test.
- Add a Harbor-compatible task without network or private-data dependencies.
- Improve English or Chinese documentation while preserving technical meaning.
- Submit a forecast to an open live round before its question closes.

## Quality bar

Every benchmark contribution must:

1. Use only public, redistributable, or clearly synthetic data.
2. Define the information cutoff, close time, resolution deadline, and objective resolution rule.
3. Keep outcome information unavailable to the forecaster at forecast time.
4. Include deterministic tests and provenance notes.
5. Avoid investment recommendations, return promises, private workflows, and unsupported performance claims.

Run before opening a pull request:

```bash
python -m unittest discover -s tests -v
python -m open_market_eval demo --output runs/demo
```

For a benchmark or scoring change, explain what failure mode it catches and provide a minimal fixture. Maintainers may decline large generated dumps, promotional content, unverifiable forecasts, or datasets with unclear rights.

For a live-round forecast, follow the round README. The GitHub commit must predate the question close time, and the submitted seal must match the forecast file. Late entries cannot receive L2 status.
