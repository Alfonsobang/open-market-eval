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


def verify_seal(manifest: dict[str, Any], paths: list[str | Path]) -> None:
    """Verify that a seal was created from the supplied files."""
    if manifest.get("algorithm") != "sha256":
        raise ValueError("seal algorithm must be sha256")
    entries = manifest.get("files")
    if not isinstance(entries, list) or not entries:
        raise ValueError("seal must contain a non-empty files list")

    supplied = {Path(path).name: Path(path) for path in paths}
    sealed_names = [Path(entry.get("path", "")).name for entry in entries]
    if len(sealed_names) != len(set(sealed_names)):
        raise ValueError("seal contains duplicate file names")
    if set(sealed_names) != set(supplied):
        raise ValueError("seal file set does not match supplied files")

    combined = hashlib.sha256()
    for entry in entries:
        name = Path(entry["path"]).name
        payload = supplied[name].read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if entry.get("sha256") != digest or entry.get("bytes") != len(payload):
            raise ValueError(f"seal mismatch for {name}")
        combined.update(name.encode("utf-8"))
        combined.update(b"\0")
        combined.update(payload)
    if manifest.get("combined_sha256") != combined.hexdigest():
        raise ValueError("combined seal mismatch")


def canonical_digest(value: dict[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
