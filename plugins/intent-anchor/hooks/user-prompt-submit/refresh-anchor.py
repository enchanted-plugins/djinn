#!/usr/bin/env python3
"""
refresh-anchor.py — UserPromptSubmit handler.

If the new user prompt introduces constraints that materially differ from the
anchored intent (preservation_ratio < 0.5 against the anchor's own LCS
similarity to itself), append a delta to state/anchor.json. If no anchor
exists yet, seed it (first-turn fallback when SessionStart lacked a prompt).

Fail-open.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main(plugin_root: Path) -> int:
    shared_scripts = plugin_root.parent.parent / "shared" / "scripts"
    sys.path.insert(0, str(shared_scripts))

    try:
        from anchor import capture_anchor, refresh_anchor
        from engines.c1_lcs import normalize, preservation_ratio
        from state_io import read_json
        from events import publish_intent_captured, publish_intent_refreshed
    except Exception as exc:
        print(f"[intent-anchor] import error: {exc}", file=sys.stderr)
        return 0

    try:
        raw = sys.stdin.read() or "{}"
        hook_input = json.loads(raw)
    except Exception:
        hook_input = {}

    session_id = hook_input.get("session_id") or "unknown"
    new_prompt = (
        hook_input.get("prompt")
        or hook_input.get("user_prompt")
        or hook_input.get("message")
        or ""
    ).strip()
    turn = int(hook_input.get("turn", 0) or 0)

    if not new_prompt:
        return 0

    state_path = plugin_root / "state" / "anchor.json"
    existing = read_json(state_path)

    if not existing:
        # Seed anchor from this prompt — first-turn fallback.
        try:
            record = capture_anchor(session_id, new_prompt, state_path)
            publish_intent_captured(
                session_id=session_id,
                anchor_text=new_prompt,
                anchor_hash=record["anchor_hash"],
                intent_type=record["intent_type"],
                captured_at=record["captured_at"],
            )
        except Exception as exc:
            print(f"[intent-anchor] seed failed: {exc}", file=sys.stderr)
        return 0

    try:
        anchor_tokens = normalize(existing.get("anchor_text", ""))
        new_tokens = normalize(new_prompt)
        ratio = preservation_ratio(anchor_tokens, new_tokens)
    except Exception:
        return 0

    # Only log a refresh when the prompt is materially new. Below 0.5 LCS ratio
    # is the threshold for "introduces new constraint rather than restating".
    if ratio >= 0.5:
        return 0

    try:
        refresh_anchor(state_path, new_prompt, turn)
        publish_intent_refreshed(
            session_id=session_id,
            new_anchor_delta=new_prompt,
            turn=turn,
        )
    except Exception as exc:
        print(f"[intent-anchor] refresh failed: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    plugin_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent.parent
    sys.exit(main(plugin_root))
