# Djinn Architecture

Phase-1: architecture documentation lives in `docs/science/README.md` (formal derivations) and `CLAUDE.md` (agent contract). PDF generation via `generate.py` is scaffolded but NOT required for Phase-1 ship — the HTML artifacts are browser-viewable directly.

## Source-of-truth diagrams

Mermaid sources live in `docs/architecture/*.mmd`. These are NOT hand-edited — they're generated from `plugin.json` + `hooks.json` + SKILL frontmatter by `generate.py`.

- `highlevel.mmd` — the 6-sub-plugin lifecycle
- `dataflow.mmd` — state-file + event-bus flow
- `hooks.mmd` — the 4 hook bindings
- `lifecycle.mmd` — SessionStart → PostToolUse → PreCompact ordering

## Phase-2 TODO

- Port `generate.py` from schematic (requires dev-only puppeteer for PDF; HTML + mermaid is the Phase-1 surface).
- Dark-themed report PDF on release tags.
