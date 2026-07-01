/**
 * Pack-level smoke: `eval-pilot` is a conformant agent plugin + TypeScript engine.
 *
 * Structural eval (no Copilot CLI / LLM judge). Guards the packaging of the
 * portable eval plugin. Ported from the legacy pytest
 * `test_smoke_plugin_conformance.py`; the engine-packaging check was rewritten
 * to reflect the single TypeScript engine (`engine-ts`, npm `@evalpilot/cli`)
 * after the Python engine was removed.
 *
 * Checks:
 *  - plugin.json parses, valid kebab-case name, non-empty description, agents/
 *    skills paths resolve to directories.
 *  - the 3 skills (eval-author/eval-runner/eval-metrics) each have a SKILL.md
 *    whose `name` == dir name, a description, and `user-invocable: true`.
 *  - the bundled `eval-judge` agent ships under agents/ AND byte-identically as
 *    engine package data (engine-ts/_data/agents/) so it runs in arbitrary repos.
 *  - engine-ts/package.json declares the `@evalpilot/cli` package, the
 *    `evalpilot` bin, ships `_data` as package files, and the key TS modules
 *    exist.
 *  - README documents the Copilot CLI, VS Code, and `gh skill` install flows.
 *  - marketplace.json registers eval-pilot at the right source path.
 */

import { readFileSync, statSync } from "node:fs";
import * as path from "node:path";
import { Eval } from "@evalpilot/cli";

const PLUGIN_ROOT = "agent-packs/eval-pilot";
const MARKETPLACE = ".github/plugin/marketplace.json";
const EXPECTED_SKILLS = ["eval-author", "eval-runner", "eval-metrics"];
const NAME_RE = /^[a-z0-9-]{1,64}$/;

type Ctx = {
  root: string;
  read(rel: string): string | null;
  glob(pattern: string): string[];
};
type Result = boolean | [boolean, string];

function isDir(abs: string): boolean {
  try {
    return statSync(abs).isDirectory();
  } catch {
    return false;
  }
}

