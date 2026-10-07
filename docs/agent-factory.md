# Agent Factory: minimal customization

The [new adjacent factory](../agent-packs/agent-factory/README.md) creates or modernizes reusable agent customizations using one portable skill. It does not replace the Copilot/Roo factories, and defines no planner/researcher/engineer/reviewer organization.

| Missing requirement | Representation |
| --- | --- |
| Nothing missing from the default environment | No artifact; useful task request |
| Broad repository invariant | Small scoped instruction |
| Specialized reusable judgment/knowledge | Skill and relevant resources |
| Repeated invocation with inputs | Prompt in a supported format |
| Enduring isolated context/tools/permissions | Native specialist profile |
| Missing operation/data source | Tool/MCP |
| Mandatory execution/enforcement | Hook/code/policy |
| Distribution | Plugin/package containing only justified components |

## Migration without losing expertise

The factory distinguishes domain knowledge, product facts, constraints, output contracts, examples, capabilities, deterministic policy, useful guidance, compatibility material, and obsolete scaffolding within source text. Meaningful approval/order and output contracts survive; generic choreography can disappear.

Actual migrations record original capability, source rules and destinations, removed material with rationale, uncertain legacy behavior, retained host dependencies and recommended evals. Contradictory or dated assertions are surfaced, not silently rewritten as current guarantees.

Declared canonical source rules take precedence over conflicting examples or subordinate instructions. An unresolved business choice remains conditional. Inspection-only restrictions do not authorize removing a useful utility: retain its capability unless a native equivalent is verified or the user approves the scope change.

## Harness compatibility and native orchestration

Portable skills and the Copilot/Codex Agent Plugins core share one canonical knowledge tree. Claude Code has a thin native manifest. Profiles, prompts, instructions, tools, hooks, permission enforcement and context inheritance remain surface-specific. Runtime subagents are the harness's concern; custom profiles and explicit domain workflow are separately justified.

First-party platform references are dated and refreshed for capability/schema/model changes, substantial redesigns or observed duplication. The skill has no permanent model pin, vendor-specific reasoning recipe, or recurring web-research phase.

## Availability and evaluation

Run `init.cmd` to install only the new skill into `.github\skills\agent-factory`. No separate Node.js installer is needed. Matching installed skill files are overwritten; review local edits first. Legacy source packs and existing legacy installations are left alone. Other hosts can copy the canonical skill to their native project skill directory.

[Evaluation documentation](../evals/packs/agent-factory/README.md) distinguishes structural/discovery checks, live behavioral exercises, old/modern/bare comparisons, ablation, and runtime/integration limitations. A shorter prompt is not sufficient proof of preserved task quality.
