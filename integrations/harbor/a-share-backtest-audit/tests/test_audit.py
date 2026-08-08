import json
import os
import unittest
from pathlib import Path


TASK_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = TASK_ROOT / "solution" / "audit_report.json"
ARTIFACT = Path(os.environ.get("AUDIT_REPORT_ARTIFACT", "/logs/artifacts/audit_report.json"))
if not Path("/logs").exists() and not ARTIFACT.exists():
    ARTIFACT = DEFAULT_ARTIFACT

ALLOWED_CODES = {
    "same_close_execution",
    "current_universe_projection",
    "adjusted_price_execution",
    "t_plus_one_violation",
    "tradability_constraints_ignored",
    "transaction_costs_omitted",
    "revision_leakage",
    "delisting_survivorship",
}
EXPECTED_CODES = {"tradability_constraints_ignored", "t_plus_one_violation"}


class AuditArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.answer = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_contract(self):
        self.assertEqual(self.answer.get("case_id"), "bt-003")
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
