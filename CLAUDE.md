# Djinn — Agent Contract

Audience: Claude. Djinn pins the original session intent, watches for long-horizon drift across `/compact`, and reasserts the goal when the agent diverges. Answers the question: *"Am I still working on what you asked?"*

## Shared behavioral modules

These apply to every skill in every plugin. Load once; do not re-derive.

- @shared/conduct/discipline.md — coding conduct: think-first, simplicity, surgical edits, goal-driven loops
- @shared/conduct/context.md — attention-budget hygiene, U-curve placement, checkpoint protocol
- @shared/conduct/verification.md — independent checks, baseline snapshots, dry-run for destructive ops
- @shared/conduct/delegation.md — subagent contracts, tool whitelisting, parallel vs. serial rules
- @shared/conduct/failure-modes.md — 14-code taxonomy for accumulated-learning logs
- @shared/conduct/tool-use.md — tool-choice hygiene, error payload contract, parallel-dispatch rules
- @shared/conduct/formatting.md — per-target format (XML/Markdown/minimal/few-shot), prefill + stop sequences
- @shared/conduct/skill-authoring.md — SKILL.md frontmatter discipline, discovery test
- @shared/conduct/hooks.md — advisory-only hooks, injection over denial, fail-open
- @shared/conduct/precedent.md — log self-observed failures to `state/precedent-log.md`; consult before risky steps
- @shared/conduct/tier-sizing.md — agent-tier budget allocation per task class
- @shared/conduct/web-fetch.md — external-URL-handling hygiene

When a module conflicts with a plugin-local instruction, the plugin wins — but log the override.

## Lifecycle

Djinn is hook-driven with two skill-invoked sub-plugins. Four hook bindings publish four events on the `djinn.*` namespace. Intent lives in out-of-context state (`plugins/intent-anchor/state/anchor.json`), not in repeated in-context reminders — that is how we survive the recall-valley failure that plagues LangChain-style memory buffers.

| Event / Skill | Sub-plugin | Role |
|---|---|---|
| SessionStart | `intent-anchor` | Capture first-turn intent; write `anchor.json`; publish `djinn.intent.captured` |
| UserPromptSubmit | `intent-anchor` | Refresh anchor when new constraints appear (LCS ratio < 0.5); publish `djinn.intent.refreshed` |
| PostToolUse | `drift-aligner` | Per-turn D1+D2+D3 alignment; stderr advisory + `djinn.drift.detected` when preservation < 0.7 and N ≥ 5 |
| PreCompact | `compact-guard` | Inject anchor as structural hint; publish `djinn.compact.intent-hint.injected` |
| PreCompact | `drift-learning` | Fold session statistics into (intent-type × developer) posterior via D5 Gauss Accumulation |
| `/rank` | `utterance-rank` | On-demand D4 PageRank over the session utterance DAG |
| `/reorient` | `intent-reorient` | Manual re-pin of the session anchor |

Matchers in `./plugins/<name>/hooks/hooks.json`. Agents in `./plugins/<name>/agents/`.

## Algorithms

D1 Hunt-Szymanski LCS · D2 Baum-Welch HMM · D3 Vitter Reservoir · D4 Brin-Page PageRank · D5 Gauss Accumulation. Derivations in `docs/science/README.md`. **Defining engine:** D1.

| ID | Name | Plugin | Algorithm | Reference |
|----|------|--------|-----------|-----------|
| D1 | Hunt-Szymanski LCS Alignment | intent-anchor + drift-aligner + compact-guard | LCS ratio over normalized tokens | Hunt and Szymanski (1977) |
| D2 | Baum-Welch HMM Task-Boundary Inference | drift-aligner | 3-state HMM (ON_TASK / SIDEQUEST / LOST), forward-backward + single-pass re-estimation | Baum and Welch (1970) |
| D3 | Vitter Reservoir Sampling | intent-anchor + drift-aligner | Algorithm R, k=32 | Vitter (1985) |
| D4 | PageRank Utterance-DAG Ranking | utterance-rank | Sparse power-iteration over file-touch DAG | Brin and Page (1998) |
| D5 | Gauss Accumulation — Intent-Type Drift Signature | drift-learning | EMA with 30-day half-life + sample-count tracking | Gauss (1809) |

## Behavioral contracts

Markers: **[H]** hook-enforced (deterministic) · **[A]** advisory (relies on your adherence).

