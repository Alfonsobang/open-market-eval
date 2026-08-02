import json
import unittest
from pathlib import Path

from open_market_eval.io import read_jsonl
from open_market_eval.ledger import seal_files
from open_market_eval.validation import validate_forecast, validate_question


ROOT = Path(__file__).resolve().parents[1]
ROUND = ROOT / "live" / "rounds" / "2026-08"


class LiveRoundTests(unittest.TestCase):
    def test_question_slate_and_baseline_are_time_safe(self):
        questions = read_jsonl(ROUND / "questions.jsonl")
        forecasts = read_jsonl(ROUND / "baselines" / "uninformative-0-5.jsonl")
        self.assertEqual(len(questions), 6)
        self.assertEqual(len(forecasts), 6)
        by_id = {question["id"]: question for question in questions}
        for question in questions:
            validate_question(question)
            self.assertEqual(question["integrity_level"], "L2-live-sealed")
            self.assertTrue(question["resolution_sources"])
        for forecast in forecasts:
            validate_forecast(forecast, by_id[forecast["question_id"]])
            self.assertEqual(forecast["probability"], 0.5)
            self.assertEqual(forecast["evidence"], [])

    def test_committed_seal_matches_files(self):
        expected = json.loads((ROUND / "seal.json").read_text(encoding="utf-8"))
        actual = seal_files(
            [
                ROUND / "questions.jsonl",
                ROUND / "baselines" / "uninformative-0-5.jsonl",
            ]
        )
        self.assertEqual(actual["combined_sha256"], expected["combined_sha256"])
        self.assertEqual(
            [row["sha256"] for row in actual["files"]],
            [row["sha256"] for row in expected["files"]],
        )


if __name__ == "__main__":
    unittest.main()
