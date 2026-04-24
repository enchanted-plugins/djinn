#!/usr/bin/env python3
"""
align-turn.py — PostToolUse handler.

Per-turn flow:
  1. Read the anchor from intent-anchor/state/anchor.json.
  2. Extract the current-turn utterance (tool_input + tool_response summary).
  3. Compute D1 preservation_ratio.
  4. Update D3 reservoir in state/reservoir.json (atomic).
  5. Update D2 HMM state sequence in state/states.jsonl (append).
  6. Compute (score, ci_low, ci_high, N) from reservoir samples via bootstrap.
  7. If score < 0.7 AND N >= 5, emit djinn.drift.detected + stderr advisory.

Honest-numbers contract: advisory ALWAYS carries (value, ci_low, ci_high, N).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


DRIFT_THRESHOLD = 0.7
MIN_N_FOR_ADVISORY = 5


def main(plugin_root: Path) -> int:
    shared_scripts = plugin_root.parent.parent / "shared" / "scripts"
    sys.path.insert(0, str(shared_scripts))

    try:
        from bootstrap_ci import bootstrap_ci
        from engines.c1_lcs import normalize, preservation_ratio
        from engines.c2_hmm import infer_states
        from engines.c3_reservoir import update_reservoir
        from state_io import atomic_write_json, read_json, append_jsonl
        from events import publish_drift_detected
    except Exception as exc:
        print(f"[drift-aligner] import error: {exc}", file=sys.stderr)
        return 0

    try:
        raw = sys.stdin.read() or "{}"
        hook_input = json.loads(raw)
    except Exception:
        hook_input = {}

    # Find the anchor written by intent-anchor.
    anchor_path = plugin_root.parent / "intent-anchor" / "state" / "anchor.json"
    anchor = read_json(anchor_path)
    if not anchor:
        return 0

    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {}) or {}
    tool_response = hook_input.get("tool_response", {}) or {}

    # Compose the turn's utterance from the fields most likely to carry intent.
    utterance_parts = []
    for key in ("prompt", "query", "description", "command", "file_path", "content"):
        v = tool_input.get(key)
        if isinstance(v, str):
            utterance_parts.append(v)
    for key in ("output", "stdout", "result"):
        v = tool_response.get(key)
        if isinstance(v, str):
            utterance_parts.append(v[:500])
    utterance = " ".join(utterance_parts)

    if not utterance.strip():
        return 0

    anchor_tokens = normalize(anchor.get("anchor_text", ""))
    turn_tokens = normalize(utterance)
    score = preservation_ratio(anchor_tokens, turn_tokens)

    session_id = anchor.get("session_id", "unknown")
    turn_idx = int(hook_input.get("turn", 0) or 0)

    # D3 reservoir bookkeeping.
    reservoir_path = plugin_root / "state" / "reservoir.json"
    rstate = read_json(reservoir_path, default={"n_seen": 0, "reservoir": []})
    n_seen = int(rstate.get("n_seen", 0)) + 1
    reservoir = list(rstate.get("reservoir", []))
    turn_record = {"turn": turn_idx, "score": score, "tool": tool_name}
    try:
        reservoir = update_reservoir(reservoir, turn_record, n_seen)
    except Exception:
        pass
    atomic_write_json(reservoir_path, {"n_seen": n_seen, "reservoir": reservoir})

    # D2 HMM observation log.
    states_path = plugin_root / "state" / "states.jsonl"
    topic = "on_task" if score >= 0.7 else ("sidequest" if score >= 0.4 else "lost")
    append_jsonl(states_path, {"turn": turn_idx, "tool": tool_name, "topic": topic, "score": score})

    # Run HMM over the recent tail of observations (bounded).
    observations: list[tuple[str, str]] = []
    try:
        with open(states_path, "r", encoding="utf-8") as fh:
            for line in fh.readlines()[-64:]:
                rec = json.loads(line)
                observations.append((str(rec.get("tool", "")), str(rec.get("topic", ""))))
    except Exception:
        pass

    hmm_states: list[str] = []
    try:
        if observations:
            hmm_states = infer_states(observations)
    except Exception:
        hmm_states = []

    # Decision: emit advisory only if score < threshold AND N is sufficient.
    sample_scores = [float(r.get("score", 1.0)) for r in reservoir]
    if len(sample_scores) < MIN_N_FOR_ADVISORY:
        return 0

    point, ci_low, ci_high, N = bootstrap_ci(sample_scores)

    if point >= DRIFT_THRESHOLD:
        return 0

    # Classify drift_kind from the tail of HMM states.
    tail = hmm_states[-5:] if hmm_states else []
    if tail.count("LOST") >= 3:
        drift_kind = "lost"
    elif tail.count("SIDEQUEST") >= 3:
        drift_kind = "side_quest"
    else:
        drift_kind = "refocus"

    publish_drift_detected(
        session_id=session_id,
        preservation_score=point,
        ci_low=ci_low,
        ci_high=ci_high,
        N=N,
        turn=turn_idx,
        drift_kind=drift_kind,
    )

    sys.stderr.write(
        f"[Djinn] drift: preservation={point:.2f} "
        f"(95% CI {ci_low:.2f}-{ci_high:.2f}, N={N}) "
        f"kind={drift_kind} anchor={anchor.get('intent_type','unknown')}\n"
    )
    return 0


if __name__ == "__main__":
    plugin_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent.parent
    sys.exit(main(plugin_root))
