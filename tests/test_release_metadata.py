import re
import unittest
from pathlib import Path

from open_market_eval import __version__


ROOT = Path(__file__).resolve().parents[1]


def _version_from(path: Path, pattern: str) -> str:
    match = re.search(pattern, path.read_text(encoding="utf-8"), re.MULTILINE)
    if match is None:
        raise AssertionError(f"version not found in {path.name}")
    return match.group(1)


class ReleaseMetadataTests(unittest.TestCase):
    def test_public_version_metadata_stays_in_sync(self):
        pyproject_version = _version_from(
            ROOT / "pyproject.toml", r'^version = "([^"]+)"$'
        )
        citation_version = _version_from(ROOT / "CITATION.cff", r"^version: ([^\s]+)$")
        self.assertEqual(pyproject_version, __version__)
        self.assertEqual(citation_version, __version__)


if __name__ == "__main__":
    unittest.main()
