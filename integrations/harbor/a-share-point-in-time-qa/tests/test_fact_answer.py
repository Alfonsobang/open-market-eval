import json
import os
import unittest
from decimal import Decimal
from pathlib import Path


TASK_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = TASK_ROOT / "solution" / "fact_answer.json"
ARTIFACT = Path(
    os.environ.get("FACT_ANSWER_ARTIFACT", "/logs/artifacts/fact_answer.json")
)
if not Path("/logs").exists() and not ARTIFACT.exists():
    ARTIFACT = DEFAULT_ARTIFACT


class FactAnswerArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.answer = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_exact_contract(self):
        self.assertEqual(
            set(self.answer),
            {
                "task_id",
                "value",
                "unit",
                "normalized_value_yuan",
                "period",
                "scope",
                "pdf_page",
                "source_id",
            },
        )
        self.assertEqual(self.answer["task_id"], "pit-300750-revenue-2024")

    def test_exact_value_and_unit_conversion(self):
        self.assertEqual(self.answer["value"], "362012554")
        self.assertEqual(self.answer["unit"], "CNY_THOUSAND")
        self.assertEqual(self.answer["normalized_value_yuan"], "362012554000")
        self.assertEqual(
            Decimal(self.answer["value"]) * 1000,
            Decimal(self.answer["normalized_value_yuan"]),
        )

    def test_period_scope_and_source_provenance(self):
        self.assertEqual(self.answer["period"], "2024")
        self.assertEqual(self.answer["scope"], "listed_company_consolidated")
        self.assertEqual(self.answer["pdf_page"], 9)
        self.assertEqual(self.answer["source_id"], "cninfo-300750-2024-annual")


if __name__ == "__main__":
    unittest.main()
