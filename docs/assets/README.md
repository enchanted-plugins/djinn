# docs/assets — rendered diagrams & equations

These SVGs are **pre-rendered** so GitHub's mobile app (which renders neither
` ```mermaid ` blocks nor `$$...$$` math) shows them correctly. `README.md` and
`docs/science/README.md` reference the files here as `<img>`.

## Files

| File | Source | Regenerate |
|------|--------|-----------|
| `pipeline.svg` | `pipeline.mmd` | `npx -y @mermaid-js/mermaid-cli -i pipeline.mmd -o pipeline.svg -c mermaid.config.json -p puppeteer.config.json -b "#0a1628" -w 1800 && node apply-blueprint.js pipeline.svg` |
| `lifecycle.svg` | `lifecycle.mmd` | `npx -y @mermaid-js/mermaid-cli -i lifecycle.mmd -o lifecycle.svg -c mermaid.config.json -p puppeteer.config.json -b "#0a1628" -w 1800 && node apply-blueprint.js lifecycle.svg` |
| `state-flow.svg` | `state-flow.mmd` | `npx -y @mermaid-js/mermaid-cli -i state-flow.mmd -o state-flow.svg -c mermaid.config.json -p puppeteer.config.json -b "#0a1628" -w 1800 && node apply-blueprint.js state-flow.svg` |
| `math/*.svg` | `render-math.js` | `npm install --prefix . mathjax-full && node render-math.js` |

The `apply-blueprint.js` step overlays an engineering-blueprint grid (navy `#0a1628` paper, `#1e3a5f` major lines / `#16304f` minor lines) onto the rendered diagram so it reads as a CAD drawing rather than a neutral dark card. Matches the look of the sibling repos (emu, wixie, crow, hydra, sylph, lich, pech).

Run the commands from `docs/assets/` (paths are relative). The toolchain
(`node_modules/`, `package-lock.json`) is gitignored; only the rendered SVGs
and source `.mmd` / `.js` files are committed.

## Equations rendered

The 14 equations cover every Djinn engine plus the honest-numbers contract:

| ID | File | Coverage |
|----|------|----------|
| D1 | `math/d1-ratio.svg`, `math/d1-decision.svg` | Hunt-Szymanski LCS ratio + ON_TASK / SIDEQUEST / LOST decision rule |
| D2 | `math/d2-forward.svg`, `math/d2-gamma.svg`, `math/d2-label.svg` | Baum-Welch forward recursion + posterior + state label |
| D3 | `math/d3-reservoir.svg`, `math/d3-step.svg` | Vitter Algorithm R uniform-sample invariant + step rule |
| D4 | `math/d4-pagerank.svg`, `math/d4-edges.svg` | PageRank stationary + file-touch DAG edges |
| D5 | `math/d5-ema-mean.svg`, `math/d5-ema-variance.svg`, `math/d5-p10.svg` | EMA mean + variance + p10 threshold |
| Contract | `math/honest-tuple.svg`, `math/honest-bootstrap.svg` | Honest-numbers tuple shape + bootstrap percentile interval |

## Relationship to docs/architecture/

Two diagram surfaces exist in this repo:

- **`docs/assets/{pipeline,lifecycle,state-flow}.svg`** — hand-authored blueprint diagrams referenced by the root `README.md`. Shape is designed for narrative clarity (the README reader).
- **`docs/architecture/{highlevel,hooks,lifecycle,dataflow}.mmd`** — auto-generated from `plugins/*/.claude-plugin/plugin.json` + `hooks/hooks.json` + `SKILL.md` frontmatter by `docs/architecture/generate.py`. Shape follows the code; regenerates on every source change.

Both are blueprint-styled but serve different audiences. The `docs/assets/` set is for the GitHub landing page; the `docs/architecture/` set is for developers browsing the code.
