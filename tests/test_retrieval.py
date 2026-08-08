import json
import unittest
from pathlib import Path

from open_market_eval.retrieval import audit_research_packet, render_research_audit_markdown


ROOT = Path(__file__).resolve().parents[1]


class ResearchPacketAuditTests(unittest.TestCase):
    def load(self, name):
        return json.loads(
            (ROOT / "examples" / "research-packets" / name).read_text(encoding="utf-8")
        )

    def test_leaky_packet_exposes_all_six_failure_classes(self):
        report = audit_research_packet(self.load("leaky-packet.json"))
        codes = {item["code"] for item in report["findings"]}
        self.assertFalse(report["passed"])
        self.assertEqual(report["checks_run"], 6)
        self.assertEqual(
            codes,
            {
                "cutoff_violation",
                "timestamp_inconsistency",
                "duplicate_evidence",
                "unsealed_evidence",
                "primary_source_missing",
                "unsupported_claim",
            },
        )
        self.assertIn("REVIEW REQUIRED", render_research_audit_markdown(report))

    def test_conservative_packet_passes_static_checks(self):
        report = audit_research_packet(self.load("conservative-packet.json"))
        self.assertTrue(report["passed"])
        self.assertEqual(report["finding_count"], 0)
        self.assertEqual(report["primary_source_count"], 1)
        self.assertIn("independent review", render_research_audit_markdown(report))

    def test_naive_cutoff_is_rejected(self):
        packet = self.load("conservative-packet.json")
        packet["as_of"] = "2025-04-30T15:00:00"
        with self.assertRaisesRegex(ValueError, "UTC offset"):
            audit_research_packet(packet)

    def test_duplicate_evidence_id_is_rejected(self):
        packet = self.load("leaky-packet.json")
        packet["evidence"][1]["id"] = packet["evidence"][0]["id"]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            audit_research_packet(packet)

    def test_non_string_claim_reference_is_rejected(self):
        packet = self.load("conservative-packet.json")
        packet["claims"][0]["evidence_ids"] = [1]
        with self.assertRaisesRegex(ValueError, "contain strings"):
            audit_research_packet(packet)


if __name__ == "__main__":
    unittest.main()
