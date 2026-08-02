import json
import os
import unittest
from datetime import datetime
from pathlib import Path


TASK_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = TASK_ROOT / "solution" / "forecast.json"
ARTIFACT = Path(os.environ.get("MARKET_FORECAST_ARTIFACT", "/logs/artifacts/forecast.json"))
if not ARTIFACT.exists():
    ARTIFACT = DEFAULT_ARTIFACT


def timestamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class ForecastArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.answer = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.question = json.loads(
            (TASK_ROOT / "fixtures" / "question.json").read_text(encoding="utf-8")
        )

    def test_contract(self):
        required = {
            "question_id",
            "probability",
            "evidence_cutoff",
            "thesis",
            "evidence",
            "falsifiers",
            "not_investment_advice",
        }
        self.assertTrue(required.issubset(self.answer))
        self.assertEqual(self.answer["question_id"], self.question["id"])
        self.assertTrue(0 <= self.answer["probability"] <= 1)
        self.assertIs(self.answer["not_investment_advice"], True)

    def test_no_future_evidence(self):
        cutoff = timestamp(self.answer["evidence_cutoff"])
        self.assertLessEqual(cutoff, timestamp(self.question["evidence_cutoff"]))
        for item in self.answer["evidence"]:
            self.assertLessEqual(timestamp(item["published_at"]), cutoff)
            self.assertNotEqual(item["url"], "fixture://outcome-leak")


if __name__ == "__main__":
    unittest.main()
