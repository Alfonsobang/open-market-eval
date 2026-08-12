import json
import unittest
from pathlib import Path

from open_market_eval.retrieval import audit_research_packet


ROOT = Path(__file__).resolve().parents[1]
BACKTEST_TASK = ROOT / "integrations" / "harbor" / "a-share-backtest-audit"
FACT_QA_TASK = ROOT / "integrations" / "harbor" / "a-share-point-in-time-qa"
RESEARCH_TASK = ROOT / "integrations" / "harbor" / "a-share-research-evidence"
FORECAST_TASK = ROOT / "integrations" / "harbor" / "market-forecast"
TASKS = (
    BACKTEST_TASK,
    FACT_QA_TASK,
    RESEARCH_TASK,
    FORECAST_TASK,
)


class HarborTaskTests(unittest.TestCase):
    def test_tasks_follow_current_portable_contract(self):
        for task in TASKS:
            with self.subTest(task=task.name):
                config = (task / "task.toml").read_text(encoding="utf-8")
                self.assertIn('schema_version = "1.3"', config)
                self.assertIn('network_mode = "no-network"', config)
                self.assertTrue((task / "environment" / "Dockerfile").exists())
                self.assertTrue((task / "solution" / "solve.sh").exists())
                test_script = (task / "tests" / "test.sh").read_text(encoding="utf-8")
                self.assertIn("/logs/verifier/reward.txt", test_script)
                self.assertNotIn("artifacts =", config)

    def test_runtime_fixtures_match_documented_fixtures(self):
        pairs = (
            (
                BACKTEST_TASK / "fixtures" / "case.json",
                BACKTEST_TASK / "environment" / "fixtures" / "case.json",
            ),
            (
                FACT_QA_TASK / "fixtures" / "filing_page.json",
                FACT_QA_TASK / "environment" / "fixtures" / "filing_page.json",
            ),
            (
                RESEARCH_TASK / "fixtures" / "research_packet.json",
                RESEARCH_TASK / "environment" / "fixtures" / "research_packet.json",
            ),
            (
                FORECAST_TASK / "fixtures" / "question.json",
                FORECAST_TASK / "environment" / "fixtures" / "question.json",
            ),
        )
        for documented, runtime in pairs:
            with self.subTest(fixture=documented.name):
                self.assertEqual(
                    json.loads(documented.read_text(encoding="utf-8")),
                    json.loads(runtime.read_text(encoding="utf-8")),
                )

    def test_research_evidence_task_has_exactly_two_supported_defects(self):
        packet = json.loads(
            (RESEARCH_TASK / "fixtures" / "research_packet.json").read_text(
                encoding="utf-8"
            )
        )
        report = audit_research_packet(packet)
        self.assertEqual(
            {item["code"] for item in report["findings"]},
            {"cutoff_violation", "unsupported_claim"},
        )

    def test_fact_qa_task_matches_the_public_benchmark(self):
        benchmark = ROOT / "benchmarks" / "a-share-point-in-time-qa"
        fixture = json.loads(
            (FACT_QA_TASK / "fixtures" / "filing_page.json").read_text(encoding="utf-8")
        )
        labels = [
            json.loads(line)
            for line in (benchmark / "labels.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        ]
        sources = json.loads((benchmark / "sources.json").read_text(encoding="utf-8"))[
            "sources"
        ]
        label = next(row for row in labels if row["task_id"] == fixture["task_id"])
        source = next(row for row in sources if row["id"] == label["source_id"])

        self.assertEqual(fixture["source"]["url"], source["url"])
        self.assertEqual(fixture["source"]["content_sha256"], source["sha256"])
        self.assertEqual(fixture["source"]["pdf_page"], label["pdf_page"])
        self.assertEqual(fixture["table"]["declared_unit"], label["unit"])
        self.assertEqual(fixture["table"]["rows"][0]["2024"], label["value"])


if __name__ == "__main__":
    unittest.main()
