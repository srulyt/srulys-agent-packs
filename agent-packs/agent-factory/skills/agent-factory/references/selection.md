# Choosing the smallest useful customization

The question is not "how many agents does this task need?" It is "what does the default environment lack?"

| Primitive | Evidence that earns it | Evidence against it |
| --- | --- | --- |
| Nothing | Normal repository context and native capabilities suffice | A real missing rule, data source, contract, or isolation requirement |
| Instructions | A short fact/invariant applies almost universally within its scope | Task-specific expertise; long references; competing instruction scopes |
| Skill | Specialized reusable knowledge, examples, decisions, templates, or domain procedure | A single convenience prompt or generic coding advice |
| Prompt | Repeating an invocation with inputs is the actual need | Duplicates a skill or introduces another routing layer |
| Custom agent | Recurring specialist context, an independently useful execution boundary, or genuinely different tools | Personality, complexity alone, generic research/review/testing, a historical role name |
| Tool/MCP | An operation/data source is absent from available tools | Existing tools already provide it; prose pretending to access live systems |
| Hook/code/policy | An action/check must happen deterministically | A preference for model behavior rather than a requirement to enforce |
| Package | Components need distribution/versioning | Extra components added solely to make the package look complete |

A requirement can need more than one primitive: unavailable proprietary data may need MCP and a skill containing interpretation rules. Explain each independent delta; do not use packaging to justify a hierarchy.

## Three different kinds of multi-agent behavior

- **Runtime subagents:** the harness/model chooses a bounded delegation for the current task. No persistent specialist definition is implied.
- **Custom agents:** reusable configuration for an enduring specialist, context, tool, or permission distinction.
- **Explicit orchestration:** a workflow whose fixed ordering/topology is part of the actual requirement. Rare; justify it independently.

An intelligent default agent can apply multiple kinds of judgment. Do not add delegation hints unless observed failures show they improve the target model/harness. Never assume conversation history, invoked skills, or repository instructions automatically reach subagents.

## Instruction collision and context cost

An instruction earns its scope only if it is necessary, unavailable elsewhere, relevant there, and unlikely to conflict. A template, example, deterministic check, or relevant reference often communicates more precisely than another imperative paragraph.

Keep descriptions narrow enough to distinguish customization creation from using the generated customization. Knowledge has one canonical home; deployment copies can be generated, but must not become independently edited vendor forks.

## Signals, not automatic deletion rules

Investigate fake organizations/personality-only agents; planner/researcher/architect/implementer/reviewer pipelines without isolation; fixed subagent counts; recursive routing; always-delegate rules without a capability boundary; huge always-on context; broad triggers; common-knowledge skills; duplicated rules; forced phases; exhaustive discovery for small work; obsolete model workarounds; generic thinking/testing/verification commands; excess agent-only documentation; thought-stage state machines; and common-sense prompt novels.

Extract embedded real constraints before removing scaffolding. "Review before publishing" can be a compliance obligation; "always invoke the reviewer persona" may be merely one old implementation of it.

## Examples of different outcomes

- Fixing a bug in a conventional repo: usually no customization, just a clear request.
- A reusable incident brief with proprietary severity definitions: one narrow skill with a template.
- A repository-wide immutable customer-ID convention: a small scoped instruction, not an incident skill.
- A recurring audit that needs isolated confidential context and dedicated read-only tools: a custom specialist with native tool restrictions, not a five-agent factory.
- A production release requiring approval before irreversible migration: preserve the runbook order and actual approval/enforcement mechanism.
