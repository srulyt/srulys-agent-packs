---
name: agent-builder
description: "Builds and validates GitHub Copilot agent packs. Use for .agent.md, SKILL.md, delegation, workflow contracts, and Eval Pilot integration."
---

# Agent Builder

Factory source of truth for materializing Copilot agent packs. Load this skill
when writing or reviewing agents, skills, prompts, instructions, READMEs, or
evals.

## Capability Baseline

The detailed, sourced, surface-specific matrix is
[Copilot Artifacts](references/copilot-artifacts.md). It is authoritative for
the Factory's selected target; do not turn its supported set into a universal
Copilot claim. The current baseline is `factory-cli-2026-08-12`, statically
validated in this repository; a Copilot CLI executable was not available in
the build environment, so runtime smoke status is explicitly unverified.

Core Factory-supported agent keys for that baseline:

| Key | Use |
|---|---|
| `name` | Human-readable name; invocation slug comes from filename |
| `description` | Required, double-quoted string |
| `tools` | Minimum target-supported aliases |
| `disable-model-invocation` | `true` on user-facing orchestrators |
| `user-invocable` | `false` on delegation-only subagents |
| `model`, `target` | Optional only after target compatibility decision |

Skill keys are `name`, `description`, and optional `license`. Validate against
the matrix target column; reject duplicates and target-unsupported keys.

## Critical Preflight

Before emitting any frontmatter:

1. Start `---` at line 1 and parse YAML as a flat mapping.
2. Double-quote every `description`.
3. Reject duplicate or target-unsupported keys.
4. Apply role flags: orchestrator =
   `disable-model-invocation: true`, `user-invocable: true`; subagent =
   `user-invocable: false` and no `disable-model-invocation`.
5. Use the minimum tools. `["*"]` is forbidden for generated coordinators;
   `execute` needs an explicit architecture justification.

## Required Prompt Structure

Every generated agent has:

- role, inputs, and role-specific process;
- `## File Access Boundaries` with narrow read/write paths;
- `## Must NOT`;
- `## Skills to Load` when skills are used;
- a machine-parseable named-fence output contract for subagents.

Every subagent uses the two-sided guard in
[agent-template.md](assets/copilot/agent-template.md): it proceeds only for the
named orchestrator plus valid STM/session path and refuses users, default
agents, `general-purpose`, and role-play proxies.

Every coordinator follows
[Task Tool Mechanics](references/task-tool-mechanics.md): mandatory
`## How to Delegate (Task Tool Mechanics)` and
`## Hard Delegation Rule (STOP-and-delegate)` sections, one `task(...)`
example per subagent, named-fence parsing, iteration protocol, and retry cap.

## File Boundaries

Path restrictions are prompt-level guardrails; the target runtime does not
provide per-path tool permissions in this Factory baseline. Grant the
narrowest tool and write scopes:

| Role | Typical tools | Write scope |
|---|---|---|
| read-only analyst | `read`, `search` | none |
| critic with report | `read`, `edit`, `search` | STM artifacts |
| engineer | `read`, `edit`, `search` | designated output + STM manifest |
| coordinator | `read`, `edit`, `search`, `agent` | STM only |

## Skills and Context

Skills are progressively disclosed by relevance. Keep reusable domain policy
in skills and role-specific gates/boundaries in prompts; do not duplicate
paragraphs across both.

For deterministic repository context, use supported repository/path-specific
custom instructions. `.github/memory/*.md` is only a Factory-managed local
convention and must be explicitly read by an authorized agent. GitHub Copilot
Memory is a distinct, availability-dependent product capability; never assume
it exists or that a local memory directory maps to it.

## MCP and Models

Architectures make concise requirement-driven decisions:

- MCP: use only when required external capability is unavailable through
  built-ins; record target support, trust, auth, least-privilege tools, and
  fallback.
- Model: inherit default unless an outcome requires an available override.
  Record resolved model when exposed; consider cost/multiplier and eval
  comparability. Do not hard-code model rankings.

## Evals and Workflow Contracts

- Author generated-pack evals using
  [Eval Authoring](references/eval-authoring.md) and Eval Pilot's own skills.
- Use [Workflow Contracts](references/workflow-contracts.md) for the versioned
  eval result/failure schema, canonical `target` selector, and improvement
  analysis fences.
- Path checks use executable `scripts/validate-factory-paths.mjs`; guarded eval
  execution uses `scripts/run-evals-guarded.mjs`. Resolve and invoke both only
  through the absolute-path, explicit-Node preflight in Workflow Contracts'
  **Canonical guarded-wrapper invocation**; never copy a placeholder or run an
  `.mjs` directly. Prompt reasoning is not a substitute for either
  enforcement point.
- Full builds require at least one spec plus eval README and lint. Incremental
  work changes evals only when the approved finding requires it.

## Quality Checklist

- [ ] Architecture/approved finding coverage; no invented artifacts.
- [ ] Frontmatter preflight passes for selected target.
- [ ] Correct flags, two-sided guards, least-privilege tools and paths.
- [ ] Skills are declared and not duplicated into prompts.
- [ ] Subagent named fences and coordinator task mechanics are complete.
- [ ] README counts, names, phases, and paths match implementation.
- [ ] Agent bodies are under 30,000 characters; skills under 5,000 words.
- [ ] Manifest lists every created/modified eval artifact.
- [ ] Eval specs lint and include structural assertions.

## References

- [Copilot Artifacts](references/copilot-artifacts.md)
- [Task Tool Mechanics](references/task-tool-mechanics.md)
- [Delegation Templates](references/delegation-templates.md)
- [Workflow Contracts](references/workflow-contracts.md)
- [Eval Authoring](references/eval-authoring.md)
- [User Interaction](references/user-interaction.md)
- [Agent Template](assets/copilot/agent-template.md)
