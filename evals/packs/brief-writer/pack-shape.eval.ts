/**
 * Static pack-shape checks for brief-writer (no SUT, offline).
 * Proves loadability, wiring, and preserved rules only — not runtime quality.
 */

import * as fs from "node:fs";
import * as path from "node:path";
import { Eval } from "evalpilot";

const PACK = "agent-packs/brief-writer";
const SKILL = `${PACK}/skills/brief-writer`;
const NAME_RE = /^[a-z0-9-]{1,64}$/;
const REFS = [
  "references/structure.md",
  "references/audience-and-championing.md",
  "references/writing-style.md",
  "references/evidence.md",
  "references/decision-framing.md",
  "references/review-and-editing.md",
  "assets/brief-template.md",
];

type Ctx = { root: string; read(rel: string): string | null };
type Result = boolean | [boolean, string];

const full = (ctx: Ctx, rel: string) => path.join(ctx.root, ...rel.split("/"));

function frontmatter(text: string): Record<string, string> {
  const end = text.indexOf("\n---", 3);
  const out: Record<string, string> = {};
  for (const line of text.slice(3, end).split(/\r?\n/)) {
    if (!line.trim()) continue;
    const [k, ...rest] = line.split(":");
    out[k!.trim()] = rest.join(":").trim().replace(/^["']|["']$/g, "");
  }
  return out;
}

function mdFiles(dir: string): string[] {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
    const p = path.join(dir, e.name);
    return e.isDirectory() ? mdFiles(p) : e.name.endsWith(".md") ? [p] : [];
  });
}

const skillText = (ctx: Ctx) =>
  mdFiles(full(ctx, SKILL)).map((f) => fs.readFileSync(f, "utf8")).join("\n");

export default new Eval("brief-writer-pack-shape", { kind: "none", tags: ["pack", "structural"] })
  .summarize("brief-writer is a loadable single-skill plugin that keeps the legacy business rules.")
  .describe(
    "Manifest, single skill layout, no legacy orchestration, link resolution, all references wired, " +
      "preserved rules present, install docs, marketplace registration.",
  )
  .check("manifest is conformant", (ctx: Ctx): Result => {
    const text = ctx.read(`${PACK}/plugin.json`);
    if (text === null) return [false, "missing plugin.json"];
    const m = JSON.parse(text);
    if (!m.$schema) return [false, "missing $schema"];
    if (m.name !== "brief-writer" || !NAME_RE.test(m.name)) return [false, `bad name ${m.name}`];
    if (!m.description || m.description.length > 1024) return [false, "bad description"];
    return true;
  })
  .check("single user-invocable skill, skills-only layout", (ctx: Ctx): Result => {
    const dirs = fs.readdirSync(full(ctx, `${PACK}/skills`), { withFileTypes: true })
      .filter((d) => d.isDirectory()).map((d) => d.name);
    if (dirs.length !== 1 || dirs[0] !== "brief-writer") return [false, `skills: ${dirs}`];
    const fm = frontmatter(ctx.read(`${SKILL}/SKILL.md`) ?? "");
    if (fm.name !== "brief-writer") return [false, `frontmatter name ${fm.name}`];
    if (!fm.description || fm.description.length > 1024) return [false, "bad skill description"];
    if (fm["user-invocable"] !== "true") return [false, "skill must be user-invocable"];
    for (const f of ["agents", "prompts", "chatmodes", "instructions", ".github"]) {
      if (fs.existsSync(full(ctx, `${PACK}/${f}`))) return [false, `unexpected ${f}/`];
    }
    return true;
  })
  .check("no legacy orchestration scaffolding", (ctx: Ctx): Result => {
    const t = skillText(ctx);
    const hit = t.match(/\.product-brief-agent-stm|@brief-orchestrator|brief-composer|evidence-analyst|strategy-modeler|final-artifacts-json|escalate-to-user|state\.json/);
    return [!hit, hit ? `legacy scaffolding: ${hit[0]}` : ""];
  })
  .check("all relative markdown links resolve", (ctx: Ctx): Result => {
    const broken: string[] = [];
    for (const file of mdFiles(full(ctx, PACK))) {
      const text = fs.readFileSync(file, "utf8");
      for (const m of text.matchAll(/\]\(([^)#\s]+)(#[^)]*)?\)/g)) {
        const target = m[1]!;
        if (/^[a-z]+:/i.test(target)) continue;
        if (!fs.existsSync(path.resolve(path.dirname(file), target))) {
          broken.push(`${path.relative(ctx.root, file)} -> ${target}`);
        }
      }
    }
    return broken.length ? [false, broken.join("; ")] : true;
  })
  .check("SKILL.md links every reference and the template", (ctx: Ctx): Result => {
    const s = ctx.read(`${SKILL}/SKILL.md`) ?? "";
    const missing = REFS.filter((r) => !s.includes(`(${r})`));
    return [missing.length === 0, `unlinked: ${missing.join(", ")}`];
  })
  .check("preserved business rules present", (ctx: Ctx): Result => {
    const t = skillText(ctx);
    const rules: [string, RegExp][] = [
      ["closing types P1–P5", /Decision Ask[\s\S]*Call to Action[\s\S]*Recommendation[\s\S]*Next Steps[\s\S]*Summary/],
      ["scope-brief type", /scope-brief/],
      ["audience calibration", /least-expert reader/],
      ["Decision Posture", /Decision Posture/],
      ["no-fabrication labels", /Insufficient data/],
      ["AI-ism guidance", /metadiscourse/i],
      ["no bold-as-heading", /never bold/i],
      ["review checklist", /checklist/i],
    ];
    const missing = rules.filter(([, re]) => !re.test(t)).map(([n]) => n);
    return [missing.length === 0, `missing: ${missing.join(", ")}`];
  })
  .check("README documents install flows", (ctx: Ctx): Result => {
    const r = ctx.read(`${PACK}/README.md`) ?? "";
    if (!r.includes("copilot plugin install")) return [false, "missing CLI flow"];
    if (!r.includes("gh skill install")) return [false, "missing gh skill flow"];
    if (!r.includes("chat.pluginLocations")) return [false, "missing VS Code flow"];
    return true;
  })
  .check("registered in marketplace", (ctx: Ctx): Result => {
    const m = JSON.parse(ctx.read(".github/plugin/marketplace.json") ?? "{}");
    return (m.plugins ?? []).some((p: { name: string; source: string }) =>
      p.name === "brief-writer" && p.source === PACK) || [false, "not in marketplace.json"];
  })
  .build();
