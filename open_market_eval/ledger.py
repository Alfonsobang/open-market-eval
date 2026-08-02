from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def seal_files(paths: list[str | Path]) -> dict[str, Any]:
    files = []
    combined = hashlib.sha256()
    for raw_path in sorted(map(Path, paths), key=lambda item: item.as_posix()):
        payload = raw_path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        combined.update(raw_path.name.encode("utf-8"))
        combined.update(b"\0")
        combined.update(payload)
        files.append({"path": raw_path.as_posix(), "sha256": digest, "bytes": len(payload)})
    return {
        "algorithm": "sha256",
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "combined_sha256": combined.hexdigest(),
        "files": files,
        "note": "Commit this manifest before outcomes are known to create a public audit trail.",
    }


def canonical_digest(value: dict[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
