import json
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
        tracks = json.loads(
            (ROOT / "benchmarks" / "a-share-lab" / "tracks.json").read_text(encoding="utf-8")
        )
        sources = json.loads(
            (ROOT / "benchmarks" / "a-share-lab" / "sources.json").read_text(encoding="utf-8")
        )
        with tempfile.TemporaryDirectory() as directory:
            build_site(
                score,
                questions,
                tracks,
                sources,
                directory,
                ROOT / "docs" / "assets" / "a-share-agent-lab.png",
            )
            index = (Path(directory) / "index.html").read_text(encoding="utf-8")
            self.assertIn("A股研究 Agent 公共实验场", index)
            self.assertIn("你的 A 股回测经得起审计吗", index)
            self.assertIn("A股公开成绩", index)
            self.assertIn("尚未发布", index)
            self.assertIn("不构成投资建议", index)
            self.assertIn("FinBench", index)
            self.assertIn("Harbor", index)
            self.assertEqual(index.count('class="track-link"'), 5)
            self.assertEqual(index.count('class="check-row"'), 8)
            self.assertTrue((Path(directory) / "data" / "live-questions.jsonl").exists())
            self.assertTrue(
                (Path(directory) / "assets" / "a-share-agent-lab.png").exists()
            )
            self.assertTrue((Path(directory) / "data" / "a-share-tracks.json").exists())
            self.assertTrue((Path(directory) / "data" / "source-registry.json").exists())


if __name__ == "__main__":
    unittest.main()
