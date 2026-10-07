import { Eval } from "evalpilot";
import { createRequire } from "node:module";
import { existsSync, readFileSync, realpathSync } from "node:fs";
import path from "node:path";

const PACK = "agent-packs/agent-factory";
const SKILL = `${PACK}/skills/agent-factory`;
type Context = { root: string; read(name: string): string | null };

export default new Eval("agent-factory-portable-contracts", {
  kind: "none",
  tags: ["pack", "structural", "smoke"],
})
  .summarize("The adjacent factory has one portable skill, intact deployment boundaries and focused resources.")
  .check("portable skill frontmatter and small body", (ctx: Context) => {
    const require = createRequire(path.join(ctx.root, "agent-packs/eval-pilot/engine-ts/package.json"));
    const yaml = require("js-yaml") as { load(source: string): unknown };
    const text = ctx.read(`${SKILL}/SKILL.md`);
    if (!text) return [false, "missing skill"];
    const match = /^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/.exec(text);
    if (!match) return [false, "frontmatter must start at line 1"];
    const meta = yaml.load(match[1]) as Record<string, unknown>;
    if (!meta || meta.name !== "agent-factory") return [false, "wrong skill identity"];
    if (Object.keys(meta).some((key) => !["name", "description"].includes(key))) {
      return [false, "host-specific or unnecessary portable fields"];
    }
    if (typeof meta.description !== "string" || !meta.description.trim() || meta.description.length > 1024) {
      return [false, "invalid portable description"];
    }
    if (!/^description: "/m.test(match[1])) return [false, "description must be quoted"];
    const words = match[2].trim().split(/\s+/).length;
    return words <= 600 ? true : [false, `factory body exceeds 600-word project budget: ${words}`];
  })
  .check("all directly linked resources exist and stay inside the skill", (ctx: Context) => {
    const root = realpathSync(path.join(ctx.root, SKILL));
    const text = ctx.read(`${SKILL}/SKILL.md`) ?? "";
    const links = [...text.matchAll(/\]\(([^)]+)\)/g)].map((match) => match[1]);
    if (links.length < 8) return [false, "missing selective resources"];
    for (const link of links) {
      const target = path.resolve(root, link);
      if (!existsSync(target)) return [false, `missing ${link}`];
      const relative = path.relative(root, realpathSync(target));
      if (relative === ".." || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative)) {
        return [false, `escaping resource ${link}`];
      }
    }
    return true;
  })
  .check("portable and Claude wrappers package the same skill without a factory agent", (ctx: Context) => {
    const manifest = JSON.parse(ctx.read(`${PACK}/plugin.json`) ?? "null");
    const claude = JSON.parse(ctx.read(`${PACK}/.claude-plugin/plugin.json`) ?? "null");
    const allowed = ["$schema", "name", "version", "description", "author", "repository", "keywords"];
    if (!manifest || manifest.$schema !== "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json") {
      return [false, "missing portable schema selection"];
    }
    if (Object.keys(manifest).some((key) => !allowed.includes(key))) return [false, "nonportable manifest fields"];
    if (manifest.name !== "agent-factory" || claude?.name !== manifest.name || claude.version !== manifest.version) {
      return [false, "wrapper identity/version drift"];
    }
    for (const unnecessary of ["agents", "hooks", "mcp.json", ".github/instructions", ".codex/agents"]) {
      if (existsSync(path.join(ctx.root, PACK, unnecessary))) return [false, `unjustified factory component: ${unnecessary}`];
    }
    const marketplace = JSON.parse(ctx.read(".github/plugin/marketplace.json") ?? "{}");
    const entries = marketplace.plugins.filter((plugin: { name: string }) => plugin.name === "agent-factory");
    return entries.length === 1 && entries[0].source === PACK && entries[0].version === manifest.version
      ? true : [false, "marketplace registration drift"];
  })
  .check("migration and evaluation contracts cover preservation and zero-artifact outcomes", (ctx: Context) => {
    const modernization = ctx.read(`${SKILL}/references/modernization.md`) ?? "";
    const record = ctx.read(`${SKILL}/assets/migration-record.md`) ?? "";
    const evaluation = ctx.read(`${SKILL}/references/evaluation.md`) ?? "";
    for (let category = 1; category <= 10; category++) {
      if (!modernization.includes(`| ${category}.`)) return [false, `missing classification ${category}`];
    }
    for (const heading of ["Original capability", "Preserved information", "Removed scaffolding", "Uncertainty", "Recommended evaluations"]) {
      if (!record.includes(heading)) return [false, `missing record field ${heading}`];
    }
    return evaluation.includes("bare frontier agent") && evaluation.includes("no-customization") &&
      modernization.includes("competent human expert") &&
      modernization.includes("explicit authority/precedence") &&
      modernization.includes("conditional on resolution") &&
      modernization.includes("still choreography without persona names") &&
      modernization.includes("Not executing a utility is not evidence")
      ? true : [false, "missing quality baseline, zero outcome, domain order, source precedence or choreography criterion"];
  })
  .check("platform references separate dated evidence and runtime limits", (ctx: Context) => {
    for (const host of ["copilot", "codex", "claude"]) {
      const text = ctx.read(`${SKILL}/references/${host}.md`) ?? "";
      if (!text.includes("2026-10-07") || !text.includes("Official sources")) {
        return [false, `missing evidence for ${host}`];
      }
      if (host !== "copilot" && !text.includes("unverified here")) return [false, `unsupported runtime claim for ${host}`];
    }
    return true;
  })
  .build();
