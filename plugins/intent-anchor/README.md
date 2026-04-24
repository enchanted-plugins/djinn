# intent-anchor

*Part of [Djinn](../../README.md) — the anchor-bound intent-preservation plugin.*

Captures the first-turn session intent and refreshes it when the developer adds constraints. This is the out-of-context state that survives `/compact`.

## What it does

- **SessionStart hook** writes `state/anchor.json` once per session with the first user prompt, its sha1 hash, intent type (feature/bugfix/refactor/research/docs), and capture timestamp.
- **UserPromptSubmit hook** compares each new prompt against the anchor via D1 LCS. If preservation < 0.5, appends a `refresh_delta` to the anchor record.
- Publishes `djinn.intent.captured` on first capture; `djinn.intent.refreshed` on constraint deltas.

## Inputs

Hook-driven. No slash command.

## Outputs

- `state/anchor.json` — the session anchor record.
- Published events: `djinn.intent.captured`, `djinn.intent.refreshed`.

## Engines owned

- **D1 Hunt-Szymanski LCS** (Hunt and Szymanski 1977) — ratio test for constraint-refresh eligibility.
- **D3 Vitter reservoir** (Vitter 1985) — seeded here; populated by drift-aligner.
