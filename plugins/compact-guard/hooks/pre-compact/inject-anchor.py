#!/usr/bin/env python3
"""
inject-anchor.py — PreCompact handler.

Prints a structural hint to stdout that the Claude Code PreCompact protocol
threads into the compaction input. The hint names the original session
intent and any refresh-deltas accumulated since. Also publishes
djinn.compact.intent-hint.injected on the event bus.

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
        from state_io import read_json
        from events import publish_intent_hint_injected
    except Exception as exc:
        print(f"[compact-guard] import error: {exc}", file=sys.stderr)
        return 0

    try:
        raw = sys.stdin.read() or "{}"
        hook_input = json.loads(raw)
    except Exception:
        hook_input = {}

    anchor_path = plugin_root.parent / "intent-anchor" / "state" / "anchor.json"
    anchor = read_json(anchor_path)
    if not anchor:
        return 0

    anchor_text = (anchor.get("anchor_text") or "").strip()
    deltas = anchor.get("refresh_deltas") or []
    delta_lines = "\n".join(f"- {d.get('delta','')}" for d in deltas if d.get("delta"))

    hint = (
        "[Djinn intent anchor — preserve across compaction]\n"
        f"Original goal: {anchor_text}\n"
    )
    if delta_lines:
        hint += f"Developer added these constraints:\n{delta_lines}\n"

    # Phase-1: emit hint to stdout. The Claude Code PreCompact protocol reads
    # this as additional context to carry into the compacted summary.
    sys.stdout.write(hint)

    try:
        publish_intent_hint_injected(
            session_id=anchor.get("session_id", "unknown"),
            hint_text=hint,
            anchor_hash=anchor.get("anchor_hash", ""),
            pre_compact_turn_count=int(hook_input.get("turn", 0) or 0),
        )
    except Exception as exc:
        print(f"[compact-guard] publish failed: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    plugin_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent.parent
    sys.exit(main(plugin_root))