/** Parse leading `---` frontmatter as a flat key/value map (no yaml dep). */
function frontmatter(text: string): Record<string, string> {
  if (!text.startsWith("---")) {
    throw new Error("file must start with '---' frontmatter");
  }
  const end = text.indexOf("\n---", 3);
  if (end === -1) throw new Error("frontmatter block is not closed");
  const block = text.slice(3, end).replace(/\r\n?/g, "\n");
  const out: Record<string, string> = {};
  for (const line of block.split("\n")) {
    if (!line.trim() || line.trimStart().startsWith("#")) continue;
    if (/^[ \t]/.test(line)) continue; // nested / continuation
    const idx = line.indexOf(":");
    if (idx === -1) continue;
    const key = line.slice(0, idx).trim();
    const value = line.slice(idx + 1).trim().replace(/^["']|["']$/g, "");
    out[key] = value;
  }
  return out;
}

export default new Eval("eval-pilot-conformance", {
  kind: "none",
  tags: ["pack", "structural"],
})
  .summarize("eval-pilot is a conformant agent plugin backed by the TS engine.")
  .describe(
    "Structural conformance (no SUT): plugin.json manifest, three invocable " +
      "skills, the eval-judge agent synced to engine package data, the " +
      "TypeScript engine packaging (@evalpilot/cli), README install flows, and " +
      "marketplace registration.",
  )
  .check("plugin.json is conformant", (ctx: Ctx): Result => {
    const text = ctx.read(`${PLUGIN_ROOT}/plugin.json`);
    if (text === null) return [false, "missing plugin.json"];
    const m = JSON.parse(text);
    if (m.name !== "eval-pilot") return [false, `unexpected plugin name ${JSON.stringify(m.name)}`];
    if (!NAME_RE.test(m.name)) return [false, "plugin name must be kebab-case, <=64 chars"];
    const desc = m.description ?? "";
    if (!(desc.length > 0 && desc.length <= 1024)) {
      return [false, "description must be present and <=1024 chars"];
    }
    for (const key of ["agents", "skills"]) {
      const rel = m[key];
      if (!rel) return [false, `plugin.json must declare an '${key}' path`];
      const abs = path.join(ctx.root, PLUGIN_ROOT, String(rel).replace(/\/+$/, ""));
      if (!isDir(abs)) return [false, `declared ${key} path does not resolve: ${abs}`];
    }
    if ("license" in m && ctx.read("LICENSE") === null) {
      return [false, "plugin.json claims a license but the repo has no LICENSE file"];
    }
    return true;
  })
  .check("three skills present, named, and invocable", (ctx: Ctx): Result => {
    const found = new Set(
      ctx
        .glob(`${PLUGIN_ROOT}/skills/*/SKILL.md`)
        .map((p) => path.basename(path.dirname(p))),
    );
    for (const s of EXPECTED_SKILLS) {
      if (!found.has(s)) return [false, `missing skill: ${s}`];
    }
    if (found.size !== EXPECTED_SKILLS.length) {
      return [false, `expected exactly ${EXPECTED_SKILLS.length} skills, found ${found.size}`];
    }
    for (const skill of EXPECTED_SKILLS) {
      const text = ctx.read(`${PLUGIN_ROOT}/skills/${skill}/SKILL.md`);
      if (text === null) return [false, `missing ${skill}/SKILL.md`];
      const fm = frontmatter(text);
      if (fm.name !== skill) {
        return [false, `${skill}/SKILL.md: name ${JSON.stringify(fm.name)} != dir name`];
      }
      const d = fm.description ?? "";
      if (!(d.length > 0 && d.length <= 1024)) {
        return [false, `${skill}/SKILL.md: description missing/too long`];
      }
      if (fm["user-invocable"] !== "true") {
        return [false, `${skill} must be user-invocable: true`];
      }
    }
    return true;
  })
  .check("eval-judge agent present and synced to engine package data", (ctx: Ctx): Result => {
    const pluginAgentRel = `${PLUGIN_ROOT}/agents/eval-judge.agent.md`;
    const text = ctx.read(pluginAgentRel);
    if (text === null) return [false, `missing ${pluginAgentRel}`];
    if (frontmatter(text).name !== "eval-judge") {
      return [false, "agent frontmatter name != 'eval-judge'"];
    }
    const bundledRel = `${PLUGIN_ROOT}/engine-ts/_data/agents/eval-judge.agent.md`;
    if (ctx.read(bundledRel) === null) {
      return [false, `missing bundled judge package data: ${bundledRel}`];
    }
    const a = readFileSync(path.join(ctx.root, pluginAgentRel));
    const b = readFileSync(path.join(ctx.root, bundledRel));
    if (!a.equals(b)) {
      return [
        false,
        "the bundled judge (engine package data) and agents/ copy have drifted; " +
          "they must stay byte-identical",
      ];
    }
    return true;
  })
  .check("TypeScript engine packaging is conformant", (ctx: Ctx): Result => {
    const pkgText = ctx.read(`${PLUGIN_ROOT}/engine-ts/package.json`);
    if (pkgText === null) return [false, "missing engine-ts/package.json"];
    const pkg = JSON.parse(pkgText);
    if (pkg.name !== "@evalpilot/cli") {
      return [false, `engine must declare the @evalpilot/cli package, got ${JSON.stringify(pkg.name)}`];
    }
    if (!pkg.bin || !pkg.bin.evalpilot) {
      return [false, "engine package.json must declare the 'evalpilot' bin"];
    }
    const files: string[] = pkg.files ?? [];
    if (!files.includes("_data")) {
      return [false, "engine must ship '_data' (bundled judge + templates) as package files"];
    }
    const src = `${PLUGIN_ROOT}/engine-ts/src`;
    for (const mod of ["cli.ts", "executor.ts", "metrics.ts", "judge.ts", "collect.ts"]) {
      if (ctx.read(`${src}/${mod}`) === null) {
        return [false, `missing engine module: ${src}/${mod}`];
      }
    }
    return true;
  })
  .check("README documents all three install flows", (ctx: Ctx): Result => {
    const readme = ctx.read(`${PLUGIN_ROOT}/README.md`);
    if (readme === null) return [false, "missing README.md"];
    if (!readme.includes("copilot plugin install")) return [false, "missing Copilot CLI install flow"];
    if (!readme.includes("gh skill install")) return [false, "missing gh skill install flow"];
    if (!readme.includes("chat.pluginLocations") && !readme.includes("Install Plugin From Source")) {
      return [false, "missing VS Code agent-plugin install flow"];
    }
    return true;
  })
  .check("marketplace registers eval-pilot", (ctx: Ctx): Result => {
    const text = ctx.read(MARKETPLACE);
    if (text === null) return [false, "missing marketplace.json"];
    const entries = new Map<string, any>(
      (JSON.parse(text).plugins as any[]).map((p) => [p.name, p]),
    );
    if (!entries.has("eval-pilot")) return [false, "eval-pilot not registered in marketplace.json"];
    if (entries.get("eval-pilot").source !== "agent-packs/eval-pilot") {
      return [false, "eval-pilot marketplace source path is wrong"];
    }
    return true;
  })
  .build();
