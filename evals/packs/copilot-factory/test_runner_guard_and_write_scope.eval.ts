import { Eval } from "evalpilot";

type Ctx = { read(path: string): string | null };

const RUNNER =
  "agent-packs/copilot-factory/.github/agents/factory-eval-runner.agent.md";
const WRAPPER =
  "agent-packs/copilot-factory/.github/skills/agent-builder/scripts/run-evals-guarded.mjs";

export default new Eval("copilot-factory-runner-safety", {
  kind: "none",
  tags: ["pack", "structural", "smoke"],
})
  .summarize("Guarded Eval Pilot execution enforces disjoint repository writes.")
  .check("runner frontmatter grants edit but remains a hidden subagent", (ctx: Ctx) => {
    const text = ctx.read(RUNNER);
    if (!text) return [false, "runner missing"] as [boolean, string];
    const frontmatter = text.slice(0, text.indexOf("\n---", 4));
    if (!frontmatter.includes('"edit"')) return [false, "runner lacks edit tool"] as [boolean, string];
    if (!frontmatter.includes("user-invocable: false")) return [false, "runner is user-invocable"] as [boolean, string];
    if (frontmatter.includes("disable-model-invocation")) {
      return [false, "runner was removed from task registry"] as [boolean, string];
    }
    return true;
  })
  .check("runner requires the enforcing wrapper", (ctx: Ctx) => {
    const text = ctx.read(RUNNER) ?? "";
    for (const phrase of [
      "Runner-owned write (`edit`)",
      "Guarded child output (`execute`)",
      "run-evals-guarded.mjs",
      "OS-temporary eval root",
      "fingerprints the repository",
      "FACTORY_GUARDED_REPORT",
      "no direct `evalpilot`",
    ]) {
      if (!text.includes(phrase)) return [false, `missing safety phrase: ${phrase}`] as [boolean, string];
    }
    return true;
  })
  .check("wrapper isolates child output and detects repository writes", (ctx: Ctx) => {
    const text = ctx.read(WRAPPER) ?? "";
    for (const phrase of [
      "EVALPILOT_EVAL_ROOT",
      "EVALPILOT_METRICS_ROOT",
      "snapshotTree(root)",
      "diffSnapshots(before",
      "repository write outside isolated output",
      "runs.length !== 1",
      "errorOnExist: true",
      "FACTORY_GUARDED_REPORT",
    ]) {
      if (!text.includes(phrase)) return [false, `wrapper missing: ${phrase}`] as [boolean, string];
    }
    return true;
  })
  .check("guard rejects direct users and proxy agents but permits Factory task shape", (ctx: Ctx) => {
    const text = ctx.read(RUNNER) ?? "";
    for (const phrase of [
      "actual `@copilot-factory` `task` delegation",
      ".copilot-factory/sessions/{session-id}/",
      "default agent",
      "role-play",
      "Both the orchestrator identity and session path are required",
    ]) {
      if (!text.includes(phrase)) return [false, `guard missing: ${phrase}`] as [boolean, string];
    }
    return true;
  })
  .build();
