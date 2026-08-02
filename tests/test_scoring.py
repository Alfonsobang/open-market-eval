import unittest

from open_market_eval.scoring import brier_score, score_forecasts


class ScoringTests(unittest.TestCase):
    def test_brier_score(self):
        self.assertAlmostEqual(brier_score(0.8, 1), 0.04)

    def test_summary_beats_uninformative_baseline(self):
        forecasts = [
            {"question_id": "a", "forecaster": "x", "probability": 0.8},
            {"question_id": "b", "forecaster": "x", "probability": 0.2},
        ]
        resolutions = [
            {"question_id": "a", "outcome": 1},
            {"question_id": "b", "outcome": 0},
        ]
        result = score_forecasts(forecasts, resolutions)
        self.assertEqual(result["mean_brier"], 0.04)
        self.assertGreater(result["brier_skill_vs_0_5"], 0)


if __name__ == "__main__":
    unittest.main()
