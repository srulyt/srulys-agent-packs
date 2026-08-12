import { Eval } from "evalpilot";

type Ctx = { read(path: string): string | null };

const PACK = "agent-packs/copilot-factory";

export default new Eval("copilot-factory-capability-docs-consistency", {
  kind: "none",
  tags: ["pack", "structural", "smoke"],
})
  .summarize("Capability baseline, memory guidance, and workflow docs stay aligned.")
  .check("surface/version matrix is explicit and caveated", (ctx: Ctx) => {
    const text = ctx.read(`${PACK}/.github/skills/agent-builder/references/copilot-artifacts.md`) ?? "";
    for (const phrase of [
      "factory-cli-2026-08-12",
      "Surface Compatibility Matrix",
      "Runtime tested here",
      "Runtime compatibility status",
      "unverified",
      "not a universal schema",
      "Copilot Memory",
      "availability-dependent",
      "MCP Decision",
      "Model Decision",
    ]) {
      if (!text.includes(phrase)) return [false, `missing baseline content: ${phrase}`] as [boolean, string];
    }
    if (/Smoke-load verified|direct smoke-load/i.test(text)) {
      return [false, "reference falsely claims a Copilot CLI smoke-load"] as [boolean, string];
    }
    const readme = ctx.read(`${PACK}/README.md`) ?? "";
    const skill = ctx.read(`${PACK}/.github/skills/agent-builder/SKILL.md`) ?? "";
    if (!readme.includes("**unverified**") || !skill.includes("explicitly unverified")) {
      return [false, "README/skill do not state runtime validation is unverified"] as [boolean, string];
    }
    return true;
  })
  .check("README and prompts include eval and fix gates", (ctx: Ctx) => {
    for (const rel of [
      "README.md",
      ".github/prompts/create-pack.prompt.md",
      ".github/prompts/analyze-and-improve.prompt.md",
      ".github/instructions/factory.instructions.md",
    ]) {
      const text = ctx.read(`${PACK}/${rel}`) ?? "";
      if (!/eval/i.test(text)) return [false, `${rel} omits eval workflow`] as [boolean, string];
    }
    const readme = ctx.read(`${PACK}/README.md`) ?? "";
    if (!readme.includes("eval-run-{n}.json") || !readme.includes("improvement-analysis.md")) {
      return [false, "README state tree is incomplete"] as [boolean, string];
    }
    return true;
  })
  .check("unsupported automatic local-memory claim is absent", (ctx: Ctx) => {
    const files = [
      `${PACK}/README.md`,
      `${PACK}/.github/skills/agent-builder/SKILL.md`,
      `${PACK}/.github/skills/agent-builder/references/copilot-artifacts.md`,
    ];
    for (const file of files) {
      const text = (ctx.read(file) ?? "").toLowerCase();
      if (text.includes("memory files survive between conversations and are automatically loaded")) {
        return [false, `unsupported memory claim in ${file}`] as [boolean, string];
      }
    }
    return true;
  })
  .check("behavioral smoke tags match smoke filenames only", (ctx: Ctx) => {
    const specs = [
      ["test_smoke_issue_triage.eval.md", true],
      ["test_smoke_orchestrator_no_self_redirect.eval.md", true],
      ["test_critic_veto_weak_architecture.eval.md", false],
      ["test_incremental_improvement_honoured.eval.md", false],
    ] as const;
    for (const [name, expected] of specs) {
      const text = ctx.read(`evals/packs/copilot-factory/${name}`) ?? "";
      const frontmatter = text.split("---", 3)[1] ?? "";
      const tagged = /tags:\s*\[[^\]]*\bsmoke\b/.test(frontmatter);
      if (tagged !== expected) {
        return [false, `${name}: smoke tag expected=${expected}, actual=${tagged}`] as [boolean, string];
      }
    }
    return true;
  })
  .check("agent bodies retain role boundaries under compact aggregate budget", (ctx: Ctx) => {
    const names = [
      "copilot-factory", "factory-architect", "factory-critic",
      "factory-engineer", "factory-eval-runner",
    ];
    let bytes = 0;
    for (const name of names) {
      const text = ctx.read(`${PACK}/.github/agents/${name}.agent.md`);
      if (!text) return [false, `${name} missing`] as [boolean, string];
      const body = text.split(/^---\s*$/m, 3)[2] ?? text;
      bytes += new TextEncoder().encode(body.replace(/^\r?\n/, "")).length;
      for (const section of ["File Access Boundaries", "Must NOT"]) {
        if (!body.includes(`## ${section}`)) {
          return [false, `${name} lost ${section}`] as [boolean, string];
        }
      }
    }
    return bytes < 36000
      ? true
      : [false, `aggregate agent bodies are ${bytes} bytes (budget <36000)`] as [boolean, string];
  })
  .build();
