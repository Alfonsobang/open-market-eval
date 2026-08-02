## What changed

## Forecasting or evaluation failure mode addressed

## Validation

- [ ] Tests pass
- [ ] No post-cutoff evidence is introduced
- [ ] Data is public, redistributable, or clearly synthetic
- [ ] No investment recommendation or unsupported performance claim is included

## Live forecast submissions only

- [ ] The submission is under `live/rounds/<round>/submissions/<github-handle>/`
- [ ] `forecasts.jsonl` and `seal.json` were generated before each question closed
- [ ] `python -m open_market_eval verify-live` passes
