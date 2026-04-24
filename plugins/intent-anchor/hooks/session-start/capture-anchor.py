#!/usr/bin/env python3
"""
capture-anchor.py — SessionStart handler.

Reads the hook payload from stdin. If a first-turn prompt is present AND no
anchor exists for this session_id, captures it into state/anchor.json and
publishes djinn.intent.captured. Otherwise no-op.

Fail-open: never raises to the caller.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main(plugin_root: Path) -> int:
    shared_scripts = plugin_root.parent.parent / "shared" / "scripts"
    sys.path.insert(0, str(shared_scripts))

    try:
        from anchor import capture_anchor
        from state_io import read_json
        from events import publish_intent_captured
    except Exception as exc:
        print(f"[intent-anchor] import error: {exc}", file=sys.stderr)
        return 0

    try:
        raw = sys.stdin.read() or "{}"
        hook_input = json.loads(raw)
    except Exception:
        hook_input = {}

    session_id = (
        hook_input.get("session_id")
        or hook_input.get("transcript_path")
        or "unknown"
    )
    initial_prompt = (
        hook_input.get("prompt")
        or hook_input.get("user_prompt")
        or hook_input.get("message")
        or ""
    )

    if not initial_prompt.strip():
        # SessionStart may fire before the first user prompt. The
        # UserPromptSubmit hook will seed the anchor on next fire.
        return 0

    state_path = plugin_root / "state" / "anchor.json"
    existing = read_json(state_path)
    if existing and existing.get("session_id") == session_id:
        return 0

    try:
        record = capture_anchor(session_id, initial_prompt, state_path)
        publish_intent_captured(
            session_id=session_id,
            anchor_text=initial_prompt,
            anchor_hash=record["anchor_hash"],
            intent_type=record["intent_type"],
            captured_at=record["captured_at"],
        )
    except Exception as exc:
        print(f"[intent-anchor] capture failed: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    plugin_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent.parent
    sys.exit(main(plugin_root))
