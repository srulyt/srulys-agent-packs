/**
 * B1 regression (structural, no LLM): the pdf->png stage must prefer
 * `pypdfium2` (permissively licensed) over poppler, and the full
 * generate_deck.py -> render_pptx.py pipeline must produce per-slide PNGs at
 * 150 DPI.
 *
 * Ported from the legacy pytest `test_smoke_pypdfium2_render_path.py` "tooling"
 * smoke test. The preferred-engine wiring is a pure source read (always runs).
 * The pipeline guard drives the pack's own Python scripts and degrades to a
 * pass with a note when Python, the pack's rendering deps, or a LibreOffice
 * (pptx->pdf) engine are unavailable — the pack's verify-or-block policy owns
 * that case; here we only assert wiring.
 */

import { spawnSync } from "node:child_process";
import { mkdtempSync, writeFileSync, existsSync, statSync, readdirSync } from "node:fs";
import { tmpdir } from "node:os";
import * as path from "node:path";
import { Eval } from "evalpilot";

const PACK = "agent-packs/story-telling-agent/.github/skills";
const GEN = `${PACK}/pptx-engine/scripts/generate_deck.py`;
const RENDER = `${PACK}/pptx-visual-qa/scripts/render_pptx.py`;
const SYSTEMS = `${PACK}/slide-design-systems/references/systems`;

type Ctx = { root: string; read(rel: string): string | null };
type Result = boolean | [boolean, string];

function pythonPrefix(): string[] | null {
  for (const c of [["python"], ["python3"], ["py", "-3"]]) {
    const r = spawnSync(c[0]!, [...c.slice(1), "--version"], { encoding: "utf-8" });
    if (!r.error && r.status === 0) return c;
  }
  return null;
}

function depsMissing(stderr: string): boolean {
  return /ModuleNotFoundError|ImportError|No module named/i.test(stderr || "");
}

function systemTokens(ctx: Ctx, name: string): Record<string, unknown> {
  const md = ctx.read(`${SYSTEMS}/${name}.md`);
  if (md === null) throw new Error(`missing system file ${name}.md`);
  const m = /```json\s*(\{[\s\S]*?\})\s*```/.exec(md);
  if (!m) throw new Error(`${name}.md has no JSON token block`);
  return JSON.parse(m[1]!);
}

export default new Eval("story-telling-pypdfium2-render-path", {
  kind: "none",
  tags: ["pack", "structural", "tooling"],
})
  .summarize("The pdf->png stage prefers pypdfium2 and renders per-slide PNGs at 150 DPI.")
  .describe(
    "Source guard: pypdfium2 is the first pdf_to_pngs branch and PyMuPDF/fitz is " +
      "never used. Pipeline guard: generate + render produce 150-DPI PNGs via the " +
      "preferred engine when the host has the pack's rendering stack.",
  )
  .check("pypdfium2 is the preferred pdf->png engine", (ctx: Ctx): Result => {
    const src = ctx.read(RENDER);
    if (src === null) return [false, "missing render_pptx.py"];
    if (!src.includes("import pypdfium2")) {
      return [false, "render_pptx.py must import pypdfium2"];
    }
    const afterDef = src.split("def pdf_to_pngs")[1] ?? "";
    const beforePoppler = afterDef.split("pdftoppm")[0] ?? "";
    if (!beforePoppler.includes("pypdfium2")) {
      return [false, "pypdfium2 branch must come BEFORE the pdftoppm/poppler fallback"];
    }
    const scrubbed = src
      .replace("PyMuPDF / `fitz` is deliberately NOT used", "")
      .replace("PyMuPDF/`fitz` is intentionally excluded", "");
    if (src.includes("import fitz") || scrubbed.includes("PyMuPDF")) {
      return [false, "PyMuPDF/fitz (AGPL) must not be used"];
    }
    return true;
  })
  .check("pipeline renders PNGs via pypdfium2", (ctx: Ctx): Result => {
    const py = pythonPrefix();
    if (!py) return [true, "skipped: no Python interpreter on host"];

    const tmp = mkdtempSync(path.join(tmpdir(), "st-render-"));
    const spec = {
      design_system_tokens: systemTokens(ctx, "signal-dark"),
      slides: [
        {
          index: 0, style: "styled", style_recipe: "stat_grid_3up",
          title: "Platform at scale",
          stats: [
            { value: "99.99%", label: "Uptime", delta: "+0.04" },
            { value: "42ms", label: "p99", delta: "-11" },
            { value: "3.2B", label: "Events/day", delta: "+0.9" },
          ],
        },
        {
          index: 1, style: "styled", style_recipe: "editorial_2col_6040",
          title: "Why this architecture",
          standfirst: "One control plane, many data planes.",
          points: ["Region-local failure domains", "Zero-downtime evolution"],
          aside: { kicker: "Tradeoff", body: "Eventual at edge, strong at core." },
        },
      ],
    };
    const specPath = path.join(tmp, "spec.json");
    const outPptx = path.join(tmp, "deck.pptx");
    const renderDir = path.join(tmp, "render");
    writeFileSync(specPath, JSON.stringify(spec), "utf-8");

    const gen = spawnSync(
      py[0]!,
      [...py.slice(1), path.join(ctx.root, GEN), "--spec", specPath, "--out", outPptx],
      { encoding: "utf-8", timeout: 180_000, input: "" },
    );
    if (gen.status !== 0) {
      if (depsMissing(gen.stderr)) {
        return [true, "skipped: pack rendering deps (python-pptx) unavailable"];
      }
      return [false, `generate_deck failed: ${gen.stderr}\n${gen.stdout}`];
    }
    if (!(existsSync(outPptx) && statSync(outPptx).size > 0)) {
      return [false, "output.pptx missing/empty"];
    }

    const rnd = spawnSync(
      py[0]!,
      [
        ...py.slice(1), path.join(ctx.root, RENDER),
        "--pptx", outPptx, "--out", renderDir, "--dpi", "150",
      ],
      { encoding: "utf-8", timeout: 240_000, input: "" },
    );
    if (rnd.status !== 0) {
      if (depsMissing(rnd.stderr)) return [true, "skipped: pack render deps unavailable"];
      return [false, `render_pptx failed: ${rnd.stderr}\n${rnd.stdout}`];
    }
    const manifestRel = path.relative(ctx.root, path.join(renderDir, "manifest.json")).replace(/\\/g, "/");
    const manifest = JSON.parse(ctx.read(manifestRel)!);

    if (manifest.dpi !== 150) return [false, "aesthetic pass must render at 150 DPI"];
    if ((manifest.png_engines_preference ?? [])[0] !== "pypdfium2") {
      return [false, "pypdfium2 must be first in the png-engine preference order"];
    }
    if (!manifest.render_engine) {
      return [true, "skipped: no LibreOffice (pptx->pdf) engine on host; verify-or-block owns this case"];
    }
    if (manifest.png_engine !== "pypdfium2") {
      return [false, `PNG stage should use pypdfium2; got ${JSON.stringify(manifest.png_engine)}`];
    }
    if (manifest.render_unverified !== false) {
      return [false, "full pipeline should verify"];
    }
    const pngs = readdirSync(renderDir).filter((f) => /^slide-.*\.png$/.test(f));
    if (pngs.length !== 2) return [false, `expected 2 slide PNGs; got ${pngs.length}`];
    for (const p of pngs) {
      if (statSync(path.join(renderDir, p)).size <= 0) return [false, `empty PNG: ${p}`];
    }
    return true;
  })
  .build();
