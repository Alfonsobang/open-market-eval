from __future__ import annotations

import math
from collections import defaultdict
from typing import Any


def brier_score(probability: float, outcome: int) -> float:
    return (float(probability) - outcome) ** 2


def log_loss(probability: float, outcome: int) -> float:
    p = min(max(float(probability), 1e-15), 1 - 1e-15)
    return -(outcome * math.log(p) + (1 - outcome) * math.log(1 - p))


def score_forecasts(
    forecasts: list[dict[str, Any]], resolutions: list[dict[str, Any]]
) -> dict[str, Any]:
    outcomes = {row["question_id"]: row["outcome"] for row in resolutions}
    scored = []
    for forecast in forecasts:
        question_id = forecast["question_id"]
        if question_id not in outcomes:
            continue
        outcome = outcomes[question_id]
        p = float(forecast["probability"])
        scored.append(
            {
                "question_id": question_id,
                "forecaster": forecast["forecaster"],
                "probability": p,
                "outcome": outcome,
                "brier": brier_score(p, outcome),
                "log_loss": log_loss(p, outcome),
            }
        )
    if not scored:
        raise ValueError("no forecasts have matching resolutions")

    mean_brier = sum(row["brier"] for row in scored) / len(scored)
    mean_log_loss = sum(row["log_loss"] for row in scored) / len(scored)
    baseline_brier = sum(brier_score(0.5, row["outcome"]) for row in scored) / len(scored)
    bins: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in scored:
        bins[min(int(row["probability"] * 10), 9)].append(row)
    calibration = []
    ece = 0.0
    for index in sorted(bins):
        bucket = bins[index]
        confidence = sum(row["probability"] for row in bucket) / len(bucket)
        frequency = sum(row["outcome"] for row in bucket) / len(bucket)
        weight = len(bucket) / len(scored)
        ece += weight * abs(confidence - frequency)
        calibration.append(
            {
                "bin": f"{index / 10:.1f}-{(index + 1) / 10:.1f}",
                "count": len(bucket),
                "mean_probability": round(confidence, 6),
                "observed_frequency": round(frequency, 6),
            }
        )
    return {
        "n_scored": len(scored),
        "mean_brier": round(mean_brier, 6),
        "mean_log_loss": round(mean_log_loss, 6),
        "baseline_brier_0_5": round(baseline_brier, 6),
        "brier_skill_vs_0_5": round(1 - mean_brier / baseline_brier, 6),
        "expected_calibration_error": round(ece, 6),
        "calibration": calibration,
        "predictions": scored,
    }
