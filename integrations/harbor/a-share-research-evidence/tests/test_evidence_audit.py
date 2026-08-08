import json
import os
import unittest
from pathlib import Path


TASK_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = TASK_ROOT / "solution" / "evidence_audit.json"
ARTIFACT = Path(
    os.environ.get("EVIDENCE_AUDIT_ARTIFACT", "/logs/artifacts/evidence_audit.json")
)
if not Path("/logs").exists() and not ARTIFACT.exists():
    ARTIFACT = DEFAULT_ARTIFACT

ALLOWED_CODES = {
    "cutoff_violation",
    "timestamp_inconsistency",
    "duplicate_evidence",
    "unsealed_evidence",
    "primary_source_missing",
    "unsupported_claim",
}
EXPECTED_CODES = {"cutoff_violation", "unsupported_claim"}


class EvidenceAuditArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.answer = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_contract(self):
        self.assertEqual(self.answer.get("packet_id"), "search-001")
        findings = self.answer.get("findings")
        self.assertIsInstance(findings, list)
        self.assertEqual(len(findings), len(EXPECTED_CODES))
        for finding in findings:
            self.assertIn(finding.get("code"), ALLOWED_CODES)
            self.assertIn(finding.get("severity"), {"critical", "high", "medium", "low"})
            self.assertGreaterEqual(len(finding.get("evidence", "")), 20)

    def test_exact_defect_detection(self):
        codes = {finding["code"] for finding in self.answer["findings"]}
        self.assertEqual(codes, EXPECTED_CODES)


if __name__ == "__main__":
    unittest.main()
