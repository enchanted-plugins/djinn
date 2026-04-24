# intent-reorient

*Part of [Djinn](../../README.md).*

Manual re-pin of the session intent anchor. Hosts the Opus `orchestrator` agent that composes D1 + D2 + D4 + D5 signals into drift verdicts.

## Skills

### `/reorient`

Developer-facing override when the captured anchor no longer reflects the current task. Archives the old anchor, writes a fresh one, resets the D3 reservoir, and publishes `djinn.intent.captured` for the new intent. Reports the alignment delta between old and new anchors.

## Agents

### `orchestrator` (Opus)

Tipping-judgment over the full Djinn signal stack. Invoked when drift-aligner stderr advisories repeat 3+ turns, when the developer asks "am I still on task?", or as the go/no-go gate before `/reorient` fires. Returns:

```
{
  "verdict": "tolerable_side_quest | real_drift | refocus_moment | insufficient_data | no_anchor",
  "advisory": "one-sentence action the developer can take",
  "composite_score": float,
  "ci_low": float, "ci_high": float, "N": int
}
```

Honest-numbers contract: when N < 5, returns `insufficient_data` — never fabricates a band.
