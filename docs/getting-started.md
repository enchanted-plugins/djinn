# Getting started with Djinn

A guided first session. Assumes Claude Code is installed and authenticated.

## 1. Install

In Claude Code:

```
/plugin marketplace add enchanted-plugins/djinn
/plugin install full@djinn
```

This installs all six sub-plugins plus the `full` meta-plugin via dependency resolution. Verify:

```
/plugin list
```

You should see: `full`, `intent-anchor`, `drift-aligner`, `compact-guard`, `utterance-rank`, `drift-learning`, `intent-reorient`.

## 2. Start a session with a clear first-turn goal

The first user prompt becomes the session anchor. Say what you want, as specifically as you would say it to a colleague who hasn't seen the codebase yet:

> *"Add dark-mode support to the settings page with a11y keyboard-trap tests."*

`intent-anchor` captures this into `plugins/intent-anchor/state/anchor.json`, hashes it, classifies the intent type (here: `feature`), and publishes `djinn.intent.captured` on the event bus.

## 3. Work normally

Every `PostToolUse` runs the drift-aligner silently. It:

- Computes D1 Hunt-Szymanski LCS between the anchor and the turn's utterance.
- Updates the D3 Vitter reservoir (bounded sample of 32 turn-score records).
- Appends a D2 HMM observation (`tool`, `topic`, `score`).

When the bootstrap 95% CI point estimate drops below 0.7 AND reservoir N ≥ 5, stderr emits:

```
[Djinn] drift: preservation=0.48 (95% CI 0.41-0.55, N=32) kind=side_quest anchor=feature
```

**That is the signal.** It is advisory — no tool call is blocked.

## 4. Let `/compact` fire when it does

When Claude Code compacts your session, `compact-guard` injects the anchor as a structural hint **before** the compaction model sees the context. The first-turn goal survives the compaction regardless of recency bias.

Simultaneously, `drift-learning` folds the session's summary statistics into the per-(intent-type × developer) posterior — future "feature" sessions from you will be calibrated against your own drift envelope.

## 5. Audit on demand

```
/rank
```

Runs D4 PageRank over the session's utterance DAG and returns the top-5 utterances that demonstrably influenced output (edges are file-touch overlaps, not semantic similarity).

## 6. Re-pin if you pivot

If you genuinely change direction mid-session:

```
/reorient "now switching to fixing the broken migration on the users table"
```

The `orchestrator` Opus agent archives the old anchor, writes a fresh one, and resets the reservoir. The alignment delta between old and new anchors is reported so you can see how far the pivot is.

## What to expect per session

- Anchor captured exactly once per session (unless you `/reorient`).
- 32-sample reservoir maintained across the whole session.
- stderr advisory fires when preservation drops, with full `(score, ci_low, ci_high, N)` tuple.
- Four events on the `djinn.*` namespace; a Phase-1 file-tail fallback persists them under the enchanted-mcp bus path.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for install/runtime issues. Common first-session quirks:

- **No anchor captured.** Either the SessionStart hook didn't fire (harness configuration) or the initial prompt was empty — the UserPromptSubmit hook will seed the anchor on your first prompt as a fallback.
- **No advisories firing.** Reservoir needs N ≥ 5 before the honest-numbers contract allows an advisory. First few turns are silent by design.
- **`/compact` happened but anchor didn't persist across.** Check `plugins/intent-anchor/state/anchor.json` still exists — compact-guard injects into the compaction hint but does not delete the anchor file.