1. **IMPORTANT — Honest-numbers contract** [H] Every advisory Djinn publishes carries `(preservation_score, ci_low, ci_high, N)`. Advisories without all four are rejected by the Haiku validator. A score without a bootstrap band and a sample count is not a measurement — it is a guess. Non-parametric bootstrap (1000 iterations, stdlib `random.choices`) over the D3 reservoir is the only source of the band.
2. **YOU MUST NOT repeat the anchor in-context** [A] Intent lives in `state/anchor.json`, not in reinjected prompt text. The only structural reinjection point is PreCompact. Mid-context repetition lives in the recall valley (Liu et al. "Lost in the Middle", NAACL 2024) and buys zero recall. If you find yourself tempted to echo the anchor into a system message, stop.
3. **YOU MUST NOT ask the agent** [A] Djinn does NOT solicit the agent's own opinion on whether it has drifted. A drifted agent self-reports as on-task (Shinn et al., Reflexion 2023). Djinn measures with deterministic compute (D1 LCS + D2 HMM + D4 PageRank + D5 EMA) and reports; the agent's self-report is not in the signal path.

## State paths

| State file | Owner | Purpose |
|---|---|---|
| `plugins/intent-anchor/state/anchor.json` | intent-anchor | Session-intent anchor (captured once, refreshed on new constraints) |
| `plugins/drift-aligner/state/reservoir.json` | drift-aligner | Vitter reservoir of turn-score records (k=32) |
| `plugins/drift-aligner/state/states.jsonl` | drift-aligner | Append-only HMM observation log |
| `plugins/drift-learning/state/posteriors.json` | drift-learning | Per-(intent-type × developer) drift-signature posterior |
| `plugins/drift-learning/state/learnings.jsonl` | drift-learning | Per-session append-only summary log (backtesting source) |
| `plugins/utterance-rank/state/last-rank.json` | utterance-rank | Most recent /rank output |

## Agent tiers

| Tier | Model | Agent | Used for |
|---|---|---|---|
| Orchestrator | Opus | `orchestrator` | Tipping-judgment: compose D1 + D2 + D4 + D5 into a drift verdict |
| Executor | Sonnet | `topic-tagger` | Gated semantic topic labeling when D1 < 0.7 |
| Validator | Haiku | `aligner` | Per-turn deterministic shape-check — LCS + reservoir bookkeeping |

Respect the tiering. Routing a Haiku validation task to Opus burns budget and breaks the cost contract.

## Anti-patterns

- **Echoing the anchor as a mid-context reminder.** Lives in the recall valley; buys nothing. Counter: anchor is out-of-context state, reinjected only at PreCompact.
- **Summary-based intent preservation.** Lossy by construction; detail-specific intent survives the summary but rarely survives many summaries. Counter: D1 operates on the ORIGINAL anchor tokens, never a summary.
- **Retrieving "similar" turns.** Semantic similarity ≠ intent preservation. Two drifted agents can mutually retrieve each other's drift as "relevant context". Counter: D4 ranks by DEMONSTRATED influence on output (file-touch overlap), not similarity.
- **Self-critique loops on drift.** A drifted agent confidently self-reports as on-task. Counter: Djinn never asks the agent; deterministic compute only.
- **Inflating advisories without N.** A preservation score without sample count is a guess. Counter: honest-numbers contract enforced by the Haiku validator; `orchestrator` returns `insufficient_data` when N < 5.
- **Collapsing Djinn with Emu.** Emu owns A1 Markov on tool patterns (token-level drift); Djinn owns D1 LCS on goal-tokens (semantic intent drift). Orthogonal signals — do not merge.

---

## Brand invariants (survive unchanged into every sibling)

1. **Zero external runtime deps.** Hooks: bash + jq only. Scripts: Python 3.8+ stdlib only. No npm/pip/cargo at runtime.
2. **Managed agent tiers.** Opus = orchestrator/judgment. Sonnet = executor/loops. Haiku = validator/format.
3. **Named formal algorithm per engine.** ID prefix letter + number + Author-Year citation in docstring.
4. **Emu-style marketplace.** Each sub-plugin ships `.claude-plugin/plugin.json` + `{agents,commands,hooks,skills,state}/` + `README.md`.
5. **Dark-themed PDF report.** Produced by `docs/architecture/generate.py` on final release.
6. **Gauss Accumulation learning.** Per-session learnings at `plugins/drift-learning/state/learnings.jsonl`; posteriors at `plugins/drift-learning/state/posteriors.json`.
7. **enchanted-mcp event bus.** Inter-plugin coordination via published/subscribed events namespaced `djinn.<event>`.
8. **Diagrams from source of truth.** `docs/architecture/generate.py` reads `plugin.json` + `hooks.json` + `SKILL.md` frontmatter → writes mermaid diagrams.

Events this plugin publishes: `djinn.intent.captured`, `djinn.drift.detected`, `djinn.compact.intent-hint.injected`, `djinn.intent.refreshed`
Events this plugin subscribes to (optional): `emu.checkpoint.saved`, `crow.change.classified`
