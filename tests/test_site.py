import tempfile
import unittest
from pathlib import Path

from open_market_eval.io import read_jsonl
from open_market_eval.scoring import score_forecasts
from open_market_eval.site import build_site


ROOT = Path(__file__).resolve().parents[1]


class SiteTests(unittest.TestCase):
    def test_dashboard_is_self_contained_and_honest(self):
        smoke = ROOT / "benchmarks" / "synthetic-smoke"
        score = score_forecasts(
            read_jsonl(smoke / "forecasts.jsonl"),
            read_jsonl(smoke / "resolutions.jsonl"),
        )
        questions = read_jsonl(ROOT / "live" / "rounds" / "2026-08" / "questions.jsonl")
        with tempfile.TemporaryDirectory() as directory:
            build_site(
                score,
                questions,
                directory,
                ROOT / "docs" / "assets" / "open-market-eval-hero.png",
            )
            index = (Path(directory) / "index.html").read_text(encoding="utf-8")
            self.assertIn("Forecast the event. Audit the agent.", index)
            self.assertIn("Synthetic fixture", index)
            self.assertIn("Nothing here is investment advice", index)
            self.assertIn("ForecastBench-Sim", index)
            self.assertIn("Harbor", index)
            self.assertIn("technical lineage, not as endorsements", index)
            self.assertEqual(index.count('class="live-question"'), 6)
            self.assertTrue((Path(directory) / "data" / "live-questions.jsonl").exists())
            self.assertTrue(
                (Path(directory) / "assets" / "open-market-eval-hero.png").exists()
            )
            self.assertTrue((Path(directory) / "data" / "research-references.json").exists())


if __name__ == "__main__":
    unittest.main()
