"""
anchor.py — session-intent anchor capture + hash.

The anchor is captured ONCE at SessionStart and lives in state/anchor.json
(out-of-context state). Reinjected only at PreCompact and never repeated
mid-context — see Djinn failure-block §"Recall valley repetition".

Stdlib only.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from state_io import atomic_write_json, read_json


INTENT_KEYWORDS = {
    "feature": ("add", "build", "implement", "create", "introduce", "ship"),
    "bugfix": ("fix", "bug", "broken", "regression", "repair", "patch"),
    "refactor": ("refactor", "rename", "reorganize", "cleanup", "restructure", "simplify"),
    "research": ("research", "investigate", "explore", "analyze", "study", "compare"),
    "docs": ("document", "docs", "readme", "changelog", "comment"),
}


def classify_intent(text: str) -> str:
    """Heuristic intent classification. Returns one of {feature,bugfix,refactor,research,docs,unknown}."""
    t = text.lower()
    scores = {kind: sum(1 for kw in kws if kw in t) for kind, kws in INTENT_KEYWORDS.items()}
    best_kind, best_score = max(scores.items(), key=lambda kv: kv[1])
    return best_kind if best_score > 0 else "unknown"


def anchor_hash(text: str) -> str:
    """Stable 12-char sha1 of the normalized anchor text."""
    return hashlib.sha1(text.strip().lower().encode("utf-8")).hexdigest()[:12]


def capture_anchor(
    session_id: str,
    anchor_text: str,
    state_path: Path,
) -> dict:
    """Write anchor.json for the session. Called exactly once per session."""
    record = {
        "session_id": session_id,
        "anchor_text": anchor_text,
        "anchor_hash": anchor_hash(anchor_text),
        "intent_type": classify_intent(anchor_text),
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "refresh_deltas": [],
    }
    atomic_write_json(state_path, record)
    return record


def refresh_anchor(
    state_path: Path,
    new_constraint: str,
    turn: int,
) -> Optional[dict]:
    """Append a constraint delta to the existing anchor.json. No-op if no anchor exists."""
    existing = read_json(state_path)
    if not existing or not isinstance(existing, dict):
        return None
    deltas = list(existing.get("refresh_deltas", []))
    deltas.append({"delta": new_constraint, "turn": turn})
    existing["refresh_deltas"] = deltas
    atomic_write_json(state_path, existing)
    return existing
