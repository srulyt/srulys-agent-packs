/**
 * Structural conformance for the context-pack-builder plugin.
 *
 * No SUT (kind: none) — reads the shipped pack files directly and asserts the
 * plugin is mechanically loadable and internally consistent. Runs offline via
 * `evalpilot run` (no copilot binary, no LLM judge).
 *
 * Ported from the legacy pytest `test_smoke_plugin_conformance.py`.
 */

import * as path from "node:path";
import { Eval } from "evalpilot";

const PACK = "agent-packs/context-pack-builder";
const MARKETPLACE = ".github/plugin/marketplace.json";
const THRESHOLD_REF =
  `${PACK}/skills/progressive-disclosure/references/split-threshold.md`;

const EXPECTED_AGENTS = [
  "cpb-orchestrator",
  "cpb-discovery",
  "cpb-analyzer",
  "cpb-synthesizer",
  "cpb-writer",
  "cpb-indexer",
];
const EXPECTED_SKILLS = [
  "context-pack-schema",
  "context-discovery",
  "progressive-disclosure",
];

const SUPPORTED_AGENT_KEYS = new Set([
  "name",
  "description",
  "tools",
  "disable-model-invocation",
  "user-invocable",
  "model",
  "target",
]);
const SUPPORTED_SKILL_KEYS = new Set([
  "name",
  "description",
  "license",
  "user-invocable",
]);

type Ctx = {
  root: string;
  read(rel: string): string | null;
  glob(pattern: string): string[];
};
type Result = boolean | [boolean, string];

function splitFrontmatter(text: string): { fmLines: string[]; body: string } {
  const lines = text.split(/\r?\n/);
  if (!lines.length || lines[0]!.trim() !== "---") {
    throw new Error("frontmatter must start at line 1");
  }
  let end = -1;
  for (let i = 1; i < lines.length; i++) {
    if (lines[i]!.trim() === "---") {
      end = i;
      break;
    }
  }
  if (end === -1) throw new Error("frontmatter block is not closed");
  return { fmLines: lines.slice(1, end), body: lines.slice(end + 1).join("\n") };
}

function topLevelKeys(fmLines: string[]): string[] {
  const keys: string[] = [];
  for (const ln of fmLines) {
    if (ln && !/^\s/.test(ln) && ln.includes(":")) {
      keys.push(ln.split(":", 1)[0]!.trim());
    }
  }
  return keys;
}

function tokenEstimate(body: string): number {
  const chars = body.length;
  const words = body.split(/\s+/).filter(Boolean).length;
  return Math.max(Math.ceil(chars / 4), Math.ceil(words * 1.33));
}

