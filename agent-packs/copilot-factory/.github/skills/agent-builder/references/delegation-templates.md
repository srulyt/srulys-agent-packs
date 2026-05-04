# Delegation Templates

Reusable delegation patterns for orchestrator agents that coordinate sub-agents through structured workflows.

## `task` Call Shape

Each template below shows the **prompt body** the orchestrator
constructs. The orchestrator must wrap that prompt in a literal
`task` tool call:

```
task(
  agent_type: "<frontmatter-name>",  // "Factory Architect" | "Factory Engineer" | "Factory Critic"
  name: "<short-kebab>",
  description: "<3-5 word summary>",
  mode: "sync",                      // background only when justified
  prompt: "<the prompt body from the matching template below>"
)
```

See [`task-tool-mechanics.md`](task-tool-mechanics.md) for the
canonical template, rules, and full `task` semantics — including
the conditional availability of `read_agent` / `write_agent` /
`list_agents` (registered only when a background-mode sub-agent is
in `status: idle`; not callable in a strictly sync pipeline). Never
invoke a sub-agent by writing prose — the only invocation channel is
the `task` tool.

## Architect Delegation

```markdown
Invoke @factory-architect to design the system architecture.

Session: {session-id}
Context: .copilot-factory/sessions/{session-id}/context/user-request.md
Output: .copilot-factory/sessions/{session-id}/artifacts/architecture.md

Requirements:
1. Design for requirement fit, not template compliance
2. Define clear agent boundaries and tool restrictions
3. Include communication and state strategy (if needed)
4. Return implementation-ready architecture
```

## Critic Delegation (Architecture)

```markdown
Invoke @factory-critic to review architecture.

Session: {session-id}
Requirements: .copilot-factory/sessions/{session-id}/context/user-request.md
Architecture: .copilot-factory/sessions/{session-id}/artifacts/architecture.md
Review Type: architecture

Return:
- PASS or BLOCKING
- Blocking issues with remediation
- Optional non-blocking concerns
```

## Critic Delegation (Improvement Analysis)

```markdown
Invoke @factory-critic to analyze and improve an existing agent pack.

Session: {session-id}
Target Pack: {pack-path-or-name}
Requirements: .copilot-factory/sessions/{session-id}/context/user-request.md
Review Type: improvement-analysis

Return:
- Prioritized improvements by category
- Actionable rewrites or diffs where possible
- Recommendation: proceed to implementation workflow or stop
```

## Engineer Delegation (Full Build)

```markdown
Invoke @factory-engineer to implement the system.

Session: {session-id}
Architecture: .copilot-factory/sessions/{session-id}/artifacts/architecture.md
Context: .copilot-factory/sessions/{session-id}/context/user-request.md

Output location: agent-packs/{pack-name}/

Artifacts to generate:
- .github/agents/*.agent.md
- .github/skills/*/SKILL.md
- README.md

Build manifest: .copilot-factory/sessions/{session-id}/artifacts/build-manifest.json

Requirements:
1. Read architecture document completely
2. Generate Copilot CLI artifacts
3. Update build manifest with created files
4. Return summary of what was created
```

## Engineer Delegation (Incremental Improvement)

When `improvement_strategy` is `incremental`:

```markdown
Invoke @factory-engineer to apply incremental improvements.

Session: {session-id}
Improvement Analysis: .copilot-factory/sessions/{session-id}/artifacts/improvement-analysis.md
Context: .copilot-factory/sessions/{session-id}/context/user-request.md
Mode: incremental

Target pack: agent-packs/{pack-name}/

Requirements:
1. Read the improvement analysis document completely
2. Apply ONLY the changes identified in the analysis
3. Preserve all existing content that is not flagged for change
4. Do NOT restructure or rewrite files beyond what the analysis specifies
5. Update build manifest with modified files
6. Return summary of changes applied vs. skipped
```

## Eval Runner Delegation (Phase 7.5 / 7.6)

Used by the orchestrator to launch `@factory-eval-runner` after a
PASS verdict from `review-prompts`, and again after each
`@factory-engineer mode=fix` turn during the eval-fix-loop.

```
task(
  agent_type: "Factory Eval Runner",
  name: "run-evals",
  description: "Execute the pack's eval suite",
  mode: "sync",
  prompt: "You are being invoked as @factory-eval-runner.\n" +
          "Session: {session-id}\nPack: {pack-name}\n" +
          "Eval run index: {n}\n" +
          "Output path: .copilot-factory/sessions/{session-id}/artifacts/eval-run-{n}.json\n" +
          "Spec path: evals/packs/{pack-name}/spec.yaml\n" +
          "cases_subset: {all|case-id-1,case-id-2}\n\n" +
          "Read the spec to resolve `budgets:` and `loop_convergence:` " +
          "yourself (the orchestrator does not have read access to " +
          "`evals/`). Emit `eval-summary`, `eval-verdict`, " +
          "`failing-cases-json`, `resolved-budgets-json`, " +
          "`resolved-convergence-json`, `ready-for-orchestrator`."
)
```

Parse `eval-verdict.status` (`pass` | `fail` | `harness-error`). On
`harness-error`, escalate per the orchestrator's Iteration Caps; do
NOT loop. The orchestrator MUST trust the runner's
`resolved-budgets-json` / `resolved-convergence-json` blocks and
persist them into `state.eval_loop.guardrails` — the orchestrator's
own File Access Boundaries do not include `evals/`, so the runner is
the single source of truth for spec-derived values.

## Engineer Delegation (Fix Mode — eval-fix-loop)

Used by the orchestrator inside Phase 7.6 once the user has approved
the eval-fix-loop. Each invocation is a FRESH sub-agent launch — do
NOT use `write_agent` to continue a prior fix turn (stale failure
data must not leak across iterations).

```
task(
  agent_type: "Factory Engineer",
  name: "fix-eval-failures",
  description: "Apply fixes for the latest eval run's failures",
  mode: "sync",
  prompt: "You are being invoked as @factory-engineer.\n" +
          "Session: {session-id}\nMode: fix\n" +
          "Eval run path: .copilot-factory/sessions/{session-id}/artifacts/eval-run-{n}.json\n" +
          "Loop iteration: {m}\n\nRead `failures[]`. Edit ONLY paths " +
          "in each failure's `fixable_in[]`. Emit `fix-summary`, " +
          "`failures-addressed-json`, `failures-skipped-json`, " +
          "`files-modified-json`, `ready-for-rerun`."
)
```

If `ready-for-rerun: false` (engineer skipped every failure), the
orchestrator must surface `failures-skipped-json` to the user and
stop the loop — this is the safety valve against unfixable-rubric
infinite loops.

## Critic Delegation (Implementation)

```markdown
Invoke @factory-critic to review implementation.

Session: {session-id}
Architecture: .copilot-factory/sessions/{session-id}/artifacts/architecture.md
Build Manifest: .copilot-factory/sessions/{session-id}/artifacts/build-manifest.json
Review Type: implementation

Return:
- PASS or BLOCKING
- Architecture alignment findings
- Blocking issues if any
```
