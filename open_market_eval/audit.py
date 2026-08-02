from __future__ import annotations

from typing import Any


ISSUE_CODES = {
    "adjusted_price_execution",
    "current_universe_projection",
    "delisting_survivorship",
    "revision_leakage",
    "same_close_execution",
    "t_plus_one_violation",
    "tradability_constraints_ignored",
    "transaction_costs_omitted",
}


def _submission_index(rows: list[dict[str, Any]]) -> dict[str, set[str]]:
    indexed: dict[str, set[str]] = {}
    for row in rows:
        case_id = row.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            raise ValueError("audit submission row has no case_id")
        if case_id in indexed:
            raise ValueError(f"duplicate audit submission case_id: {case_id}")
        findings = row.get("findings")
        if not isinstance(findings, list):
            raise ValueError(f"audit submission {case_id} findings must be a list")
        codes: set[str] = set()
        for finding in findings:
            if not isinstance(finding, dict) or not isinstance(finding.get("code"), str):
                raise ValueError(f"audit submission {case_id} has an invalid finding")
            code = finding["code"]
            if code not in ISSUE_CODES:
                raise ValueError(f"audit submission {case_id} has unknown issue code: {code}")
            if code in codes:
                raise ValueError(f"audit submission {case_id} repeats issue code: {code}")
            codes.add(code)
        indexed[case_id] = codes
    return indexed


def score_audit_submission(
    submissions: list[dict[str, Any]], labels: list[dict[str, Any]]
) -> dict[str, Any]:
    predicted = _submission_index(submissions)
    truth: dict[str, set[str]] = {}
    rationales: dict[str, dict[str, str]] = {}
    for row in labels:
        case_id = row.get("case_id")
        codes = row.get("issue_codes")
        if not isinstance(case_id, str) or not isinstance(codes, list):
            raise ValueError("invalid audit label row")
        if case_id in truth:
            raise ValueError(f"duplicate audit label case_id: {case_id}")
        if any(code not in ISSUE_CODES for code in codes):
            raise ValueError(f"audit label {case_id} contains an unknown issue code")
        truth[case_id] = set(codes)
        rationales[case_id] = row.get("rationales", {})

    missing = sorted(set(truth) - set(predicted))
    unknown = sorted(set(predicted) - set(truth))
    if missing:
        raise ValueError(f"audit submission is missing cases: {', '.join(missing)}")
    if unknown:
        raise ValueError(f"audit submission contains unknown cases: {', '.join(unknown)}")

    true_positive = 0
    false_positive = 0
    false_negative = 0
    exact_matches = 0
    cases = []
    issue_stats = {
        code: {"true_positive": 0, "false_positive": 0, "false_negative": 0}
        for code in sorted(ISSUE_CODES)
    }

    for case_id in truth:
        expected = truth[case_id]
        found = predicted[case_id]
        tp = found & expected
        fp = found - expected
        fn = expected - found
        true_positive += len(tp)
        false_positive += len(fp)
        false_negative += len(fn)
        exact_matches += found == expected
        for code in ISSUE_CODES:
            if code in tp:
                issue_stats[code]["true_positive"] += 1
            elif code in fp:
                issue_stats[code]["false_positive"] += 1
            elif code in fn:
                issue_stats[code]["false_negative"] += 1
        cases.append(
            {
                "case_id": case_id,
                "exact_match": found == expected,
                "correct": sorted(tp),
                "false_positives": sorted(fp),
                "missed": sorted(fn),
                "rationales": rationales[case_id],
            }
        )

    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    return {
        "benchmark": "a-share-backtest-forensics-dev-v0.1",
        "case_count": len(truth),
        "issue_class_count": len(ISSUE_CODES),
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "exact_case_accuracy": exact_matches / len(truth) if truth else 0.0,
        "cases": cases,
        "by_issue": issue_stats,
        "claim_boundary": "Development-pack score only; not investment performance or a hidden-test leaderboard result.",
    }


def render_audit_markdown(score: dict[str, Any]) -> str:
    rows = [
        "# A-Share Backtest Forensics Scorecard",
        "",
        "> Development-pack result. This is not investment performance and not a hidden-test leaderboard result.",
        "",
        f"- Cases: **{score['case_count']}**",
        f"- Precision: **{score['precision']:.1%}**",
        f"- Recall: **{score['recall']:.1%}**",
        f"- F1: **{score['f1']:.1%}**",
        f"- Exact case accuracy: **{score['exact_case_accuracy']:.1%}**",
        "",
        "| Case | Exact | Correct | Missed | False positives |",
        "| --- | --- | --- | --- | --- |",
    ]
    for case in score["cases"]:
        rows.append(
            "| {case_id} | {exact} | {correct} | {missed} | {false_positives} |".format(
                case_id=case["case_id"],
                exact="yes" if case["exact_match"] else "no",
                correct=", ".join(case["correct"]) or "none",
                missed=", ".join(case["missed"]) or "none",
                false_positives=", ".join(case["false_positives"]) or "none",
            )
        )
    return "\n".join(rows) + "\n"
