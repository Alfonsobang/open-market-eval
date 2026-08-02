# Contributing

OpenMarketEval welcomes small, auditable contributions that improve A-share research-agent evaluation and market-event forecasting.

## Submit an Arena result

Run `python -m open_market_eval audit-demo`, replace the format fixture with your Agent output, and use the **Submit an Agent result** issue template. Include the exact Agent and model version, reproduction command, runtime environment, raw JSONL, and generated scorecard. Do not remove failed cases.

Development-pack results are engineering evidence, not hidden-test rankings. Maintainers will reject screenshot-only scores, undisclosed human editing, incomplete artifacts, or investment-performance framing.

## Propose an A-share task

Use the [A-share task proposal](https://github.com/Alfonsobang/open-market-eval/issues/new?template=a-share-task.yml) for filing search, point-in-time QA, event forecasting, backtest audit, or research-memo tasks. A useful proposal includes:

1. A concrete research question that has one inspectable deliverable.
2. An exact information cutoff, including timezone.
3. Public primary sources that were available before that cutoff.
4. Expected fields or artifacts, plus a deterministic or reviewer-auditable verifier.
5. Known failure modes such as revised filings, unit mistakes, look-ahead leakage, survivorship bias, or unsupported claims.

Do not submit stock tips, target prices, unverifiable screenshots, scraped datasets without clear rights, or tasks whose answer depends on private terminals. The first task pack should remain runnable by an independent researcher using public information.

## Good first contributions

- Add a question with unambiguous resolution criteria and public sources.
- Turn one A-share workflow in [`benchmarks/a-share-lab/tracks.json`](benchmarks/a-share-lab/tracks.json) into a minimal public fixture.
- Add an official disclosure source or document a point-in-time data caveat in [`sources.json`](benchmarks/a-share-lab/sources.json).
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
python -m open_market_eval list-tracks
```

For a benchmark or scoring change, explain what failure mode it catches and provide a minimal fixture. Maintainers may decline large generated dumps, promotional content, unverifiable forecasts, or datasets with unclear rights.

For a live-round forecast, follow the round README. The GitHub commit must predate the question close time, and the submitted seal must match the forecast file. Late entries cannot receive L2 status.

Store live entries at `live/rounds/<round>/submissions/<github-handle>/`. Do not edit another participant's files. The `prepare-submission` command creates the required files, and `python -m open_market_eval verify-live` runs the same integrity check as CI.
