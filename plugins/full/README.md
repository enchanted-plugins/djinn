# djinn / full

Meta-plugin. One install pulls in every Djinn sub-plugin via dependency resolution.

```
/plugin install full@djinn
```

Dependencies:

- `intent-anchor` — SessionStart + UserPromptSubmit anchor capture (D1, D3)
- `drift-aligner` — PostToolUse per-turn alignment + advisory (D1, D2, D3)
- `compact-guard` — PreCompact anchor injection (D1)
- `utterance-rank` — /rank skill for PageRank analysis (D4)
- `drift-learning` — PreCompact Gauss Accumulation posterior (D5)
- `intent-reorient` — /reorient skill + Opus orchestrator

See [../../README.md](../../README.md) for the full Djinn contract.
