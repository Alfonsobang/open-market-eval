# Benchmark Design

A useful financial forecasting benchmark must test more than final accuracy.

| Layer | Question | Failure caught |
| --- | --- | --- |
| Temporal integrity | Was every input available before cutoff? | Hindsight leakage |
| Retrieval | Did the agent find primary, relevant evidence? | Search noise |
| Judgment | Did probability reflect evidence and base rates? | Overconfidence |
| Resolution | Is the outcome rule objective and reproducible? | Label ambiguity |
| Calibration | Do 70% calls happen about 70% of the time? | Confidence inflation |
| Baseline | Does the agent beat 0.5 or a stronger reference? | Impressive-looking but weak scores |
| Replication | Does performance survive repeated questions and trials? | Small-sample luck |

Leaderboard entries should expose sample size, unresolved-question handling, exclusions, confidence intervals, and evidence-access conditions. A single accuracy number is insufficient.
