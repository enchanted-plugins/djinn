# Frequently asked questions

Template version — cloned siblings replace `Djinn` / `djinn` / `Am I still working on what you asked?` with real values and swap the repo-specific entries at the bottom.

## What's the difference between Djinn and the other siblings?

Djinn answers *"Am I still working on what you asked?"*. Sibling plugins answer different questions in the same session (Wixie: prompt engineering; Emu: session health; Crow: change trust; Hydra: security surface; Sylph: git workflow). All are independent installs; none require the others. See [docs/ecosystem.md](ecosystem.md) for the full map.

## Do I need the other siblings to use Djinn?

No. Djinn is self-contained — install `full@djinn` and every command works standalone. The siblings compose if you install them, but nothing in Djinn depends on another repo being present.

## How do I report a bug vs. ask a question vs. disclose a security issue?

- **Security vulnerability** — private advisory, never a public issue. See [SECURITY.md](../SECURITY.md).
- **Reproducible bug** — a bug report issue with repro steps + exact versions.
- **Usage question or half-formed idea** — [Discussions](https://github.com/enchanted-plugins/djinn/discussions).

The [SUPPORT.md](../SUPPORT.md) page has the exact links for each.

## Is Djinn an official Anthropic product?

No. Djinn is an independent open-source plugin for [Claude Code](https://github.com/anthropics/claude-code) (Anthropic's CLI). It's published by [enchanted-plugins](https://github.com/enchanted-plugins) under the MIT license and is not affiliated with, endorsed by, or supported by Anthropic.

## Why doesn't Djinn just inject the anchor into every turn as a system-prompt reminder?

Because mid-context reminders live in the recall valley. Liu et al. ("Lost in the Middle", NAACL 2024) documented a ≥30% recall drop for middle-of-context tokens; repeating the anchor mid-session burns tokens without reliable preservation. The anchor lives in `state/anchor.json` (out-of-context state) and is structurally reinjected *only* at PreCompact — the one moment the compaction model is guaranteed to see it. See [docs/science/README.md § D1](science/README.md) for the failure-mode analysis.

## Can Djinn detect drift without the `drift-aligner` sub-plugin installed?

No — `drift-aligner` is the measurement surface. Without it, `intent-anchor` will still capture the anchor on SessionStart and `compact-guard` will still inject it at PreCompact, but no per-turn advisory fires and no reservoir accumulates. If you want intent preservation without per-turn cost, install only `intent-anchor@djinn` + `compact-guard@djinn` — survival-only mode, no advisories. The full pipeline lives under `full@djinn`.
