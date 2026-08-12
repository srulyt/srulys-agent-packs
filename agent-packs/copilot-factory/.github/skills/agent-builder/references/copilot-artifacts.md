# Copilot Artifact Compatibility Reference

## Baseline

| Field | Value |
|---|---|
| Factory baseline ID | `factory-cli-2026-08-12` |
| Documentation checked | 2026-08-12 |
| Copilot CLI executable/version | unavailable / unverified |
| Runtime tested here | No |
| Runtime compatibility status | **unverified**; no Copilot CLI executable or run evidence was available |
| Validation performed | targeted static frontmatter/schema/contracts, pack lint, Eval Pilot lint, guarded-wrapper unit tests |
| Primary documentation | [Configuring custom agents](https://docs.github.com/en/copilot/customizing-copilot/custom-agents/configuring-custom-agents), [Copilot CLI](https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli), [Agent Skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) |

This is a **Factory-supported** baseline, not a universal schema. Re-check the
target host/version before changing the matrix or using a field marked
conditional.

## Surface Compatibility Matrix

`S` = Factory-supported for the tested CLI baseline, `C` = documented but
surface/version conditional, `—` = not selected for that artifact/surface.

| Capability | Copilot CLI baseline | VS Code custom agent | GitHub.com coding agent | Factory rule |
|---|---:|---:|---:|---|
| Markdown + YAML custom agent | S | C | C | target must be declared |
| `name`, `description`, `tools` | S | C | C | description double-quoted |
| `disable-model-invocation` | S | C | C | orchestrator true only after target check |
| `user-invocable` | S | C | C | subagent false only after target check |
| `model` | C | C | C | omit by default; availability-check |
| `target` | C | C | C | use only for a documented surface |
| `task`/agent delegation | S | C | C | CLI semantics in task reference |
| `SKILL.md` Agent Skills | S | C | C | progressive disclosure by relevance |
| repository/path instructions | C | S | C | preferred deterministic context |
| MCP tools | C | C | C | requirement, trust/auth, fallback decision |
| Copilot Memory product | C | C | C | availability-dependent; not local files |

Host behavior and rollout can change. A generated architecture selects one
column and records any compatibility assumptions. The critic rejects a field
only when unsupported in that selected column/baseline, not merely because it
is absent from a different surface.

If `copilot` is unavailable in a future validation environment, set runtime
compatibility explicitly to **unverified**; a static lint result must never be
reported as smoke-load success.

## Factory-Supported Agent Frontmatter

```yaml
---
name: "Human-readable name"
description: "Purpose and when to use it."
tools: ["read", "edit", "search"]
disable-model-invocation: true
user-invocable: true
model: "<available target model>"
target: "<documented target>"
---
```

Supported keys for `factory-cli-2026-08-12`:

| Key | Required | Validation |
|---|---|---|
| `name` | recommended | human-readable; invocation slug is filename |
| `description` | yes | string, explicitly double-quoted |
| `tools` | no | target-supported aliases, minimum needed |
| `disable-model-invocation` | no | user entry only; subagents omit |
| `user-invocable` | no | delegation-only subagents set false |
| `model` | no | conditional; target availability recorded |
| `target` | no | conditional; selected surface recorded |

Reject duplicate keys and keys unsupported by the selected target. Friendly
labels belong in `name`; do not invent `display-name`, `title`, aliases, tags,
or version fields for this baseline.

### Invocation roles

```yaml
# user-facing orchestrator
disable-model-invocation: true
user-invocable: true

# delegation-only subagent
user-invocable: false
# disable-model-invocation is absent
```

Pair subagents with a two-sided prompt guard. These flags are the selected
Factory baseline policy, but runtime behavior remains unverified here;
revalidate them against an available CLI when the baseline changes.

## Tools

Factory aliases for the CLI baseline:

| Alias | Purpose |
|---|---|
| `read` | read files |
| `edit` | create/modify files |
| `search` | locate files/text |
| `execute` | shell; grant only when role requires it |
| `agent` | task delegation |
| `web`, `vision` | optional target capabilities |
| host/MCP-qualified tools | conditional; never assume `github/*` is universal |

`["*"]` is not allowed for generated coordinators. Tool grants do not enforce
path scope, so prompts must contain explicit read/write boundaries.

## Skill Frontmatter

```yaml
---
name: "skill-name"
description: "What the skill provides and when it is relevant."
license: "MIT"
---
```

Only `name`, `description`, and optional `license` are Factory-supported.
Descriptions are double-quoted; frontmatter starts on line 1. Put detail in
`references/`, assets in `assets/`, and scripts in `scripts/`.

## Instructions and Prompts

- Deterministic repository context uses the host's documented repository-wide
  or path-specific custom-instruction mechanism. `applyTo` behavior is
  host-specific and must be checked for the selected surface.
- `.prompt.md` support is surface-specific. Where supported, use quoted
  `description` and a documented `agent` route.

## Memory

`.github/memory/*.md` has no documented automatic-loading guarantee in the
custom-instructions contract. The Factory may preserve it as a local file
convention only when an authorized agent explicitly reads it. State-critical
decisions belong in the session STM or supported custom instructions.

[Copilot Memory](https://docs.github.com/en/copilot/concepts/agents/copilot-memory)
is a distinct GitHub capability with rollout and surface availability that may
change. Do not equate it with a local folder or promise it will be present.

## MCP Decision

When requirements need an external capability:

1. Check whether built-in target tools already satisfy it.
2. If MCP is required, document capability, host support, server trust,
   authentication/secrets, minimum exposed tools, data boundary, and fallback.
3. Emit `none` when no MCP capability is required; never speculate a server.

See [Extending Copilot Chat with MCP](https://docs.github.com/en/copilot/customizing-copilot/extending-copilot-chat-with-mcp)
(retrieved 2026-08-12).

## Model Decision

Inherit the target default unless a requirement states an outcome needing an
override. Verify surface/plan availability at execution time, record the
resolved model when exposed, and consider cost/multiplier and eval
comparability. Do not encode a permanent model ranking or stale example name.

See [Supported AI models](https://docs.github.com/en/copilot/reference/ai-models/supported-models)
(retrieved 2026-08-12).

## Validation

- parse frontmatter and reject duplicate/target-unsupported keys;
- quote descriptions and keep agent body below 30,000 characters;
- validate role flags, two-sided guards, minimum tools, and path boundaries;
- smoke-load with the pinned/selected CLI when available; if unavailable,
  report that limitation rather than claiming runtime compatibility;
- re-version the baseline when field or task behavior changes.
