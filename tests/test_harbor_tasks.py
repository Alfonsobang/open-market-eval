import json
import unittest
from pathlib import Path

from open_market_eval.retrieval import audit_research_packet


ROOT = Path(__file__).resolve().parents[1]
TASKS = (
    ROOT / "integrations" / "harbor" / "a-share-backtest-audit",
    ROOT / "integrations" / "harbor" / "a-share-research-evidence",
    ROOT / "integrations" / "harbor" / "market-forecast",
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
            (TASKS[0] / "fixtures" / "case.json", TASKS[0] / "environment" / "fixtures" / "case.json"),
            (TASKS[1] / "fixtures" / "research_packet.json", TASKS[1] / "environment" / "fixtures" / "research_packet.json"),
            (TASKS[2] / "fixtures" / "question.json", TASKS[2] / "environment" / "fixtures" / "question.json"),
        )
        for documented, runtime in pairs:
            with self.subTest(fixture=documented.name):
                self.assertEqual(
                    json.loads(documented.read_text(encoding="utf-8")),
                    json.loads(runtime.read_text(encoding="utf-8")),
                )

    def test_research_evidence_task_has_exactly_two_supported_defects(self):
        packet = json.loads(
            (TASKS[1] / "fixtures" / "research_packet.json").read_text(
                encoding="utf-8"
            )
        )
        report = audit_research_packet(packet)
        self.assertEqual(
            {item["code"] for item in report["findings"]},
            {"cutoff_violation", "unsupported_claim"},
        )


if __name__ == "__main__":
    unittest.main()
