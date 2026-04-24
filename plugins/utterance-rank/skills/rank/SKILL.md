---
name: rank
description: Ranks session utterances by their demonstrated influence on the final output via D4 PageRank over the utterance-to-artifact DAG. Use when the developer runs /rank, asks which turns actually mattered, or wants to audit a long session for filler. Do not use for per-turn drift detection (that is drift-aligner) or for re-pinning intent (that is /reorient in intent-reorient).
model: sonnet
tools: [Read, Grep, Glob]
---

# rank

On-demand PageRank analysis over the session's utterance DAG. Noise-resistant by construction — edges are file-touch overlaps, not semantic similarity.

## Preconditions

- An anchor exists at `plugins/intent-anchor/state/anchor.json`.
- A reservoir exists at `plugins/drift-aligner/state/reservoir.json` (populated by PostToolUse).

## Inputs

None — operates on session state.

## Steps

1. **Load reservoir.** Read `plugins/drift-aligner/state/reservoir.json`.
2. **Build DAG.** For each turn, nodes are utterances; edges are shared file paths mentioned in `tool_input`/`tool_response`. Persisted utterances (files actually written) become sinks.
3. **Run PageRank.** `engines.c4_pagerank.pagerank(dag, damping=0.85, eps=1e-6)`.
4. **Return ranked list.** Top-10 utterances with their scores. Bottom-N flagged as "conversational noise".
5. **Success criterion:** Output lists the top utterances with scores summing inside [0.9, 1.1] (float tolerance).

## Outputs

- `plugins/utterance-rank/state/last-rank.json` — full ranking with timestamp.
- Stdout summary for the developer: top-5 by rank plus anchor alignment score for each.

## Handoff

No downstream skill. The output is read by the developer directly.

## Failure modes

- **F02 Fabrication.** Never invent utterances not in the reservoir. Every ranked item must trace back to a turn record.
- **F13 Distractor pollution.** Do not rank by semantic similarity — that is the LangChain retrieval failure this engine explicitly avoids.
