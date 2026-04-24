#!/usr/bin/env python3
"""
update-posterior.py — PreCompact handler.

Reads session summary: (intent_type, developer, session_length, mean_preservation).
Folds into state/learnings.jsonl per-key record via D5 EMA update.

Fail-open.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def main(plugin_root: Path) -> int:
    shared_scripts = plugin_root.parent.parent / "shared" / "scripts"
    sys.path.insert(0, str(shared_scripts))

    try:
        from engines.c5_gauss import update_posterior
        from state_io import read_json, atomic_write_json, append_jsonl
    except Exception as exc:
        print(f"[drift-learning] import error: {exc}", file=sys.stderr)
        return 0

    anchor_path = plugin_root.parent / "intent-anchor" / "state" / "anchor.json"
    reservoir_path = plugin_root.parent / "drift-aligner" / "state" / "reservoir.json"
    anchor = read_json(anchor_path)
    rstate = read_json(reservoir_path, default={"n_seen": 0, "reservoir": []})
    if not anchor:
        return 0

    samples = [float(r.get("score", 1.0)) for r in rstate.get("reservoir", [])]
    if not samples:
        return 0

    mean_preservation = sum(samples) / len(samples)
    developer = os.environ.get("USER") or os.environ.get("USERNAME") or "unknown"
    intent_type = anchor.get("intent_type", "unknown")
    session_length = int(rstate.get("n_seen", 0))

    observation = {
        "preservation_score": mean_preservation,
        "session_length": session_length,
        "intent_type": intent_type,
        "developer": developer,
    }

    # Keyed posterior: one record per (intent_type, developer).
    posteriors_path = plugin_root / "state" / "posteriors.json"
    book = read_json(posteriors_path, default={})
    key = f"{intent_type}::{developer}"
    prior = book.get(key, {})
    updated = update_posterior(prior, observation)
    book[key] = updated
    atomic_write_json(posteriors_path, book)

    # Append-only session log for later backtesting.
    append_jsonl(
        plugin_root / "state" / "learnings.jsonl",
        {
            "session_id": anchor.get("session_id"),
            "intent_type": intent_type,
            "developer": developer,
            "mean_preservation": mean_preservation,
            "session_length": session_length,
            "n_samples": len(samples),
        },
    )
    return 0


if __name__ == "__main__":
    plugin_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent.parent
    sys.exit(main(plugin_root))
