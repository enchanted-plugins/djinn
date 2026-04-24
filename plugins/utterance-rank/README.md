# utterance-rank

*Part of [Djinn](../../README.md).*

On-demand PageRank analysis (D4 Brin-Page 1998) over the session's utterance-to-artifact DAG. Ranks which agent utterances actually shaped the final output. Noise-resistant by construction — edges are file-touch overlaps, not semantic similarity, so a "similar-sounding" turn that never touched an artifact scores near the teleport floor.

## Invocation

```
/rank
```

Operates on session state; no arguments.

## Engine

D4 PageRank. Sparse power-iteration with damping = 0.85, eps = 1e-6, 100-iteration hard cap. Convergence typically at 20-50 iterations.

## Output

- `state/last-rank.json` — full ranking with timestamp
- Stdout summary of top-5 utterances with scores + bottom-N flagged as conversational noise
