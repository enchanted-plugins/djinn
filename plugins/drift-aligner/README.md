# drift-aligner

*Part of [Djinn](../../README.md).*

Per-turn alignment of the running agent utterance against the anchored intent. Emits advisory to stderr when preservation drops, carrying the honest-numbers tuple `(value, ci_low, ci_high, N)`.

## What it does

- **PostToolUse hook** fires on every tool call. Extracts the utterance from `tool_input` + `tool_response`, computes D1 preservation_ratio against the anchor, updates the D3 reservoir, appends an HMM observation, and re-runs D2 forward-backward over the recent tail.
- Emits `djinn.drift.detected` when the bootstrap 95% CI point estimate drops below 0.7 AND N ≥ 5.

## Outputs

- `state/reservoir.json` — bounded-memory sample of turn-score records.
- `state/states.jsonl` — append-only HMM observation log.
- Published events: `djinn.drift.detected`.

## Engines owned

- **D1 Hunt-Szymanski LCS** — per-turn preservation score.
- **D2 Baum-Welch HMM** — task-boundary inference (ON_TASK / SIDEQUEST / LOST).
- **D3 Vitter reservoir** — bounded-memory sampling across long sessions.

## Agents

- `drift-aligner` (Haiku) — shape-check validator.
- `topic-tagger` (Sonnet) — gated topic-tagger for uncertain turns.
