/**
 * Static pack-shape checks for spec-writer (no SUT, offline).
 * Proves loadability and template invariants only — not runtime quality.
 */

import * as fs from "node:fs";
import * as path from "node:path";
import { Eval } from "evalpilot";

const PACK = "agent-packs/spec-writer";
const SKILL = `${PACK}/skills/spec-writer`;
const NAME_RE = /^[a-z0-9-]{1,64}$/;
const MANDATORY = [
  "Document Information",
  "Problem Statement",
  "Goals & Success Metrics",
  "Users & Personas",
  "Solution Summary",
  "Functional Requirements",
  "Risks & Mitigations",
  "Open Questions",
  "Out of Scope",
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

export default new Eval("spec-writer-pack-shape", { kind: "none", tags: ["pack", "structural"] })
  .summarize("spec-writer is a loadable single-skill plugin whose template keeps its invariants.")
  .describe(
    "Manifest, single skill layout, link resolution, mandatory heading order, " +
      "single persona table, no Alternatives Considered, what-if linkage, install docs.",
  )
  .check("manifest is conformant", (ctx: Ctx): Result => {
    const text = ctx.read(`${PACK}/plugin.json`);
    if (text === null) return [false, "missing plugin.json"];
    const m = JSON.parse(text);
    if (!m.$schema) return [false, "missing $schema"];
    if (m.name !== "spec-writer" || !NAME_RE.test(m.name)) return [false, `bad name ${m.name}`];
    if (!m.description || m.description.length > 1024) return [false, "bad description"];
    return true;
  })
  .check("single user-invocable skill, skills-only layout", (ctx: Ctx): Result => {
    const dirs = fs.readdirSync(full(ctx, `${PACK}/skills`), { withFileTypes: true })
      .filter((d) => d.isDirectory()).map((d) => d.name);
    if (dirs.length !== 1 || dirs[0] !== "spec-writer") return [false, `skills: ${dirs}`];
    const fm = frontmatter(ctx.read(`${SKILL}/SKILL.md`) ?? "");
    if (fm.name !== "spec-writer") return [false, `frontmatter name ${fm.name}`];
    if (!fm.description || fm.description.length > 1024) return [false, "bad skill description"];
    if (fm["user-invocable"] !== "true") return [false, "skill must be user-invocable"];
    for (const f of ["agents", "prompts", "chatmodes", "instructions", ".github"]) {
      if (fs.existsSync(full(ctx, `${PACK}/${f}`))) return [false, `unexpected ${f}/`];
    }
    return true;
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
  .check("template has mandatory sections in order", (ctx: Ctx): Result => {
    const t = ctx.read(`${SKILL}/assets/spec-template.md`) ?? "";
    const headings = [...t.matchAll(/^## ([^<\n]+?)\s*(<!--.*)?$/gm)].map((m) => m[1]!.trim());
    let last = -1;
    for (const h of MANDATORY) {
      const i = headings.indexOf(h);
      if (i < 0) return [false, `missing ## ${h}`];
      if (i < last) return [false, `## ${h} out of order`];
      last = i;
    }
    return true;
  })
  .check("exactly one persona table; no Alternatives Considered", (ctx: Ctx): Result => {
    const t = ctx.read(`${SKILL}/assets/spec-template.md`) ?? "";
    const tables = (t.match(/^\|\s*Persona\s*\|/gm) ?? []).length;
    if (tables !== 1) return [false, `persona tables: ${tables}`];
    if (/Alternatives Considered/i.test(t)) return [false, "template references Alternatives Considered"];
    return true;
  })
  .check("what-if coverage is wired in", (ctx: Ctx): Result => {
    const ref = "references/what-if-coverage.md";
    if (ctx.read(`${SKILL}/${ref}`) === null) return [false, "missing what-if reference"];
    if (!(ctx.read(`${SKILL}/SKILL.md`) ?? "").includes(ref)) return [false, "SKILL.md doesn't link it"];
    if (!(ctx.read(`${SKILL}/assets/spec-template.md`) ?? "").includes(`../${ref}`)) {
      return [false, "template doesn't link it"];
    }
    if (!(ctx.read(`${SKILL}/references/quality-checklist.md`) ?? "").includes("what-if-coverage.md")) {
      return [false, "checklist doesn't enforce it"];
    }
    return true;
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
      p.name === "spec-writer" && p.source === PACK) || [false, "not in marketplace.json"];
  })
  .build();
