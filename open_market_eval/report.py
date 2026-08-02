from __future__ import annotations

from typing import Any


def render_markdown(score: dict[str, Any]) -> str:
    lines = [
        "# OpenMarketEval Scorecard",
        "",
        "> Lower Brier and log loss are better. Positive skill beats the 0.5 baseline.",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Resolved forecasts | {score['n_scored']} |",
        f"| Mean Brier | {score['mean_brier']:.6f} |",
        f"| Mean log loss | {score['mean_log_loss']:.6f} |",
        f"| Brier skill vs 0.5 | {score['brier_skill_vs_0_5']:.6f} |",
        f"| Calibration error | {score['expected_calibration_error']:.6f} |",
        "",
        "## Forecasts",
        "",
        "| Question | Probability | Outcome | Brier |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in score["predictions"]:
        lines.append(
            f"| `{row['question_id']}` | {row['probability']:.3f} | "
            f"{row['outcome']} | {row['brier']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This report evaluates probabilistic research quality. It is not a trading record, "
            "a return backtest, or investment advice.",
            "",
        ]
    )
    return "\n".join(lines)
