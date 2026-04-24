# compact-guard

*Part of [Djinn](../../README.md).*

PreCompact hook that injects the captured intent anchor as a structural hint **before** the compaction model runs. Survival of the original goal is structurally guaranteed by the hook lifecycle — not left to the compactor's recency bias.

## What it does

- Reads `plugins/intent-anchor/state/anchor.json` and any accumulated refresh-deltas.
- Prints a hint block to stdout that the Claude Code PreCompact protocol threads into the compacted summary.
- Publishes `djinn.compact.intent-hint.injected` with the session_id, hint text, and pre-compact turn count.

## Engine

D1 Hunt-Szymanski LCS — survival-check only. The heavy lifting happens in drift-aligner; compact-guard's job is to ensure the anchor crosses the compaction boundary.
