---
name: agent-factory
description: "Create reusable agent customizations or semantically modernize an existing agent pack/plugin. Use for requests to design, build, simplify, or migrate skills, instructions, specialist profiles, or agent plugins; not ordinary coding, task execution, or document authoring."
---

# Agent Factory

Supply the knowledge, capabilities, constraints, and output contracts missing from the user's agent environment. Do not simulate intelligence. A clear task request and **no customization** may be the best deliverable.

## Selection contract

Identify the desired outcome and the delta from the default model, repository context, existing customizations, and native tools. Every emitted component needs a concrete reason to exist.

| Need | Smallest fitting primitive |
| --- | --- |
| No meaningful delta | Nothing; return a useful task request, without creating files |
| Small, broadly applicable invariant | Scoped repository instructions |
| Reusable specialized knowledge or judgment | Skill with relevant references/examples |
| Convenient invocation/variable inputs | Reusable task prompt, in a supported host format |
| Recurring isolated context or distinct tool/permission boundary | Target-specific custom agent |
| Missing data source or operation | Tool/MCP integration |
| Mandatory execution, validation, or policy | Deterministic code, hook, or enforced policy |
| Distribution | Package only the justified components |

Keep always-loaded context small. Prefer goals, invariants, examples, and completion criteria to reasoning procedures. Do not invent required research/planning/review phases, agent counts, personas, retry loops, or session state. Runtime subagents and execution strategy belong to the model/harness; reusable custom profiles require enduring specialization. Preserve ordered domain procedures and required approvals when their order is itself necessary.

## Preservation and safety

Modernization preserves the original user-visible capability, business rules, product facts, templates, valuable examples, utilities, and safety/permission boundaries. Classify meaning, not file extensions; a workflow paragraph can contain both obsolete choreography and an essential rule.

Record preserved information with source sections and new destinations, removed scaffolding with reasons, uncertain legacy behavior, remaining host dependencies, and recommended evals. Honor explicit source precedence; unresolved conflicting operations need resolution, not an invented default. Do not delete uncertain material or change the original pack unless authorized.

Prompt instructions are not enforcement. Do not invent tools, credentials, model IDs, supported fields, or permissions. A packaging/static check is not proof of runtime discovery, task quality, or an enforced boundary.

## Select resources by need

- Primitive tradeoffs and anti-pattern signals: [selection](references/selection.md).
- Existing-pack archaeology and migration evidence: [modernization](references/modernization.md), [migration record](assets/migration-record.md).
- Representative tasks, bare baselines, ablation, and activation: [evaluation](references/evaluation.md).
- Target compatibility: [Copilot](references/copilot.md), [Codex](references/codex.md), [Claude](references/claude.md).
- Changed platform assumptions: [freshness](references/freshness.md); research only affected assumptions using current official sources.
- Exact artifact examples: [portable skill](assets/skill-template.md), [task request](assets/task-request.md), [Copilot specialist](assets/specialist-copilot.md), [Codex specialist](assets/specialist-codex.toml), [Claude specialist](assets/specialist-claude.md). These are optional shapes, not a required artifact roster.

Completion means the selected components supply the identified delta, meaningful rules survived any migration, representative tasks support the selection, and installation/use and remaining uncertainty are clear. For no customization, a concise explanation and task request suffice; do not manufacture a pack or audit directory.
