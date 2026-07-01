/**
 * C4 + C6 regression (structural, no LLM): a deck built with the new
 * `ink-editorial` premium design system and the new editorial archetypes must
 * pass the structural asserts — no overflow, no safe-area violations, no
 * blocking findings.
 *
 * Ported from the legacy pytest `test_smoke_new_system_archetype_structural.py`
 * "tooling" smoke test. Source/registration guards are pure file reads and
 * always run. The deck-generation guard shells out to the story-telling pack's
 * own Python scripts (generate_deck.py + check_pptx.py); when Python or the
 * pack's rendering deps are unavailable it degrades to a pass with a note (the
 * pack's verify-or-block policy owns runtime), never a hang.
 */

import { spawnSync } from "node:child_process";
import { mkdtempSync, writeFileSync, existsSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import * as path from "node:path";
import { Eval } from "@evalpilot/cli";

const PACK = "agent-packs/story-telling-agent/.github/skills";
const GEN = `${PACK}/pptx-engine/scripts/generate_deck.py`;
const CHECK = `${PACK}/pptx-structural-asserts/scripts/check_pptx.py`;
const SYSTEMS = `${PACK}/slide-design-systems/references/systems`;

const NEW_SYSTEMS = ["ink-editorial", "quiet-luxury", "signal-dark", "warm-editorial"];
const NEW_ARCHETYPES = [
  "stat_grid_3up",
  "pull_quote_portrait",
  "full_bleed_caption",
  "editorial_2col_6040",
  "timeline_horizontal",
  "agenda_toc",
  "closing_cta",
];

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

export default new Eval("story-telling-new-system-archetype-structural", {
  kind: "none",
  tags: ["pack", "structural", "tooling"],
})
  .summarize(
    "New premium design systems and editorial archetypes register and build " +
      "with no structural violations.",
  )
  .describe(
    "Registration guards (pure reads) plus a bounded deck-generation guard that " +
      "drives the pack's generate_deck.py + check_pptx.py and asserts no " +
      "overflow / safe-area / archetype / contrast violations.",
  )
  .check("new systems register in slide-design-systems SKILL.md", (ctx: Ctx): Result => {
    const skill = ctx.read(`${PACK}/slide-design-systems/SKILL.md`);
    if (skill === null) return [false, "missing slide-design-systems SKILL.md"];
    for (const name of NEW_SYSTEMS) {
      if (ctx.read(`${SYSTEMS}/${name}.md`) === null) {
        return [false, `missing system file ${name}.md`];
      }
      if (!skill.includes(name)) {
        return [false, `${name} not registered in slide-design-systems SKILL.md`];
      }
    }
    return true;
  })
  .check("all new archetypes registered in generate_deck.py", (ctx: Ctx): Result => {
    const src = ctx.read(GEN);
    if (src === null) return [false, "missing generate_deck.py"];
    for (const recipe of NEW_ARCHETYPES) {
      if (!src.includes(`"${recipe}"`)) {
        return [false, `${recipe} not registered in STYLED_RECIPES/BUILDERS`];
      }
    }
    return true;
  })
  .check("new archetype + system produce no structural violations", (ctx: Ctx): Result => {
    const py = pythonPrefix();
    if (!py) return [true, "skipped: no Python interpreter on host"];

    const tmp = mkdtempSync(path.join(tmpdir(), "st-struct-"));
    const spec = {
      design_system_tokens: systemTokens(ctx, "ink-editorial"),
      slides: [
        {
          index: 0, style: "styled", style_recipe: "stat_grid_3up",
          title: "The numbers moved", eyebrow: "Results",
          notes: "Lead with retention; it's the proof point.",
          stats: [
            { value: "42%", label: "Net revenue retention", delta: "+8" },
            { value: "1.9x", label: "Pipeline coverage", delta: "+0.4" },
            { value: "11d", label: "Time to value", delta: "-6" },
          ],
        },
        {
          index: 1, style: "styled", style_recipe: "editorial_2col_6040",
          title: "Why now", standfirst: "The window is open for two quarters.",
          notes: "Frame the urgency before the ask.",
          points: ["Incumbents mid-migration", "Our cost curve crossed"],
          aside: { kicker: "Context", body: "Macro tailwinds align with roadmap." },
        },
        {
          index: 2, style: "styled", style_recipe: "agenda_toc", title: "Agenda",
          notes: "Keep it to four sections.",
          sections: ["Market", "Traction", "Roadmap", "The ask"],
        },
        {
          index: 3, style: "styled", style_recipe: "closing_cta",
          title: "Let's build it", cta: "Approve the raise",
          notes: "End on the single decision we want.", contact: "founder@example.com",
        },
      ],
    };
    const specPath = path.join(tmp, "spec.json");
    const outPptx = path.join(tmp, "deck.pptx");
    const reportPath = path.join(tmp, "structural.json");
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
      return [false, "generate_deck produced no pptx"];
    }

    const chk = spawnSync(
      py[0]!,
      [
        ...py.slice(1), path.join(ctx.root, CHECK),
        "--pptx", outPptx, "--spec", specPath, "--out", reportPath,
      ],
      { encoding: "utf-8", timeout: 180_000, input: "" },
    );
    if (chk.status !== 0) {
      if (depsMissing(chk.stderr)) return [true, "skipped: pack deps unavailable"];
      return [false, `check_pptx failed: ${chk.stderr}\n${chk.stdout}`];
    }
    const report = JSON.parse(ctx.read(path.relative(ctx.root, reportPath).replace(/\\/g, "/"))!);

    if (report.aspect_ratio_pass !== true) return [false, "aspect_ratio_pass is not true"];
    if ((report.overflow_violations ?? []).length) {
      return [false, `new archetypes overflowed: ${JSON.stringify(report.overflow_violations)}`];
    }
    if ((report.safe_area_violations ?? []).length) {
      return [false, `new archetypes broke breathing-room: ${JSON.stringify(report.safe_area_violations)}`];
    }
    if ((report.archetype_violations ?? []).length) {
      return [false, `new archetypes failed shape checks: ${JSON.stringify(report.archetype_violations)}`];
    }
    if ((report.duplicate_titles ?? []).length) {
      return [false, `duplicate titles: ${JSON.stringify(report.duplicate_titles)}`];
    }
    if ((report.speaker_notes_missing ?? []).length) {
      return [false, `speaker notes missing: ${JSON.stringify(report.speaker_notes_missing)}`];
    }
    if ((report.contrast_unresolved ?? []).length >= 5) {
      return [false, `contrast still bucketing as unresolved: ${JSON.stringify(report.contrast_unresolved)}`];
    }
    if ((report.contrast_violations ?? []).length) {
      return [false, `unresolved sub-AA contrast: ${JSON.stringify(report.contrast_violations)}`];
    }
    return true;
  })
  .build();
