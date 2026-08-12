from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.parse import urlsplit


SCORED_FIELDS = (
    "value",
    "unit",
    "normalized_value_yuan",
    "period",
    "scope",
    "pdf_page",
    "source_id",
)
NUMERIC_FIELDS = {"value", "normalized_value_yuan"}
UNITS = {"CNY_THOUSAND": Decimal(1000), "CNY_YUAN": Decimal(1)}
HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _index(rows: list[dict[str, Any]], name: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError(f"{name} rows must be objects")
        task_id = _required_text(row.get("task_id"), f"{name} task_id")
        if task_id in indexed:
            raise ValueError(f"duplicate {name} task_id: {task_id}")
        indexed[task_id] = row
    return indexed


def _decimal(value: Any) -> Decimal | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = Decimal(value.replace(",", "").strip())
    except InvalidOperation:
        return None
    return parsed if parsed.is_finite() else None


def _field_matches(field: str, predicted: Any, expected: Any) -> bool:
    if field in NUMERIC_FIELDS:
        predicted_number = _decimal(predicted)
        expected_number = _decimal(expected)
        return predicted_number is not None and predicted_number == expected_number
    if field == "pdf_page":
        return (
            isinstance(predicted, int)
            and not isinstance(predicted, bool)
            and predicted == expected
        )
    return isinstance(predicted, str) and predicted == expected


def _validate_label(task_id: str, row: dict[str, Any]) -> None:
    value = _decimal(row.get("value"))
    normalized = _decimal(row.get("normalized_value_yuan"))
    if value is None or normalized is None:
        raise ValueError(f"fact QA label {task_id} has an invalid numeric value")
    unit = row.get("unit")
    if unit not in UNITS:
        raise ValueError(f"fact QA label {task_id} has an unknown unit")
    if normalized != value * UNITS[unit]:
        raise ValueError(
            f"fact QA label {task_id} has an inconsistent normalized value"
        )
    for field in ("period", "scope", "source_id"):
        _required_text(row.get(field), f"fact QA label {task_id} {field}")
    page = row.get("pdf_page")
    if not isinstance(page, int) or isinstance(page, bool) or page < 1:
        raise ValueError(f"fact QA label {task_id} has an invalid pdf_page")


def score_fact_qa_submission(
    submissions: list[dict[str, Any]], labels: list[dict[str, Any]]
) -> dict[str, Any]:
    predicted = _index(submissions, "fact QA submission")
    truth = _index(labels, "fact QA label")
    for task_id, row in truth.items():
        _validate_label(task_id, row)

    missing = sorted(set(truth) - set(predicted))
    unknown = sorted(set(predicted) - set(truth))
    if missing:
        raise ValueError(f"fact QA submission is missing tasks: {', '.join(missing)}")
    if unknown:
        raise ValueError(
            f"fact QA submission contains unknown tasks: {', '.join(unknown)}"
        )

    field_correct = {field: 0 for field in SCORED_FIELDS}
    exact_matches = 0
    cases = []
    for task_id, expected in truth.items():
        submitted = predicted[task_id]
        matches = {
            field: _field_matches(field, submitted.get(field), expected[field])
            for field in SCORED_FIELDS
        }
        exact = all(matches.values())
        exact_matches += exact
        for field, matched in matches.items():
            field_correct[field] += matched
        cases.append(
            {
                "task_id": task_id,
                "exact_match": exact,
                "field_matches": matches,
                "incorrect_fields": [
                    field for field in SCORED_FIELDS if not matches[field]
                ],
            }
        )

    task_count = len(truth)
    total_fields = task_count * len(SCORED_FIELDS)
    return {
        "benchmark": "a-share-point-in-time-qa-dev-v0.1",
        "task_count": task_count,
        "source_count": len({row["source_id"] for row in truth.values()}),
        "scored_fields": list(SCORED_FIELDS),
        "exact_task_accuracy": exact_matches / task_count if task_count else 0.0,
        "mean_field_accuracy": (
            sum(field_correct.values()) / total_fields if total_fields else 0.0
        ),
        "field_accuracy": {
            field: count / task_count if task_count else 0.0
            for field, count in field_correct.items()
        },
        "cases": cases,
        "claim_boundary": (
            "Public development-pack score only; labels are visible. "
            "This is not investment performance or a hidden-test result."
        ),
    }


def validate_fact_qa_pack(
    tasks: list[dict[str, Any]],
    labels: list[dict[str, Any]],
    manifest: dict[str, Any],
) -> dict[str, int]:
    task_index = _index(tasks, "fact QA task")
    label_index = _index(labels, "fact QA label")
    if not task_index:
        raise ValueError("fact QA pack must contain tasks")
    if set(task_index) != set(label_index):
        raise ValueError("fact QA task and label identifiers do not match")

    sources = manifest.get("sources") if isinstance(manifest, dict) else None
    if not isinstance(sources, list) or not sources:
        raise ValueError("fact QA source manifest must contain sources")
    rights = manifest.get("rights")
    if not isinstance(rights, dict) or rights.get("pdfs_redistributed") is not False:
        raise ValueError("fact QA source manifest must declare link-only PDF handling")

    source_index: dict[str, dict[str, Any]] = {}
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("fact QA sources must be objects")
        source_id = _required_text(source.get("id"), "fact QA source id")
        if source_id in source_index:
            raise ValueError(f"duplicate fact QA source id: {source_id}")
        parsed_url = urlsplit(
            _required_text(source.get("url"), f"source {source_id} url")
        )
        if (
            parsed_url.scheme != "https"
            or parsed_url.hostname != "static.cninfo.com.cn"
        ):
            raise ValueError(
                f"fact QA source {source_id} must use an official CNINFO URL"
            )
        if not HASH_PATTERN.fullmatch(str(source.get("sha256", ""))):
            raise ValueError(f"fact QA source {source_id} has an invalid SHA-256")
        if not isinstance(source.get("bytes"), int) or source["bytes"] < 1:
            raise ValueError(f"fact QA source {source_id} has an invalid byte length")
        if source.get("authority") != "primary":
            raise ValueError(f"fact QA source {source_id} must be primary")
        published_date = _required_text(
            source.get("published_date"), f"source {source_id} published_date"
        )
        try:
            date.fromisoformat(published_date)
        except ValueError as exc:
            raise ValueError(
                f"fact QA source {source_id} published_date must be ISO 8601"
            ) from exc
        _required_text(source.get("security_code"), f"source {source_id} security_code")
        source_index[source_id] = source

    referenced_sources: set[str] = set()
    for task_id, task in task_index.items():
        source_id = _required_text(
            task.get("source_id"), f"fact QA task {task_id} source_id"
        )
        if source_id not in source_index:
            raise ValueError(f"fact QA task {task_id} references an unknown source")
        referenced_sources.add(source_id)
        if task.get("report_period") != source_index[source_id].get("report_period"):
            raise ValueError(
                f"fact QA task {task_id} report period does not match its source"
            )
        for field in ("security_code", "field", "question_en", "question_zh"):
            _required_text(task.get(field), f"fact QA task {task_id} {field}")
        if task["security_code"] != source_index[source_id]["security_code"]:
            raise ValueError(
                f"fact QA task {task_id} security code does not match its source"
            )
        as_of = _required_text(task.get("as_of"), f"fact QA task {task_id} as_of")
        try:
            parsed_as_of = datetime.fromisoformat(as_of.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"fact QA task {task_id} as_of must be ISO 8601") from exc
        if parsed_as_of.tzinfo is None:
            raise ValueError(f"fact QA task {task_id} as_of must include a UTC offset")
        if parsed_as_of.date().isoformat() != source_index[source_id]["published_date"]:
            raise ValueError(
                f"fact QA task {task_id} cutoff does not match its publication date"
            )

        label = label_index[task_id]
        _validate_label(task_id, label)
        if label["source_id"] != source_id or label["period"] != task["report_period"]:
            raise ValueError(
                f"fact QA label {task_id} does not match its task contract"
            )

    if referenced_sources != set(source_index):
        raise ValueError("fact QA source manifest contains unreferenced sources")

    return {
        "task_count": len(task_index),
        "source_count": len(source_index),
        "field_count": len({task["field"] for task in task_index.values()}),
    }


def render_fact_qa_markdown(score: dict[str, Any]) -> str:
    lines = [
        "# A-Share Point-in-Time QA Scorecard",
        "",
        "> Public development-pack result with visible labels. This is not investment performance or a hidden-test result.",
        "",
        f"- Tasks: **{score['task_count']}**",
        f"- Official sources: **{score['source_count']}**",
        f"- Exact task accuracy: **{score['exact_task_accuracy']:.1%}**",
        f"- Mean field accuracy: **{score['mean_field_accuracy']:.1%}**",
        "",
        "## Field accuracy",
        "",
        "| Field | Accuracy |",
        "| --- | ---: |",
    ]
    for field in score["scored_fields"]:
        lines.append(f"| `{field}` | {score['field_accuracy'][field]:.1%} |")
    lines.extend(
        [
            "",
            "## Task diagnostics",
            "",
            "| Task | Exact | Incorrect fields |",
            "| --- | --- | --- |",
        ]
    )
    for case in score["cases"]:
        incorrect = ", ".join(case["incorrect_fields"]) or "none"
        lines.append(
            f"| `{case['task_id']}` | {'yes' if case['exact_match'] else 'no'} | {incorrect} |"
        )
    return "\n".join(lines) + "\n"
