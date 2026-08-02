import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CliTests(unittest.TestCase):
    def test_demo_builds_scorecard(self):
        with tempfile.TemporaryDirectory() as directory:
            completed = subprocess.run(
                [sys.executable, "-m", "open_market_eval", "demo", "--output", directory],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertTrue((Path(directory) / "seal.json").exists())
            self.assertTrue((Path(directory) / "scorecard.md").exists())
            self.assertIn("Mean Brier", completed.stdout)

    def test_stdio_agent_round_trip_validates(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "forecasts.jsonl"
            questions = "benchmarks/synthetic-smoke/questions.jsonl"
            run = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "open_market_eval",
                    "run-agent",
                    "--questions",
                    questions,
                    "--command",
                    f'"{sys.executable}" examples/agents/base_rate.py',
                    "--forecaster",
                    "base-rate",
                    "--output",
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            validate = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "open_market_eval",
                    "validate",
                    "--questions",
                    questions,
                    "--forecasts",
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(validate.returncode, 0, validate.stdout + validate.stderr)


if __name__ == "__main__":
    unittest.main()
