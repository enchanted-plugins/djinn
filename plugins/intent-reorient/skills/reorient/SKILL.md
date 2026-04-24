---
name: reorient
description: Manual re-pin of the session intent anchor. Use when the developer explicitly runs /reorient, says the original goal no longer applies, or pivots the session to a fundamentally different task. Do not use for constraint refinements (the intent-anchor UserPromptSubmit hook handles those automatically) or for per-turn alignment (that is drift-aligner).
model: opus
tools: [Read, Write, Grep, Glob]
---

# reorient

Manual override of the anchored session intent. Writes a fresh anchor.json, archives the previous one, and resets the reservoir so the new intent gets a clean drift track.

## Preconditions

- A prior anchor exists at `plugins/intent-anchor/state/anchor.json` (else there is nothing to override).

## Inputs

- `new_intent`: The new goal statement from the developer. Required; no default.

## Steps

1. **Archive the old anchor.** Move the current `anchor.json` to `state/archive/anchor-<timestamp>.json`.
2. **Compute alignment delta.** Run `engines.c1_lcs.preservation_ratio` between the old and new anchor texts. Report the drop — the developer should see how far the pivot is.
3. **Write new anchor.** Use `shared.scripts.anchor.capture_anchor` with the new text, atomic write.
4. **Reset reservoir.** Archive `plugins/drift-aligner/state/reservoir.json` and start fresh — the new intent gets its own N.
5. **Publish `djinn.intent.captured`.** Fresh session anchor; downstream consumers treat this as a new-session event.
6. **Success criterion:** New anchor is written, old is archived, reservoir reset. Return the alignment delta to the developer.

## Outputs

- Fresh `plugins/intent-anchor/state/anchor.json`.
- Archived old anchor under `state/archive/`.
- Stdout: `{old_hash, new_hash, alignment_delta}` for the developer.

## Tier justification

This is a judgment call — the developer is pivoting, and the orchestrator has to decide whether the new intent is distinct enough to warrant a reset or is really just a constraint refresh. Opus tier per `../../../CLAUDE.md` § Agent tiers.

## Failure modes

- **F04 Task drift.** The developer may request a "reorient" that is actually just a constraint addition — in that case, refuse and point at the UserPromptSubmit refresh path. Log F04 to `state/precedent-log.md`.
- **F11 Reward hacking.** Do not rewrite the anchor silently to make future drift scores look better. The old anchor must be archived verbatim.
