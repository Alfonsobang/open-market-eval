---
name: forecast-market-events
description: Create auditable probabilistic forecasts for stock-market, macroeconomic, regulatory, geopolitical, earnings, and supply-chain events. Use when researching a future market-relevant event, preparing an OpenMarketEval submission, testing an AI forecasting agent, or reviewing whether a forecast is time-safe, evidence-grounded, calibrated, and objectively resolvable.
---

# Forecast Market Events

Produce a probability that can be sealed now and scored later. Do not produce a trade recommendation, position size, price target, or guaranteed-return claim.

## Workflow

1. Rewrite the claim as a binary question with a specific close time and resolution deadline.
2. Define objective YES/NO criteria before researching. Prefer primary public resolution sources.
3. Set `evidence_cutoff` to the latest information the forecast may use.
4. Research base rates, current evidence, incentives, counterevidence, and plausible surprise paths.
5. Emit one probability from 0 to 1, a concise thesis, timestamped evidence links, and at least one falsifier.
6. Validate with `python -m open_market_eval validate`.
7. Seal the question and forecast ledgers with `python -m open_market_eval seal` before the event closes.
8. After resolution, record the outcome and run `python -m open_market_eval score`.

## Forecast contract

Return these fields:

```json
{
  "question_id": "stable-id",
  "forecaster": "agent-or-method",
  "probability": 0.63,
  "created_at": "2026-08-02T08:00:00Z",
  "evidence_cutoff": "2026-08-02T08:00:00Z",
  "thesis": "Why this probability is above or below the base rate.",
  "evidence": [{"url": "https://...", "published_at": "2026-08-01T10:00:00Z"}],
  "falsifiers": ["What would materially lower or raise the probability"]
}
```

Never use evidence published after the cutoff. State uncertainty instead of converting weak evidence into false precision. Keep forecasting quality separate from investment suitability.
