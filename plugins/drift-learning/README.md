# drift-learning

*Part of [Djinn](../../README.md).*

Per-(intent-type × developer) drift-signature posterior via D5 Gauss Accumulation. PreCompact hook folds the just-completed session's statistics into the posterior with a 30-day EMA half-life, letting a "research" session earn a wider tolerated drift band than a "bugfix" session.

## What it does

- PreCompact: reads `plugins/drift-aligner/state/reservoir.json` + anchor, derives (intent_type, developer, session_length, mean_preservation), updates `state/posteriors.json` via D5 EMA, and appends a raw observation to `state/learnings.jsonl` for backtesting.

## Outputs

- `state/posteriors.json` — `{key: posterior_record}` keyed by `intent_type::developer`
- `state/learnings.jsonl` — one line per session (backtesting source)

## Engine

D5 Gauss Accumulation. α = 0.3 corresponds to ~30-day EMA half-life. Records `{median_preservation, sigma, p10_threshold, session_length_median, n_sessions}`.

## How the orchestrator uses it

The `orchestrator` Opus agent reads the posterior for the current session's (intent, developer) and uses `p10_threshold` as the advisory cutoff instead of the prior-free 0.7. When `n_sessions < 3`, falls back to 0.7 and notes this in the advisory.