export default new Eval("context-pack-builder-conformance", {
  kind: "none",
  tags: ["pack", "structural"],
})
  .summarize(
    "context-pack-builder ships as a mechanically loadable, internally " +
      "consistent Copilot plugin.",
  )
  .describe(
    "Structural conformance (no SUT): plugin.json manifest, marketplace " +
      "registration, expected agents/skills, agent + skill frontmatter " +
      "shape, and the single-source SKILL.md token-threshold budget.",
  )
  .check("plugin.json manifest", (ctx: Ctx): Result => {
    const text = ctx.read(`${PACK}/plugin.json`);
    if (text === null) return [false, "missing plugin.json"];
    const m = JSON.parse(text);
    for (const key of ["name", "description", "agents", "skills"]) {
      if (!(key in m)) return [false, `plugin.json missing required key '${key}'`];
    }
    if (m.name !== "context-pack-builder") {
      return [false, `unexpected name ${JSON.stringify(m.name)}`];
    }
    if (m.agents !== "agents/") return [false, "agents must be 'agents/'"];
    if (m.skills !== "skills/") return [false, "skills must be 'skills/'"];
    return true;
  })
  .check("marketplace registration", (ctx: Ctx): Result => {
    const text = ctx.read(MARKETPLACE);
    if (text === null) return [false, "missing marketplace.json"];
    const names = new Set(
      (JSON.parse(text).plugins as { name: string }[]).map((p) => p.name),
    );
    if (!names.has("context-pack-builder")) {
      return [false, "pack not registered in marketplace.json"];
    }
    for (const n of ["prd-pilot", "product-knowledge-brain", "eval-pilot"]) {
      if (!names.has(n)) return [false, `existing entry '${n}' was disturbed`];
    }
    return true;
  })
  .check("expected agents and skills exist", (ctx: Ctx): Result => {
    const agents = new Set(
      ctx
        .glob(`${PACK}/agents/*.agent.md`)
        .map((p) => path.basename(p).replace(/\.agent\.md$/, "")),
    );
    for (const a of EXPECTED_AGENTS) {
      if (!agents.has(a)) return [false, `missing agent: ${a}`];
    }
    for (const s of EXPECTED_SKILLS) {
      if (ctx.read(`${PACK}/skills/${s}/SKILL.md`) === null) {
        return [false, `${s} missing SKILL.md`];
      }
    }
    return true;
  })
  .check("agent frontmatter quoted + supported keys", (ctx: Ctx): Result => {
    let orchestrators = 0;
    let subagents = 0;
    for (const file of ctx.glob(`${PACK}/agents/*.agent.md`)) {
      const rel = path.relative(ctx.root, file).replace(/\\/g, "/");
      const text = ctx.read(rel)!;
      const { fmLines } = splitFrontmatter(text);
      const keys = topLevelKeys(fmLines);
      if (keys.length !== new Set(keys).size) {
        return [false, `${rel}: duplicate frontmatter key`];
      }
      for (const k of keys) {
        if (!SUPPORTED_AGENT_KEYS.has(k)) {
          return [false, `${rel}: unsupported key '${k}'`];
        }
      }
      const desc = fmLines.find((ln) => ln.startsWith("description:"));
      if (!desc) return [false, `${rel}: missing description`];
      const val = desc.split(":").slice(1).join(":").trim();
      if (!(val.startsWith('"') && val.endsWith('"'))) {
        return [false, `${rel}: description must be double-quoted`];
      }
      const joined = fmLines.join("\n");
      if (joined.includes("disable-model-invocation: true")) {
        orchestrators += 1;
        if (!joined.includes("user-invocable: true")) {
          return [false, `${rel}: orchestrator must be user-invocable`];
        }
      } else {
        subagents += 1;
        if (!joined.includes("user-invocable: false")) {
          return [false, `${rel}: subagent must set user-invocable: false`];
        }
        if (joined.includes("disable-model-invocation")) {
          return [false, `${rel}: subagent must NOT set disable-model-invocation`];
        }
      }
    }
    if (orchestrators !== 1) return [false, `expected 1 orchestrator, got ${orchestrators}`];
    if (subagents !== 5) return [false, `expected 5 subagents, got ${subagents}`];
    return true;
  })
  .check("skill frontmatter quoted + supported keys", (ctx: Ctx): Result => {
    for (const file of ctx.glob(`${PACK}/skills/*/SKILL.md`)) {
      const rel = path.relative(ctx.root, file).replace(/\\/g, "/");
      const { fmLines } = splitFrontmatter(ctx.read(rel)!);
      for (const k of topLevelKeys(fmLines)) {
        if (!SUPPORTED_SKILL_KEYS.has(k)) {
          return [false, `${rel}: unsupported skill key '${k}'`];
        }
      }
      const desc = fmLines.find((ln) => ln.startsWith("description:"));
      if (!desc) return [false, `${rel}: missing description`];
      const val = desc.split(":").slice(1).join(":").trim();
      if (!(val.startsWith('"') && val.endsWith('"'))) {
        return [false, `${rel}: description must be double-quoted`];
      }
    }
    return true;
  })
  .check("no bundled SKILL.md body over threshold", (ctx: Ctx): Result => {
    const refText = ctx.read(THRESHOLD_REF);
    if (refText === null) return [false, "missing split-threshold.md"];
    const tm = /SPLIT_THRESHOLD_TOKENS\s*=\s*(\d+)/.exec(refText);
    if (!tm) return [false, "split-threshold.md must define SPLIT_THRESHOLD_TOKENS"];
    const threshold = Number(tm[1]);
    for (const file of ctx.glob(`${PACK}/skills/*/SKILL.md`)) {
      const rel = path.relative(ctx.root, file).replace(/\\/g, "/");
      const { body } = splitFrontmatter(ctx.read(rel)!);
      const est = tokenEstimate(body);
      if (est > threshold) {
        return [false, `${rel}: body token estimate ${est} exceeds ${threshold}`];
      }
    }
    return true;
  })
  .build();
