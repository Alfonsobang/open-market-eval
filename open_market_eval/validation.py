from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


QUESTION_FIELDS = {
    "id",
    "title",
    "close_time",
    "resolve_by",
    "resolution_criteria",
    "resolution_sources",
    "tags",
}
FORECAST_FIELDS = {
    "question_id",
    "forecaster",
    "probability",
    "created_at",
    "evidence_cutoff",
    "thesis",
    "evidence",
    "falsifiers",
}
RESOLUTION_FIELDS = {
    "question_id",
    "outcome",
    "resolved_at",
    "source_url",
    "rationale",
}


def parse_time(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be an ISO-8601 string")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"{field} must be valid ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _require(row: dict[str, Any], fields: set[str], kind: str) -> None:
    missing = fields - row.keys()
    if missing:
        raise ValueError(f"{kind} is missing: {', '.join(sorted(missing))}")


def validate_question(row: dict[str, Any]) -> None:
    _require(row, QUESTION_FIELDS, "question")
    if not isinstance(row["id"], str) or not row["id"].strip():
        raise ValueError("question id must be a non-empty string")
    close = parse_time(row["close_time"], "close_time")
    resolve_by = parse_time(row["resolve_by"], "resolve_by")
    if resolve_by <= close:
        raise ValueError("resolve_by must be after close_time")
    if not isinstance(row["resolution_sources"], list) or not row["resolution_sources"]:
        raise ValueError("resolution_sources must be a non-empty list")


def validate_forecast(row: dict[str, Any], question: dict[str, Any]) -> None:
    _require(row, FORECAST_FIELDS, "forecast")
    probability = row["probability"]
    if isinstance(probability, bool) or not isinstance(probability, (int, float)):
        raise ValueError("probability must be numeric")
    if not 0.0 <= float(probability) <= 1.0:
        raise ValueError("probability must be between 0 and 1")
    created = parse_time(row["created_at"], "created_at")
    cutoff = parse_time(row["evidence_cutoff"], "evidence_cutoff")
    close = parse_time(question["close_time"], "close_time")
    if row["question_id"] != question["id"]:
        raise ValueError("forecast question_id does not match question")
    if cutoff > created:
        raise ValueError("evidence_cutoff cannot be after created_at")
    if created > close:
        raise ValueError("forecast was created after close_time")
    if not isinstance(row["evidence"], list):
        raise ValueError("evidence must be a list")
    for item in row["evidence"]:
        if not isinstance(item, dict) or "url" not in item or "published_at" not in item:
            raise ValueError("each evidence item needs url and published_at")
        if parse_time(item["published_at"], "evidence.published_at") > cutoff:
            raise ValueError("evidence published after evidence_cutoff")


def validate_resolution(row: dict[str, Any], question: dict[str, Any]) -> None:
    _require(row, RESOLUTION_FIELDS, "resolution")
    if row["question_id"] != question["id"]:
        raise ValueError("resolution question_id does not match question")
    if row["outcome"] not in (0, 1):
        raise ValueError("binary outcome must be 0 or 1")
    resolved = parse_time(row["resolved_at"], "resolved_at")
    if resolved <= parse_time(question["close_time"], "close_time"):
        raise ValueError("resolved_at must be after close_time")
