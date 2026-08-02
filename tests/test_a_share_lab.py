import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AShareLabTests(unittest.TestCase):
    def test_track_catalog_has_five_distinct_workflows(self):
        tracks = json.loads(
            (ROOT / "benchmarks" / "a-share-lab" / "tracks.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(tracks), 5)
        self.assertEqual(
            {track["id"] for track in tracks},
            {"filing-search", "point-in-time-qa", "event-forecast", "backtest-audit", "research-memo"},
        )
        for track in tracks:
            self.assertTrue(track["metrics"])
            self.assertTrue(track["failure_modes"])
            self.assertTrue(track["deliverable"])
            self.assertTrue(track["sources"])

    def test_source_registry_distinguishes_authority(self):
        sources = json.loads(
            (ROOT / "benchmarks" / "a-share-lab" / "sources.json").read_text(encoding="utf-8")
        )
        authorities = {source["authority"] for source in sources}
        self.assertEqual(authorities, {"primary", "secondary", "tool"})
        self.assertTrue(all(source["url"].startswith("https://") for source in sources))

    def test_cli_lists_and_prints_tracks(self):
        listed = subprocess.run(
            [sys.executable, "-m", "open_market_eval", "list-tracks"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(listed.returncode, 0, listed.stdout + listed.stderr)
        self.assertIn("filing-search", listed.stdout)
        self.assertIn("回测审计", listed.stdout)

        shown = subprocess.run(
            [sys.executable, "-m", "open_market_eval", "show-track", "--track", "backtest-audit"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(shown.returncode, 0, shown.stdout + shown.stderr)
        self.assertEqual(json.loads(shown.stdout)["id"], "backtest-audit")


if __name__ == "__main__":
    unittest.main()
