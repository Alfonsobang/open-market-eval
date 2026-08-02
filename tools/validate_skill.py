from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    path = Path(sys.argv[1]) / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        print("invalid or missing frontmatter")
        return 1
    frontmatter = match.group(1)
    if "name: forecast-market-events" not in frontmatter or "description:" not in frontmatter:
        print("missing skill name or description")
        return 1
    if "TODO" in text:
        print("skill still contains TODO placeholders")
        return 1
    print("skill validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
