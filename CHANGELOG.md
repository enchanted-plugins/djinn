# Changelog

All notable changes to `djinn` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-04-24 — initial scaffold

### Added

- Five engines with Author-Year citations:
  - **D1** Hunt-Szymanski LCS Alignment (Hunt and Szymanski 1977)
  - **D2** Baum-Welch HMM Task-Boundary Inference (Baum and Welch 1970)
  - **D3** Vitter Reservoir Sampling — Algorithm R (Vitter 1985)
  - **D4** PageRank Utterance-DAG Ranking (Brin and Page 1998)
  - **D5** Gauss Accumulation — Intent-Type Drift Signature (Gauss 1809)
- Six sub-plugins plus `full` meta-plugin: `intent-anchor`, `drift-aligner`, `compact-guard`, `utterance-rank`, `drift-learning`, `intent-reorient`, `full`.
- Four hook bindings: `SessionStart` + `UserPromptSubmit` (intent-anchor), `PostToolUse` (drift-aligner), `PreCompact` (compact-guard + drift-learning).
- Three tier-correct agents: `aligner` (Haiku), `topic-tagger` (Sonnet), `orchestrator` (Opus).
- Four published events on the `djinn.*` namespace: `intent.captured`, `drift.detected`, `compact.intent-hint.injected`, `intent.refreshed`.
- Honest-numbers advisory contract: `(preservation_score, ci_low, ci_high, N)` non-parametric bootstrap 95% CI, Haiku-validator enforced.
- Cross-session Gauss Accumulation: per-(intent-type × developer) drift-signature posterior with 30-day EMA half-life.
- Ten shared behavioral modules inherited verbatim from schematic.
- 22 stdlib-only unit tests (engines + hooks shape + plugin.json + subagent guard).

[Unreleased]: https://github.com/enchanted-plugins/djinn/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/enchanted-plugins/djinn/releases/tag/v0.1.0
