// Render LaTeX equations to self-contained SVGs using MathJax.
//
// GitHub's mobile app renders images but not $$...$$ math. Every equation in
// README.md and docs/science/README.md is pre-rendered here and referenced as
// an <img>. Re-run this script after editing any equation.
//
// Usage:
//   node docs/assets/render-math.js

const fs = require("fs");
const path = require("path");

const MJ_PATH = path.join(__dirname, "node_modules", "mathjax-full");
require(path.join(MJ_PATH, "js", "util", "asyncLoad", "node.js"));

const { mathjax } = require(path.join(MJ_PATH, "js", "mathjax.js"));
const { TeX } = require(path.join(MJ_PATH, "js", "input", "tex.js"));
const { SVG } = require(path.join(MJ_PATH, "js", "output", "svg.js"));
const { liteAdaptor } = require(path.join(MJ_PATH, "js", "adaptors", "liteAdaptor.js"));
const { RegisterHTMLHandler } = require(path.join(MJ_PATH, "js", "handlers", "html.js"));
const { AllPackages } = require(path.join(MJ_PATH, "js", "input", "tex", "AllPackages.js"));

const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);

const tex = new TeX({ packages: AllPackages });
const svg = new SVG({ fontCache: "none" });
const html = mathjax.document("", { InputJax: tex, OutputJax: svg });

const FG = "#e6edf3";
const OUT = path.join(__dirname, "math");
fs.mkdirSync(OUT, { recursive: true });

// [filename, TeX source]
// Djinn's 5 engines (D1-D5) + honest-numbers contract.
const EQUATIONS = [
  // D1 Hunt-Szymanski LCS Alignment
  ["d1-ratio",
   String.raw`\text{ratio}(A, C) = \dfrac{2 \cdot |\text{LCS}(A, C)|}{|A| + |C|} \;\in\; [0, 1]`],
  ["d1-decision",
   String.raw`\text{state}(t) = \begin{cases} \text{ON\_TASK} & \text{ratio}_t \geq 0.7 \\ \text{SIDEQUEST} & 0.4 \leq \text{ratio}_t < 0.7 \\ \text{LOST} & \text{ratio}_t < 0.4 \end{cases}`],

  // D2 Baum-Welch HMM Task-Boundary Inference
  ["d2-forward",
   String.raw`\alpha_t(j) = \left[\sum_{i=1}^{N} \alpha_{t-1}(i) \cdot a_{ij}\right] \cdot b_j(o_t)`],
  ["d2-gamma",
   String.raw`\gamma_t(i) = \dfrac{\alpha_t(i) \cdot \beta_t(i)}{\sum_{j=1}^{N} \alpha_t(j) \cdot \beta_t(j)}`],
  ["d2-label",
   String.raw`\hat{s}_t = \arg\max_{i \in \{\text{ON\_TASK},\, \text{SIDEQUEST},\, \text{LOST}\}} \gamma_t(i)`],

  // D3 Vitter Reservoir Sampling (Algorithm R)
  ["d3-reservoir",
   String.raw`\Pr\bigl[x_i \in R_n\bigr] = \dfrac{k}{n} \qquad \forall\, i \in \{1,\,\ldots,\,n\},\; n \geq k`],
  ["d3-step",
   String.raw`R_{n+1} = \begin{cases} R_n \cup \{x_{n+1}\} & n < k \\ R_n[j \leftarrow x_{n+1}] & j \sim U(0, n],\; j < k \\ R_n & \text{otherwise} \end{cases}`],

  // D4 PageRank Utterance-DAG Ranking
  ["d4-pagerank",
   String.raw`\text{PR}(p) = \dfrac{1 - d}{N} + d \cdot \sum_{q \to p} \dfrac{\text{PR}(q)}{L(q)}, \qquad d = 0.85`],
  ["d4-edges",
   String.raw`(u, v) \in E \;\iff\; \text{files}(u) \cap \text{files}(v) \neq \emptyset`],

  // D5 Gauss Accumulation (Intent-Type Drift Signature)
  ["d5-ema-mean",
   String.raw`\mu_{n+1} = (1 - \alpha) \cdot \mu_n + \alpha \cdot \bar{y}_{\text{session}}, \qquad \alpha = 0.3`],
  ["d5-ema-variance",
   String.raw`\sigma^2_{n+1} = (1 - \alpha) \cdot \sigma^2_n + \alpha \cdot (\bar{y}_{\text{session}} - \mu_{n+1})^2`],
  ["d5-p10",
   String.raw`\text{p10}_{\text{threshold}} = \mu - 1.2816 \cdot \sigma`],

  // Honest-numbers advisory contract
  ["honest-tuple",
   String.raw`\text{advisory} = \bigl(\text{value},\, \text{ci}_{\text{low}},\, \text{ci}_{\text{high}},\, N\bigr), \qquad N \geq 5`],
  ["honest-bootstrap",
   String.raw`\text{ci}_{95\%} = \bigl[\, Q_{0.025}(\{\bar{y}^{(b)}\}_{b=1}^{B}),\; Q_{0.975}(\{\bar{y}^{(b)}\}_{b=1}^{B}) \,\bigr], \qquad B = 1000`],
];

function render(name, source) {
  const node = html.convert(source, { display: true, em: 16, ex: 8, containerWidth: 1200 });
  let svgStr = adaptor.innerHTML(node);
  // Force visible ink. MathJax uses currentColor by default, which on mobile
  // GitHub (image opened in isolation) falls back to black — invisible on our
  // dark page. Bake a fixed fill so the SVG is self-contained.
  svgStr = svgStr.replace(/currentColor/g, FG);
  svgStr = `<?xml version="1.0" encoding="UTF-8"?>\n` + svgStr;
  const outPath = path.join(OUT, `${name}.svg`);
  fs.writeFileSync(outPath, svgStr, "utf8");
  console.log(`  docs/assets/math/${name}.svg`);
}

console.log(`Rendering ${EQUATIONS.length} equations...`);
for (const [name, src] of EQUATIONS) {
  try {
    render(name, src);
  } catch (err) {
    console.error(`FAILED: ${name}\n  ${err.message}`);
    process.exitCode = 1;
  }
}
console.log("Done.");
