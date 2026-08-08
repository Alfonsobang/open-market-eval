import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS = (
    ROOT / "integrations" / "harbor" / "a-share-backtest-audit",
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
            (TASKS[1] / "fixtures" / "question.json", TASKS[1] / "environment" / "fixtures" / "question.json"),
        )
        for documented, runtime in pairs:
            with self.subTest(fixture=documented.name):
                self.assertEqual(
                    json.loads(documented.read_text(encoding="utf-8")),
                    json.loads(runtime.read_text(encoding="utf-8")),
                )


if __name__ == "__main__":
    unittest.main()
