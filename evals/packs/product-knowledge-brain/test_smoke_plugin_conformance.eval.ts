/**
 * Structural conformance for the Product Knowledge Brain plugin.
 *
 * No SUT (kind: none) — reads the shipped pack files directly and asserts the
 * plugin is mechanically loadable and internally consistent. Runs offline via
 * `evalpilot run` (no copilot binary, no LLM judge).
 *
 * Ported from the legacy pytest `test_smoke_plugin_conformance.py`.
 */

import * as fs from "node:fs";
import * as path from "node:path";
import { Eval } from "@evalpilot/cli";

const PACK = "agent-packs/product-knowledge-brain";
const ENTRY_SKILL = "knowledge-brain";
const SPECIALIST_SKILLS = new Set([
  "knowledge-consolidation",
  "knowledge-organization",
  "knowledge-indexing",
]);
const EXPECTED_SKILLS = new Set([ENTRY_SKILL, ...SPECIALIST_SKILLS]);
const NAME_RE = /^[a-z0-9-]{1,64}$/;

type Ctx = {
  root: string;
  read(rel: string): string | null;
};
type Result = boolean | [boolean, string];

function fullPath(ctx: Ctx, rel: string): string {
  return path.join(ctx.root, ...rel.split("/"));
}

function frontmatter(text: string, skillMd: string): Record<string, string> {
  if (!text.startsWith("---")) {
    throw new Error(`${skillMd} must start with '---' frontmatter`);
  }
  const end = text.indexOf("\n---", 3);
  const block = text.slice(3, end).replace(/^\n|\n$/g, "");
  const out: Record<string, string> = {};
  for (const line of block.split(/\r?\n/)) {
    if (!line.trim() || line.trimStart().startsWith("#") || line.startsWith(" ")) continue;
    const [key, ...rest] = line.split(":");
    out[key!.trim()] = rest.join(":").trim().replace(/^["']|["']$/g, "");
  }
  return out;
}

function descriptionIsQuoted(text: string): boolean {
  for (const line of text.split(/\r?\n/)) {
    if (line.startsWith("description:")) {
      return line.split(":").slice(1).join(":").trim().startsWith('"');
    }
  }
  return false;
}

export default new Eval("product-knowledge-brain-conformance", {
  kind: "none",
  tags: ["pack", "structural"],
})
  .summarize(
    "product-knowledge-brain ships as a mechanically loadable, conformant " +
      "skills-only Copilot plugin.",
  )
  .describe(
    "Structural conformance (no SUT): plugin.json manifest, expected skills, " +
      "skill frontmatter and quoted descriptions, invocation flags, " +
      "skills-only layout, README install flows, and license-claim guard.",
  )
  .check("plugin.json is conformant", (ctx: Ctx): Result => {
    const manifestPath = `${PACK}/plugin.json`;
    const manifestText = ctx.read(manifestPath);
    if (manifestText === null) return [false, `missing manifest: ${fullPath(ctx, manifestPath)}`];

    const manifest = JSON.parse(manifestText);

    const name = manifest.name;
    if (name !== "product-knowledge-brain") {
      return [false, `unexpected plugin name ${JSON.stringify(name)}`];
    }
    if (!NAME_RE.test(name)) {
      return [
        false,
        `plugin name ${JSON.stringify(name)} must be kebab-case, lowercase, <=64 chars`,
      ];
    }
    if (name.includes("/") || name.includes(":")) return [false, ""];

    const desc = manifest.description ?? "";
    if (!(desc.length > 0 && desc.length <= 1024)) {
      return [false, "description must be present and <=1024 chars"];
    }

    const skillsPath = String(manifest.skills ?? "skills/").replace(/\/$/, "");
    const resolved = fullPath(ctx, `${PACK}/${skillsPath}`);
    if (!fs.statSync(resolved).isDirectory()) {
      return [false, `declared skills path does not resolve: ${resolved}`];
    }

    if ("license" in manifest && !fs.existsSync(fullPath(ctx, "LICENSE"))) {
      return [false, "plugin.json claims a license but the repo has no LICENSE file"];
    }
    return true;
  })
  .check("four skills present and named correctly", (ctx: Ctx): Result => {
    const skillsDir = fullPath(ctx, `${PACK}/skills`);
    const found = new Set(
      fs.readdirSync(skillsDir, { withFileTypes: true })
        .filter((p) => p.isDirectory())
        .map((p) => p.name),
    );
    if (
      found.size !== EXPECTED_SKILLS.size ||
      [...found].some((skill) => !EXPECTED_SKILLS.has(skill))
    ) {
      return [
        false,
        `expected skills ${JSON.stringify([...EXPECTED_SKILLS].sort())}, found ${JSON.stringify([...found].sort())}`,
      ];
    }

    for (const skill of EXPECTED_SKILLS) {
      const skillMd = `${PACK}/skills/${skill}/SKILL.md`;
      const text = ctx.read(skillMd);
      if (text === null) return [false, `missing ${fullPath(ctx, skillMd)}`];
      const fm = frontmatter(text, fullPath(ctx, skillMd));
      if (fm.name !== skill) {
        return [
          false,
          `${fullPath(ctx, skillMd)}: frontmatter name ${JSON.stringify(fm.name)} != dir name ${JSON.stringify(skill)}`,
        ];
      }
      const desc = fm.description ?? "";
      if (!(desc.length > 0 && desc.length <= 1024)) {
        return [false, `${fullPath(ctx, skillMd)}: description missing/too long`];
      }
      if (!descriptionIsQuoted(text)) {
        return [false, `${fullPath(ctx, skillMd)}: description value MUST be double-quoted`];
      }
    }
    return true;
  })
  .check("invocation flags match roles", (ctx: Ctx): Result => {
    const skillsDir = `${PACK}/skills`;
    const entryText = ctx.read(`${skillsDir}/${ENTRY_SKILL}/SKILL.md`)!;
    const entryFm = frontmatter(entryText, fullPath(ctx, `${skillsDir}/${ENTRY_SKILL}/SKILL.md`));
    if (entryFm["user-invocable"] !== "true") {
      return [false, `${ENTRY_SKILL} must be user-invocable: true (entry skill)`];
    }

    for (const skill of SPECIALIST_SKILLS) {
      const skillMd = `${skillsDir}/${skill}/SKILL.md`;
      const fm = frontmatter(ctx.read(skillMd)!, fullPath(ctx, skillMd));
      if (fm["user-invocable"] !== "false") {
        return [false, `${skill} must be user-invocable: false (specialist handoff skill)`];
      }
    }
    return true;
  })
  .check("only conformant layout present", (ctx: Ctx): Result => {
    if (fs.existsSync(fullPath(ctx, `${PACK}/.github`))) {
      return [false, "the .github/ tree must be absent for a skills-only plugin"];
    }
    for (const forbidden of ["agents", "prompts", "chatmodes", "instructions"]) {
      if (fs.existsSync(fullPath(ctx, `${PACK}/${forbidden}`))) {
        return [false, `unexpected '${forbidden}/' dir in a skills-only plugin`];
      }
    }
    return true;
  })
  .check("readme documents all three install flows", (ctx: Ctx): Result => {
    const readme = ctx.read(`${PACK}/README.md`)!;
    if (!readme.includes("copilot plugin install")) {
      return [false, "missing Copilot CLI install flow"];
    }
    if (!readme.includes("gh skill install")) return [false, "missing gh skill install flow"];
    if (
      !readme.includes("chat.pluginLocations") &&
      !readme.includes("Install Plugin From Source")
    ) {
      return [false, "missing VS Code agent-plugin install flow"];
    }
    return true;
  })
  .build();
