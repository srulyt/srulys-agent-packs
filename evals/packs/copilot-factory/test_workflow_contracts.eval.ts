import { Eval } from "evalpilot";

type Ctx = { read(path: string): string | null };
type Result = boolean | [boolean, string];

const ROOT = "agent-packs/copilot-factory/.github";
const UNSAFE =
  "evals/packs/copilot-factory/fixtures/selector_validation/unsafe-targets.json";
const VALID_FIXES =
  "evals/packs/copilot-factory/fixtures/fixable_path_validation/valid.json";
const INVALID_FIXES =
  "evals/packs/copilot-factory/fixtures/fixable_path_validation/invalid.json";

function requireAll(text: string | null, needles: string[]): Result {
  if (text === null) return [false, "missing file"];
  const absent = needles.filter((n) => !text.includes(n));
  return absent.length ? [false, `missing: ${absent.join(", ")}`] : true;
}

export default new Eval("copilot-factory-workflow-contracts", {
  kind: "none",
  tags: ["pack", "structural", "smoke"],
})
  .summarize("Factory producers and consumers share versioned workflow contracts.")
  .check("canonical contract defines eval failures and selector", (ctx: Ctx) =>
    requireAll(ctx.read(`${ROOT}/skills/agent-builder/references/workflow-contracts.md`), [
      "factory.eval-result/v1",
      '"failure_id"',
      '"fixable_in"',
      "Canonical rerun selector",
      "The only selector field is `target`",
    ]),
  )
  .check("eval v1 JSON Schema covers fixable and unfixable failures", (ctx: Ctx) => {
    const raw = ctx.read(
      `${ROOT}/skills/agent-builder/references/factory-eval-result-v1.schema.json`,
    );
    if (!raw) return [false, "missing eval result JSON Schema"];
    const schema = JSON.parse(raw);
    if (schema.$id !== "factory.eval-result/v1") return [false, "wrong schema id"];
    const required: string[] = schema.properties.failures.items.required;
    for (const key of [
      "failure_id", "case_id", "kind", "message_excerpt",
      "log_path", "test_path", "fixable_in",
    ]) {
      if (!required.includes(key)) return [false, `failure schema does not require ${key}`];
    }
    const fixtures = [
      { failure_id: "f/1", case_id: "f", kind: "assertion", message_excerpt: "x",
        log_path: null, test_path: "evals/packs/p/a.eval.md",
        fixable_in: ["agent-packs/p/.github/agents/a.agent.md"] },
      { failure_id: "f/2", case_id: "f", kind: "judge", message_excerpt: "x",
        log_path: null, test_path: null, fixable_in: [] },
    ];
    return fixtures.every((f) => required.every((k) => k in f))
      ? true
      : [false, "fixable/unfixable fixtures do not satisfy required fields"];
  })
  .check("fixable paths allow target .github files and reject unsafe/cross-pack paths", (ctx: Ctx) => {
    const schemaRaw = ctx.read(
      `${ROOT}/skills/agent-builder/references/factory-eval-result-v1.schema.json`,
    );
    const validRaw = ctx.read(VALID_FIXES);
    const invalidRaw = ctx.read(INVALID_FIXES);
    const validator = ctx.read(
      `${ROOT}/skills/agent-builder/scripts/validate-factory-paths.mjs`,
    ) ?? "";
    if (!schemaRaw || !validRaw || !invalidRaw) return [false, "fixable fixtures missing"];
    const schema = JSON.parse(schemaRaw);
    const pattern = new RegExp(
      schema.properties.failures.items.properties.fixable_in.items.pattern,
    );
    const runtimeSafe = (value: string, pack: string): boolean => {
      if (/^(?:[A-Za-z]:[\\/]|\\\\|\/\/|\/|[a-z][a-z0-9+.-]*:)/i.test(value)) return false;
      if (value.includes("\\") || /[*?[\]]/.test(value)) return false;
      const parts = value.split("/");
      if (parts.some((part) => part === "" || part === "." || part === "..")) return false;
      return value.startsWith(`agent-packs/${pack}/.github/`);
    };
    for (const value of JSON.parse(validRaw) as string[]) {
      if (!pattern.test(value) || !runtimeSafe(value, "example-pack")) {
        return [false, `valid fix path rejected: ${value}`];
      }
    }
    for (const value of JSON.parse(invalidRaw) as string[]) {
      if (runtimeSafe(value, "example-pack")) {
        return [false, `unsafe/cross-pack fix path accepted: ${value}`];
      }
    }
    for (const phrase of ["validateFixablePath", ".github/", "path.relative"]) {
      if (!validator.includes(phrase)) return [false, `runtime validator missing ${phrase}`];
    }
    return true;
  })
  .check("selector schema and runtime rules reject unsafe targets", (ctx: Ctx) => {
    const schemaRaw = ctx.read(
      `${ROOT}/skills/agent-builder/references/factory-eval-result-v1.schema.json`,
    );
    const fixtureRaw = ctx.read(UNSAFE);
    if (!schemaRaw || !fixtureRaw) return [false, "selector schema/fixtures missing"];
    const schema = JSON.parse(schemaRaw);
    const pattern = new RegExp(schema.properties.selector.properties.target.pattern);
    const fixtures = JSON.parse(fixtureRaw) as Array<{
      target: string; schema_rejects: boolean; reason: string;
    }>;
    const runtimeSafe = (target: string, pack: string): boolean => {
      if (target === "all") return true;
      if (/^(?:[A-Za-z]:[\\/]|\\\\|\/|[a-z][a-z0-9+.-]*:)/i.test(target)) return false;
      if (target.includes("\\") || /[*?[\]]/.test(target)) return false;
      const parts = target.split("/");
      if (parts.some((part) => part === "" || part === "." || part === "..")) return false;
      const root = ["evals", "packs", pack];
      return root.every((part, i) => parts[i] === part) && parts.length > root.length;
    };
    for (const fixture of fixtures) {
      if (fixture.schema_rejects && pattern.test(fixture.target)) {
        return [false, `schema accepted ${fixture.reason}: ${fixture.target}`];
      }
      if (runtimeSafe(fixture.target, "p")) {
        return [false, `runtime accepted ${fixture.reason}: ${fixture.target}`];
      }
    }
    for (const safe of ["all", "evals/packs/p/a.eval.md", "evals/packs/p/sub-dir"]) {
      if (!pattern.test(safe) || !runtimeSafe(safe, "p")) {
        return [false, `safe selector rejected: ${safe}`];
      }
    }
    return true;
  })
  .check("runner produces and engineer consumes eval v1", (ctx: Ctx) => {
    const runner = ctx.read(`${ROOT}/agents/factory-eval-runner.agent.md`);
    const engineer = ctx.read(`${ROOT}/agents/factory-engineer.agent.md`);
    const orchestrator = ctx.read(`${ROOT}/agents/copilot-factory.agent.md`);
    for (const [name, text] of [["runner", runner], ["engineer", engineer], ["orchestrator", orchestrator]] as const) {
      if (!text?.includes("factory.eval-result/v1")) return [false, `${name} lacks eval schema version`];
    }
    if (!runner?.includes("target") || !orchestrator?.includes("target:")) {
      return [false, "runner/orchestrator lacks canonical target selector"];
    }
    return true;
  })
  .check("improvement v1 is wired across critic, orchestrator, and template", (ctx: Ctx) => {
    for (const rel of [
      "agents/factory-critic.agent.md",
      "agents/copilot-factory.agent.md",
      "skills/agent-builder/references/delegation-templates.md",
    ]) {
      const text = ctx.read(`${ROOT}/${rel}`);
      const result = requireAll(text, [
        "factory.improvement-analysis/v1",
        "findings-json",
        "improvement-plan",
        "ready-for-orchestrator",
      ]);
      if (result !== true) return [false, `${rel}: ${result[1]}`];
    }
    return true;
  })
  .check("incremental fixture implements all five improvement-v1 fences", (ctx: Ctx) => {
    const fixture = ctx.read(
      "evals/packs/copilot-factory/fixtures/incremental_improvement_honoured/" +
      ".copilot-factory/sessions/2026-02-01-cafef00d/artifacts/improvement-analysis.md",
    ) ?? "";
    const labels = [
      "verdict", "recommendation", "findings-json",
      "improvement-plan", "ready-for-orchestrator",
    ];
    for (const label of labels) {
      if (!fixture.includes(`\`\`\`${label}`)) return [false, `fixture lacks ${label}`];
    }
    return fixture.includes("schema_version: factory.improvement-analysis/v1")
      ? true : [false, "fixture lacks improvement schema version"];
  })
  .check("review templates use current phases and persisted artifact names", (ctx: Ctx) => {
    const template = ctx.read(`${ROOT}/skills/agent-builder/references/delegation-templates.md`) ?? "";
    for (const phrase of [
      "Eval Runner Delegation (Phases 8 / 9)",
      "artifacts/architecture-review.md",
      "artifacts/implementation-review.md",
      'agent_type: "Factory Critic"',
      'agent_type: "Factory Eval Runner"',
    ]) {
      if (!template.includes(phrase)) return [false, `delegation template lacks ${phrase}`];
    }
    return template.includes("Phase 7.5 / 7.6")
      ? [false, "obsolete phase names remain"] : true;
  })
  .check("behavioral fixtures honor review and approval gates", (ctx: Ctx) => {
    const happy = ctx.read("evals/packs/copilot-factory/test_smoke_issue_triage.eval.md") ?? "";
    for (const phrase of [
      "phases 1-8",
      "approval question",
      "architecture-review.md",
      "implementation-review.md",
    ]) {
      if (!happy.includes(phrase)) return [false, `happy path lacks ${phrase}`];
    }
    if (happy.includes("standard four-phase")) return [false, "happy path uses obsolete workflow"];
    const veto = ctx.read(
      "evals/packs/copilot-factory/test_critic_veto_weak_architecture.eval.md",
    ) ?? "";
    for (const phrase of ["current", "review-arch", "architecture-review.md", "Do NOT"]) {
      if (!veto.includes(phrase)) return [false, `veto path lacks ${phrase}`];
    }
    return true;
  })
  .build();
