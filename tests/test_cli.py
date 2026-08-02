import json
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

    def test_prepare_and_verify_live_submission(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "rounds" / "2099-01"
            submission = root / "submissions" / "base-rate"
            root.mkdir(parents=True)
            question = {
                "id": "future-q1",
                "title": "Will the fixture resolve yes?",
                "close_time": "2099-01-02T00:00:00Z",
                "resolve_by": "2099-01-03T00:00:00Z",
                "resolution_criteria": "Fixture criterion.",
                "resolution_sources": ["https://example.com/source"],
                "tags": ["fixture"],
            }
            (root / "questions.jsonl").write_text(
                json.dumps(question) + "\n", encoding="utf-8"
            )
            prepare = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "open_market_eval",
                    "prepare-submission",
                    "--questions",
                    str(root / "questions.jsonl"),
                    "--command",
                    f'"{sys.executable}" examples/agents/base_rate.py',
                    "--forecaster",
                    "base-rate",
                    "--output-dir",
                    str(submission),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(prepare.returncode, 0, prepare.stdout + prepare.stderr)
            verify = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "open_market_eval",
                    "verify-live",
                    "--root",
                    str(Path(directory) / "rounds"),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)
            self.assertIn("Verified 1 live submission", verify.stdout)

            with (submission / "forecasts.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(" ")
            tampered = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "open_market_eval",
                    "verify-live",
                    "--root",
                    str(Path(directory) / "rounds"),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(tampered.returncode, 2)
            self.assertIn("seal mismatch", tampered.stdout)


if __name__ == "__main__":
    unittest.main()
