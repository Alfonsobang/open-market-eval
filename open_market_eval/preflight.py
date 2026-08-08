from __future__ import annotations

from typing import Any


def _require_mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"backtest contract field must be an object: {field}")
    return value


def _require_choice(value: Any, field: str, choices: set[str]) -> str:
    if value not in choices:
        allowed = ", ".join(sorted(choices))
        raise ValueError(f"backtest contract {field} must be one of: {allowed}")
    return value


def _finding(
    code: str, severity: str, evidence: str, repair: str
) -> dict[str, str]:
    return {
        "code": code,
        "severity": severity,
        "evidence": evidence,
        "repair": repair,
    }


def audit_backtest_contract(contract: dict[str, Any]) -> dict[str, Any]:
    if contract.get("schema_version") != "0.1":
        raise ValueError("backtest contract schema_version must be 0.1")
    if contract.get("market") != "cn_a_cash":
        raise ValueError("backtest contract market must be cn_a_cash")
    name = contract.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("backtest contract name is required")

    signal = _require_mapping(contract.get("signal"), "signal")
    universe = _require_mapping(contract.get("universe"), "universe")
    prices = _require_mapping(contract.get("prices"), "prices")
    settlement = _require_mapping(contract.get("settlement"), "settlement")
    tradability = _require_mapping(contract.get("tradability"), "tradability")
    costs = _require_mapping(contract.get("costs"), "costs")
    fundamentals = _require_mapping(contract.get("fundamentals"), "fundamentals")

    formed_at = _require_choice(
        signal.get("formed_at"),
        "signal.formed_at",
        {"before_open", "intraday", "after_close"},
    )
    execution = _require_choice(
        signal.get("execution"),
        "signal.execution",
        {"same_close", "next_open", "next_vwap", "custom"},
    )
    universe_policy = _require_choice(
        universe.get("policy"),
        "universe.policy",
        {"point_in_time", "current_snapshot"},
    )
    execution_series = _require_choice(
        prices.get("execution_series"),
        "prices.execution_series",
        {"raw", "adjusted"},
    )
    revision_policy = _require_choice(
        fundamentals.get("version_policy"),
        "fundamentals.version_policy",
        {"as_reported", "latest_backfilled"},
    )

    findings: list[dict[str, str]] = []
    if formed_at == "after_close" and execution == "same_close":
        findings.append(
            _finding(
                "same_close_execution",
                "critical",
                "The signal is formed after the close but filled at that same close.",
                "Shift execution to the next tradable timestamp or form the signal before the claimed fill.",
            )
        )
    if universe_policy == "current_snapshot":
        findings.append(
            _finding(
                "current_universe_projection",
                "critical",
                "The current security universe is projected into historical dates.",
                "Reconstruct the eligible universe for every historical decision date.",
            )
        )
    if universe.get("includes_delisted") is not True:
        findings.append(
            _finding(
                "delisting_survivorship",
                "critical",
                "Delisted securities and their terminal returns are not retained.",
                "Include delisted names, delisting periods, and terminal valuation rules.",
            )
        )
    if execution_series == "adjusted":
        findings.append(
            _finding(
                "adjusted_price_execution",
                "high",
                "Adjusted prices are used as simulated transaction prices.",
                "Use raw historical prices for fills and adjusted series only for return or signal calculations.",
            )
        )
    if settlement.get("enforce_t_plus_one") is not True:
        findings.append(
            _finding(
                "t_plus_one_violation",
                "critical",
                "The simulator does not enforce T+1 sale eligibility for newly purchased A-share cash positions.",
                "Track acquisition date by lot and block same-day sales of newly purchased cash-equity positions.",
            )
        )
    missing_constraints = [
        name
        for name in ("suspensions", "price_limits")
        if tradability.get(name) is not True
    ]
    if missing_constraints:
        findings.append(
            _finding(
                "tradability_constraints_ignored",
                "critical",
                "The execution model omits: " + ", ".join(missing_constraints) + ".",
                "Reject or defer orders when suspension or limit-state rules make the requested fill unavailable.",
            )
        )
    numeric_costs = []
    for field in ("commission_bps", "stamp_duty_bps_sell", "slippage_bps"):
        value = costs.get(field)
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError(f"backtest contract costs.{field} must be a non-negative number")
        numeric_costs.append(float(value))
    if sum(numeric_costs) == 0:
        findings.append(
            _finding(
                "transaction_costs_omitted",
                "high",
                "Commission, sell-side stamp duty, and slippage are all configured as zero.",
                "Report net results under dated fee rules and multiple slippage assumptions.",
            )
        )
    if revision_policy == "latest_backfilled":
        findings.append(
            _finding(
                "revision_leakage",
                "critical",
                "The latest revised fundamental values are backfilled into earlier research dates.",
                "Version fundamentals by first-publication timestamp and apply revisions only after they become visible.",
            )
        )

    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda item: (severity_order[item["severity"]], item["code"]))
    return {
        "contract_name": name.strip(),
        "market": "cn_a_cash",
        "passed": not findings,
        "finding_count": len(findings),
        "critical_count": sum(item["severity"] == "critical" for item in findings),
        "findings": findings,
        "checks_run": 8,
        "claim_boundary": "Static research-design preflight only; it does not validate returns or recommend securities.",
    }


def render_preflight_markdown(report: dict[str, Any]) -> str:
    status = "PASS" if report["passed"] else "REVIEW REQUIRED"
    lines = [
        "# A-Share Backtest Preflight",
        "",
        f"**{report['contract_name']}** - **{status}**",
        "",
        f"- Checks run: **{report['checks_run']}**",
        f"- Findings: **{report['finding_count']}**",
        f"- Critical: **{report['critical_count']}**",
        "",
        "> Static research-design preflight only. This does not validate returns or recommend securities.",
        "",
    ]
    if not report["findings"]:
        lines.append("No configured design defects were detected. Data integrity and implementation still require independent review.")
    else:
        lines.extend(["| Severity | Code | Evidence | Repair |", "| --- | --- | --- | --- |"])
        for finding in report["findings"]:
            lines.append(
                f"| {finding['severity']} | `{finding['code']}` | {finding['evidence']} | {finding['repair']} |"
            )
    return "\n".join(lines) + "\n"
