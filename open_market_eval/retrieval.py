from __future__ import annotations

import re
from datetime import datetime
from typing import Any
from urllib.parse import urlsplit, urlunsplit


HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"research packet {field} is required")
    return value.strip()


def _timestamp(value: Any, field: str) -> datetime:
    text = _required_text(value, field)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"research packet {field} must be ISO 8601") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"research packet {field} must include a UTC offset")
    return parsed


def _canonical_url(value: Any, field: str) -> str:
    text = _required_text(value, field)
    parsed = urlsplit(text)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"research packet {field} must be an HTTP(S) URL")
    return urlunsplit(
        (parsed.scheme.lower(), parsed.netloc.lower(), parsed.path.rstrip("/"), parsed.query, "")
    )


def _finding(code: str, severity: str, evidence: str, repair: str) -> dict[str, str]:
    return {
        "code": code,
        "severity": severity,
        "evidence": evidence,
        "repair": repair,
    }


def audit_research_packet(packet: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(packet, dict):
        raise ValueError("research packet must be an object")
    if packet.get("schema_version") != "0.1":
        raise ValueError("research packet schema_version must be 0.1")
    if packet.get("market") != "cn_a_cash":
        raise ValueError("research packet market must be cn_a_cash")

    packet_id = _required_text(packet.get("packet_id"), "packet_id")
    _required_text(packet.get("query"), "query")
    as_of = _timestamp(packet.get("as_of"), "as_of")
    evidence_items = packet.get("evidence")
    claims = packet.get("claims")
    if not isinstance(evidence_items, list) or not evidence_items:
        raise ValueError("research packet evidence must be a non-empty array")
    if not isinstance(claims, list) or not claims:
        raise ValueError("research packet claims must be a non-empty array")

    findings: list[dict[str, str]] = []
    evidence_ids: set[str] = set()
    canonical_urls: dict[str, str] = {}
    primary_source_count = 0

    for index, item in enumerate(evidence_items):
        if not isinstance(item, dict):
            raise ValueError(f"research packet evidence[{index}] must be an object")
        prefix = f"evidence[{index}]"
        evidence_id = _required_text(item.get("id"), f"{prefix}.id")
        if evidence_id in evidence_ids:
            raise ValueError(f"duplicate research packet evidence id: {evidence_id}")
        evidence_ids.add(evidence_id)
        _required_text(item.get("title"), f"{prefix}.title")
        _required_text(item.get("publisher"), f"{prefix}.publisher")
        published_at = _timestamp(item.get("published_at"), f"{prefix}.published_at")
        retrieved_at = _timestamp(item.get("retrieved_at"), f"{prefix}.retrieved_at")
        canonical_url = _canonical_url(item.get("url"), f"{prefix}.url")

        if published_at > as_of or retrieved_at > as_of:
            findings.append(
                _finding(
                    "cutoff_violation",
                    "critical",
                    f"Evidence {evidence_id} was published or retrieved after the declared as-of time.",
                    "Exclude the item or move the research cutoff forward and rerun the full packet.",
                )
            )
        if retrieved_at < published_at:
            findings.append(
                _finding(
                    "timestamp_inconsistency",
                    "high",
                    f"Evidence {evidence_id} was retrieved before its publication timestamp.",
                    "Correct the timestamps from an auditable source or remove the item.",
                )
            )
        if canonical_url in canonical_urls:
            findings.append(
                _finding(
                    "duplicate_evidence",
                    "medium",
                    f"Evidence {evidence_id} duplicates the URL used by {canonical_urls[canonical_url]}.",
                    "Deduplicate retrieval results before measuring source coverage.",
                )
            )
        else:
            canonical_urls[canonical_url] = evidence_id
        if not isinstance(item.get("content_sha256"), str) or not HASH_PATTERN.fullmatch(
            item["content_sha256"]
        ):
            findings.append(
                _finding(
                    "unsealed_evidence",
                    "high",
                    f"Evidence {evidence_id} has no valid lowercase SHA-256 content digest.",
                    "Hash the frozen evidence payload and store the 64-character digest.",
                )
            )
        if item.get("is_primary") is True:
            primary_source_count += 1
        elif item.get("is_primary") is not False:
            raise ValueError(f"research packet {prefix}.is_primary must be a boolean")

    if primary_source_count == 0:
        findings.append(
            _finding(
                "primary_source_missing",
                "high",
                "The packet contains no evidence marked as a primary source.",
                "Add the relevant filing, exchange notice, regulator release, or issuer disclosure.",
            )
        )

    claim_ids: set[str] = set()
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            raise ValueError(f"research packet claims[{index}] must be an object")
        prefix = f"claims[{index}]"
        claim_id = _required_text(claim.get("id"), f"{prefix}.id")
        if claim_id in claim_ids:
            raise ValueError(f"duplicate research packet claim id: {claim_id}")
        claim_ids.add(claim_id)
        _required_text(claim.get("text"), f"{prefix}.text")
        cited = claim.get("evidence_ids")
        if not isinstance(cited, list):
            raise ValueError(f"research packet {prefix}.evidence_ids must be an array")
        if any(not isinstance(item, str) for item in cited):
            raise ValueError(
                f"research packet {prefix}.evidence_ids must contain strings"
            )
        unknown = [item for item in cited if item not in evidence_ids]
        if not cited or unknown:
            detail = "no evidence" if not cited else "unknown evidence: " + ", ".join(unknown)
            findings.append(
                _finding(
                    "unsupported_claim",
                    "critical",
                    f"Claim {claim_id} cites {detail}.",
                    "Attach at least one evidence ID that exists in this frozen packet.",
                )
            )

    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda item: (severity_order[item["severity"]], item["code"], item["evidence"]))
    return {
        "packet_id": packet_id,
        "market": "cn_a_cash",
        "as_of": packet["as_of"],
        "passed": not findings,
        "finding_count": len(findings),
        "critical_count": sum(item["severity"] == "critical" for item in findings),
        "evidence_count": len(evidence_items),
        "claim_count": len(claims),
        "primary_source_count": primary_source_count,
        "checks_run": 6,
        "findings": findings,
        "claim_boundary": "Static evidence-integrity audit only; it does not verify claim truth or recommend securities.",
    }


def render_research_audit_markdown(report: dict[str, Any]) -> str:
    status = "PASS" if report["passed"] else "REVIEW REQUIRED"
    lines = [
        "# A-Share Research Evidence Audit",
        "",
        f"**{report['packet_id']}** - **{status}**",
        "",
        f"- Checks run: **{report['checks_run']}**",
        f"- Evidence items: **{report['evidence_count']}**",
        f"- Claims: **{report['claim_count']}**",
        f"- Findings: **{report['finding_count']}**",
        f"- Critical: **{report['critical_count']}**",
        "",
        "> Static evidence-integrity audit only. This does not verify claim truth or recommend securities.",
        "",
    ]
    if not report["findings"]:
        lines.append("No configured integrity defects were detected. Source relevance and claim truth still require independent review.")
    else:
        lines.extend(["| Severity | Code | Evidence | Repair |", "| --- | --- | --- | --- |"])
        for finding in report["findings"]:
            lines.append(
                f"| {finding['severity']} | `{finding['code']}` | {finding['evidence']} | {finding['repair']} |"
            )
    return "\n".join(lines) + "\n"
