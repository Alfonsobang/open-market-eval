import json
import tempfile
import unittest
from pathlib import Path

from open_market_eval.audit import score_audit_submission
from open_market_eval.io import read_jsonl
from open_market_eval.site import build_site


ROOT = Path(__file__).resolve().parents[1]


class SiteTests(unittest.TestCase):
    def test_dashboard_is_self_contained_and_honest(self):
        audit = ROOT / "benchmarks" / "a-share-backtest-forensics"
        score = score_audit_submission(
            read_jsonl(audit / "example-submission.jsonl"),
            read_jsonl(audit / "labels.jsonl"),
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
                read_jsonl(audit / "cases.jsonl"),
                directory,
                ROOT / "docs" / "assets" / "a-share-arena-forensics.png",
            )
            index = (Path(directory) / "index.html").read_text(encoding="utf-8")
            self.assertIn("A 股研究 Agent 联赛", index)
            self.assertIn("先体检你的回测，再让 Agent 上场", index)
            self.assertIn("把你的回测假设放上检查台", index)
            self.assertIn('id="preflight-form"', index)
            self.assertIn('id="pf-findings"', index)
            self.assertIn("Backtest Forensics", index)
            self.assertIn("公开参赛 Agent", index)
            self.assertIn("不构成投资建议", index)
            self.assertIn("Harbor", index)
            self.assertIn("FORMAT FIXTURE · NOT A MODEL", index)
            self.assertEqual(index.count('data-case="'), 10)
            self.assertTrue((Path(directory) / "data" / "live-questions.jsonl").exists())
            self.assertTrue(
                (Path(directory) / "assets" / "a-share-arena-forensics.png").exists()
            )
            self.assertTrue((Path(directory) / "data" / "a-share-tracks.json").exists())
            self.assertTrue((Path(directory) / "data" / "source-registry.json").exists())
            self.assertTrue(
                (Path(directory) / "data" / "a-share-backtest-cases.json").exists()
            )
            self.assertTrue((Path(directory) / "data" / "fact-qa-tasks.jsonl").exists())
            self.assertTrue((Path(directory) / "data" / "fact-qa-labels.jsonl").exists())
            self.assertTrue((Path(directory) / "data" / "fact-qa-sources.json").exists())
            research_audit = (Path(directory) / "research-audit.html").read_text(
                encoding="utf-8"
            )
            self.assertIn("Audit the evidence before trusting the answer", research_audit)
            self.assertIn("id=\"packet-input\"", research_audit)
            self.assertIn("cutoff_violation", research_audit)
            self.assertIn("No private company data", research_audit)
            fact_qa = (Path(directory) / "filing-qa.html").read_text(encoding="utf-8")
            self.assertIn("A 股年报时点查数实验室", fact_qa)
            self.assertIn('id="check-answer"', fact_qa)
            self.assertIn("pit-300750-revenue-2024", fact_qa)
            self.assertIn("b4f1713d7b821eb076c102711d177fe9", fact_qa)
            self.assertEqual(fact_qa.count('data-task="'), 10)


if __name__ == "__main__":
    unittest.main()
