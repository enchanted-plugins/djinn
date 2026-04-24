"""
Djinn event-bus helpers — typed wrappers over shared.scripts.publish.publish.

Exposes one function per published topic listed in `CLAUDE.md § Events`.
Every helper is fail-open per shared/conduct/hooks.md — advisory, never raises.

Phase-1 file-tail fallback: publishes go through Pech's `publish.py` (copied
verbatim into `shared/scripts/publish.py`) which JSONL-appends events to the
enchanted-mcp bus file. See docs/ecosystem.md for the cross-plugin contract.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure the sibling publish.py is importable regardless of invocation cwd.
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from publish import publish  # noqa: E402


def publish_intent_captured(
    session_id: str,
    anchor_text: str,
    anchor_hash: str,
    intent_type: str,
    captured_at: str,
) -> None:
    """djinn.intent.captured — emitted by intent-anchor on SessionStart."""
    publish(
        "djinn.intent.captured",
        {
            "session_id": session_id,
            "anchor_text": anchor_text,
            "anchor_hash": anchor_hash,
            "intent_type": intent_type,
            "captured_at": captured_at,
        },
    )


def publish_drift_detected(
    session_id: str,
    preservation_score: float,
    ci_low: float,
    ci_high: float,
    N: int,
    turn: int,
    drift_kind: str,
) -> None:
    """djinn.drift.detected — honest-numbers contract: (value, ci_low, ci_high, N) required.

    drift_kind ∈ {side_quest, lost, refocus}.
    """
    publish(
        "djinn.drift.detected",
        {
            "session_id": session_id,
            "preservation_score": preservation_score,
            "ci_low": ci_low,
            "ci_high": ci_high,
            "N": N,
            "turn": turn,
            "drift_kind": drift_kind,
        },
    )


def publish_intent_hint_injected(
    session_id: str,
    hint_text: str,
    anchor_hash: str,
    pre_compact_turn_count: int,
) -> None:
    """djinn.compact.intent-hint.injected — emitted by compact-guard at PreCompact."""
    publish(
        "djinn.compact.intent-hint.injected",
        {
            "session_id": session_id,
            "hint_text": hint_text,
            "anchor_hash": anchor_hash,
            "pre_compact_turn_count": pre_compact_turn_count,
        },
    )


def publish_intent_refreshed(
    session_id: str,
    new_anchor_delta: str,
    turn: int,
) -> None:
    """djinn.intent.refreshed — emitted by intent-anchor on UserPromptSubmit with new constraints."""
    publish(
        "djinn.intent.refreshed",
        {
            "session_id": session_id,
            "new_anchor_delta": new_anchor_delta,
            "turn": turn,
        },
    )


__all__ = [
    "publish_intent_captured",
    "publish_drift_detected",
    "publish_intent_hint_injected",
    "publish_intent_refreshed",
]
