/**
 * C5 + C11 regression (structural, no LLM): the aesthetic-craft rubric axis
 * must exist and be wired into the critic, and the categorical chart recipe
 * must consume `chart_palette` + apply number formatting.
 *
 * Ported from the legacy pytest `test_smoke_aesthetic_craft_and_charts.py`
 * "tooling" smoke test. Doc/source guards are pure reads (always run). The
 * chart-render and number-formatter guards shell out to the pack's own
 * render_chart.py; when Python or the pack's plotting deps are unavailable they
 * degrade to a pass with a note, never a hang.
 */

import { spawnSync } from "node:child_process";
import { mkdtempSync, writeFileSync, existsSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import * as path from "node:path";
import { Eval } from "@evalpilot/cli";

const PACK = "agent-packs/story-telling-agent/.github";
const RUBRIC = `${PACK}/skills/pptx-visual-qa/references/visual-rubric.md`;
const CRITIC = `${PACK}/agents/deck-critic.agent.md`;
const CHART = `${PACK}/skills/render-visual/scripts/render_chart.py`;
const RENDER = `${PACK}/skills/pptx-visual-qa/scripts/render_pptx.py`;

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

export default new Eval("story-telling-aesthetic-craft-and-charts", {
  kind: "none",
  tags: ["pack", "structural", "tooling"],
})
  .summarize("The aesthetic-craft rubric axis is wired into the critic and charts consume chart_palette.")
  .describe(
    "Doc/source guards for the aesthetic_craft axis, its critic wiring, and the " +
      "150-DPI default, plus bounded render_chart.py guards for categorical-bar " +
      "palette consumption and number formatting.",
  )
  .check("aesthetic_craft axis defined in the rubric", (ctx: Ctx): Result => {
    const text = ctx.read(RUBRIC);
    if (text === null) return [false, "missing visual-rubric.md"];
    if (!text.includes("aesthetic_craft")) return [false, "rubric missing aesthetic_craft axis"];
    if (!(text.includes("1\u20135") || text.includes("1-5") || text.includes("(1\u20135)"))) {
      return [false, "aesthetic_craft must be a 1-5 scale"];
    }
    if (!text.includes("aesthetic_craft >= 3")) return [false, "rubric must state the minimum passing bar"];
    if (!text.includes("aesthetic_craft <= 2")) return [false, "rubric must state the failing condition"];
    return true;
  })
  .check("critic applies aesthetic_craft and font concern", (ctx: Ctx): Result => {
    const text = ctx.read(CRITIC);
    if (text === null) return [false, "missing deck-critic.agent.md"];
    if (!text.includes("aesthetic_craft")) return [false, "deck-critic must score aesthetic_craft"];
    if (!text.includes("display_font_substituted")) {
      return [false, "deck-critic must surface display-font substitution as a CONCERN (B2)"];
    }
    return true;
  })
  .check("aesthetic render DPI default is 150", (ctx: Ctx): Result => {
    const text = ctx.read(RENDER);
    if (text === null) return [false, "missing render_pptx.py"];
    if (!text.includes("DEFAULT_DPI = 150")) return [false, "aesthetic pass must default to 150 DPI"];
    return true;
  })
  .check("categorical_bars consumes chart_palette", (ctx: Ctx): Result => {
    const py = pythonPrefix();
    if (!py) return [true, "skipped: no Python interpreter on host"];

    const tokens = {
      palette: {
        background_light: "#FAFAF7", background_dark: "#0B0B0C",
        primary_accent: "#E5482F", secondary_accent: "#0B0B0C",
        text_on_light: "#0B0B0C", text_on_dark: "#FAFAF7", text_secondary: "#6B6A66",
      },
      chart_palette: {
        focal: "#E5482F", muted: "#6B6A66", grid: "#D8D6CE",
        ramp: ["#E5482F", "#0B0B0C", "#6B6A66", "#B0341F", "#9C8E73", "#C9B8A0"],
      },
    };
    const spec = {
      labels: ["NA", "EMEA", "APAC", "LATAM", "MEA"],
      values: [12500, 9800, 15200, 4300, 2100],
      focal: "APAC", y_label: "Revenue", title: "Revenue by region",
    };
    const tmp = mkdtempSync(path.join(tmpdir(), "st-chart-"));
    const tokPath = path.join(tmp, "tok.json");
    const specPath = path.join(tmp, "spec.json");
    const outPng = path.join(tmp, "cat.png");
    writeFileSync(tokPath, JSON.stringify(tokens), "utf-8");
    writeFileSync(specPath, JSON.stringify(spec), "utf-8");

    const r = spawnSync(
      py[0]!,
      [
        ...py.slice(1), path.join(ctx.root, CHART),
        "--kind", "categorical_bars", "--spec", specPath, "--tokens", tokPath,
        "--out", outPng, "--on-light",
      ],
      { encoding: "utf-8", timeout: 180_000, input: "" },
    );
    if (r.status !== 0) {
      if (depsMissing(r.stderr)) return [true, "skipped: pack plotting deps (matplotlib) unavailable"];
      return [false, `categorical_bars render failed: ${r.stderr}\n${r.stdout}`];
    }
    if (!(existsSync(outPng) && statSync(outPng).size > 0)) {
      return [false, "chart PNG missing/empty"];
    }
    return true;
  })
  .check("_fmt_num applies thousands separators and units", (ctx: Ctx): Result => {
    const py = pythonPrefix();
    if (!py) return [true, "skipped: no Python interpreter on host"];

    const code =
      "import importlib.util,sys\n" +
      "spec=importlib.util.spec_from_file_location('m', sys.argv[1])\n" +
      "m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n" +
      "print(m._fmt_num(12500)); print(m._fmt_num(3.0)); " +
      "print(m._fmt_num(15200,' k')); print(m._fmt_num(42.5,'%'))";
    const r = spawnSync(
      py[0]!,
      [...py.slice(1), "-c", code, path.join(ctx.root, CHART)],
      { encoding: "utf-8", timeout: 60_000, input: "" },
    );
    if (r.status !== 0) {
      if (depsMissing(r.stderr)) return [true, "skipped: pack plotting deps unavailable"];
      return [false, `_fmt_num probe failed: ${r.stderr}\n${r.stdout}`];
    }
    const got = r.stdout.split(/\r?\n/).map((s) => s.trim()).filter(Boolean);
    const expected = ["12,500", "3", "15,200 k", "42.5%"];
    for (let i = 0; i < expected.length; i++) {
      if (got[i] !== expected[i]) {
        return [false, `_fmt_num mismatch: expected ${JSON.stringify(expected)}, got ${JSON.stringify(got)}`];
      }
    }
    return true;
  })
  .build();
