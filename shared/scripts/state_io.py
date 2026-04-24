"""
state_io.py — atomic write-tmp-rename persistence helpers.

Every JSON state file in Djinn goes through `atomic_write_json`. No direct
open('w') on state paths, ever. See `shared/conduct/verification.md` and
Emu's save-checkpoint.sh for the invariant this enforces.

Stdlib only.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


def atomic_write_json(path: Path | str, data: Any) -> None:
    """Atomically write `data` as JSON to `path` via write-tmp-rename.

    - Creates parent dirs if missing.
    - Writes to a temp file in the same directory (so rename is atomic on POSIX and Windows).
    - fsyncs the temp file before rename.
    - Never partial-writes the destination.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        prefix=p.name + ".",
        suffix=".tmp",
        dir=str(p.parent),
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, separators=(",", ":"), ensure_ascii=False)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_path, p)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def read_json(path: Path | str, default: Any = None) -> Any:
    """Read JSON; return `default` if the file is missing or malformed."""
    p = Path(path)
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def append_jsonl(path: Path | str, record: dict) -> None:
    """JSONL append with fsync. Fail-open: never raises to the caller."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(p, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, separators=(",", ":")) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
    except OSError:
        pass
