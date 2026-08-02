# Forecast Protocol

OpenMarketEval treats a forecast as an immutable research artifact, not a mutable opinion.

## Lifecycle

1. **Author the question.** Define a binary event, close time, resolution deadline, objective criteria, and preferred public sources.
2. **Freeze information.** Record an evidence cutoff and reject evidence published later.
3. **Forecast.** Emit a probability, concise thesis, evidence list, and falsifiers.
4. **Seal.** Hash question and forecast ledgers. Commit the seal before the outcome is known.
5. **Resolve.** Record the binary outcome with a public source and rationale.
6. **Score.** Compute Brier score, log loss, skill versus an uninformative baseline, and calibration error.
7. **Review.** Analyze misses by research, timing, base-rate, or judgment failure.

## Why this is harder than a backtest

A return backtest mixes forecasting, sizing, timing, execution, and risk. OpenMarketEval isolates the earlier question: did the research process assign useful probabilities using only information available at the time?

## Integrity levels

- **L0 / smoke:** synthetic events verify software behavior.
- **L1 / pastcast:** historical events with a frozen evidence bundle; useful but potentially exposed to model pretraining.
- **L2 / live sealed:** forecasts committed before close and resolved later.
- **L3 / replicated:** independently timestamped forecasts, resolution review, and repeated samples.

Only L2 and L3 support claims about live forecasting performance.
