---
name: agent-builder
description: "Templates and patterns for creating GitHub Copilot CLI artifacts. Use when generating custom agents or skills. Keywords: agent.md, SKILL.md, implementation."
---

# Agent Builder Skill

Templates and patterns for implementing multi-agent systems.

## When to Use This Skill

Load this skill when:
- Writing `.agent.md` files (Copilot CLI)
- Building `SKILL.md` files (Copilot CLI)
- Creating README documentation

## Copilot CLI Artifacts

> **⚠️ CRITICAL — YAML `description` Quoting Rule**
>
> Every `description` value in `.agent.md` and `SKILL.md` frontmatter **MUST** be wrapped in double quotes.
> Bare strings containing `:` (e.g. `Trigger keywords: foo`) cause a **"Nested mappings are not allowed in compact mappings"** YAML parse error and the agent **will not load**.
>
> ✅ `description: "Orchestrates workflows. Trigger keywords: build, deploy."`
> ❌ `description: Orchestrates workflows. Trigger keywords: build, deploy.`
>
> This is the single most common cause of agent load failures. **Always quote. No exceptions.**

For detailed Copilot patterns, see [references/copilot-artifacts.md](references/copilot-artifacts.md).

### Canonical `.agent.md` Frontmatter Schema (Single Source of Truth)

This is the **authoritative** list of frontmatter keys supported by the
Copilot CLI agent loader in this codebase. Both `@factory-engineer`
(pre-emit) and `@factory-critic` (review-pass) MUST validate every
generated `.agent.md` against this list. Unknown keys are a build bug —
the loader may silently ignore them or reject the file outright.

**Supported keys** (all others are unknown and MUST be rejected):

| Key | Required | Type | Notes |
|---|---|---|---|
| `name` | recommended | string | **Friendly / display name** for the agent (e.g. `"Spec Author Orchestrator"`). Human-readable; quoted strings with spaces are fine. The user-facing invocation slug (`@spec-author`) is derived from the **kebab-case filename** (`spec-author.agent.md`), NOT from this field. `name:` and the filename slug MAY differ. Do NOT force `name:` to match the filename slug. |
| `description` | **required** | string (double-quoted) | Triggers + purpose. MUST be wrapped in `"..."`. |
| `tools` | optional | list of strings | Tool aliases (`read`, `edit`, `search`, `execute`, `agent`, `web`, `vision`, `github/*`). |
| `disable-model-invocation` | optional | bool | Orchestrators set `true`; subagents MUST omit. |
| `user-invocable` | optional | bool | Subagents set `false`; orchestrators set `true` (default). |
| `model` | optional | string | Model override (IDE only). |
| `target` | optional | string | `vscode` or `github-copilot`. |

Sources used to derive this list:
- `agent-packs/copilot-factory/.github/skills/agent-builder/references/copilot-artifacts.md` (full schema block).
- The working orchestrator `agent-packs/copilot-factory/.github/agents/copilot-factory.agent.md` and all five `factory-*`, `eval-judge` sibling agents — none use any other keys.

**NOT supported** — do NOT emit these in frontmatter. Place
human-readable labels in the canonical `name:` field instead — see the
Supported keys table above.

| Unsupported key | Rationale |
|---|---|
| `display-name` | **Worked anti-example.** Added by session `2026-05-04-3f8b21ac` finding F1 to provide a friendly label, then doubled-down on by session `2026-05-04-b8a05c19` which forced the friendly name into the body H1 only. **Both are wrong.** Copilot CLI's loader has no `display-name` field, but the friendly name DOES have a home: the canonical `name:` field accepts human-readable strings (e.g. `name: "Spec Author Orchestrator"`). The invocation slug is the kebab-case **filename** (`spec-author.agent.md` → `@spec-author`), independent of `name:`. Use `name:` for the friendly label; do not invent `display-name`. |
| `title` / `label` / `friendly-name` | Same reason — no loader support. The friendly label belongs in `name:`. |
| `version` / `author` / `tags` | No loader support. Track in README or memory files instead. |
| `aliases` | No loader support. The `@invocation-slug` is the kebab-case filename, not an alias field. |

When in doubt: if the key is not in the **Supported keys** table
above, it MUST NOT appear in `.agent.md` frontmatter.

### Quick Reference

**.agent.md** format:
```markdown
---
name: Agent Name
description: "What it does. When to use. Trigger keywords."
tools: ["read", "edit", "search"]
---

Agent prompt body (max 30,000 chars)
```

**SKILL.md** format:
```markdown
---
name: skill-name
description: "What skill does. Trigger keywords."
---

# Skill Title

Instructions (max 5,000 words)
```

### Tool Aliases (Copilot CLI)
| Alias | Purpose |
|-------|---------|
| `execute` | Shell commands |
| `read` | Read files |
| `edit` | Create/modify files |
| `search` | Find files/text |
| `web` | Fetch URLs |
| `vision` | Analyze images/diagrams |
| `agent` | Invoke other agents |

**Built-in tools** (always available, do NOT declare in `tools:`):
- `ask_user` — present a structured question to the user with optional `choices[]`. See [User Interaction](references/user-interaction.md) for the canonical policy on when to use it.

### Additional Copilot Artifacts

**.prompt.md** (reusable workflow templates):
```markdown
---
description: "What this prompt does"
agent: "Agent Name"
---

Prompt body with instructions
```

**Memory files** (`.github/memory/*.md`):
- Plain markdown, no frontmatter
- Persistent cross-session learnings
- Organized by topic (decisions.md, patterns.md, etc.)

For detailed specs on all artifact types, see [references/copilot-artifacts.md](references/copilot-artifacts.md).

## Template Assets

- [assets/copilot/agent-template.md](assets/copilot/agent-template.md)
- [assets/copilot/skill-template.md](assets/copilot/skill-template.md)

## Quality Checklist

- [ ] `description` field present (required)
- [ ] **`description` value is always wrapped in double quotes** — bare strings containing `:` cause YAML parse errors (e.g. `description: "... Trigger keywords: foo, bar."`)
- [ ] **YAML frontmatter starts at line 1** — never wrap it in a code fence (` ```skill ` or similar)
- [ ] **Frontmatter contains ONLY keys from the Canonical Frontmatter Schema** — see the supported-keys table above. Unknown keys (e.g. `display-name`, `title`, `version`) are a build bug. No duplicate keys. YAML must parse cleanly.
- [ ] `tools` uses correct aliases
- [ ] Agent prompt under 30,000 characters
- [ ] Skill under 5,000 words
- [ ] User-facing agent descriptions include trigger keywords. Sub-agents
      (those invoked only via `task`) MAY omit trigger keywords since
      they are bound by `agent_type` (frontmatter `name`), not by
      description matching.
- [ ] Subagents have invocation guard redirecting to orchestrator
- [ ] Each agent has explicit "Skills to Load" section if it uses skills
  > Note: In Copilot CLI, skills are matched by `description` keywords. The "Skills to Load" section documents intent and aids the model in referencing the right skill. Ensure skill `description` fields contain keywords that match the agent's use case.
- [ ] Agent prompts reference skills rather than duplicating their content
- [ ] Every agent has a "File Access Boundaries" section with read/write path table
- [ ] README has clear usage instructions
- [ ] README counts/names/descriptions match actual artifacts
- [ ] All file paths are correct
- [ ] Build manifest is accurate
- [ ] Orchestrator has iteration protocol for user feedback
- [ ] Orchestrator has retry bounds on specialist re-requests
- [ ] Every agent has a `## Must NOT` (negative-scope) section enumerating
      forbidden actions, file paths, sub-agent re-invocations, and
      verdict-tampering (for reviewers)
- [ ] Every sub-agent has a machine-parseable `## Output Contract`
      using named fenced sections (e.g. ```verdict ...```)
- [ ] Orchestrator parses each sub-agent's fenced output before
      transitioning phase
- [ ] Orchestrator surfaces hard iteration caps (max 2 re-requests
      per artifact per review type) and persists counters in state
- [ ] Generated pack ships with `evals/packs/<pack>/spec.yaml` and at
      least one case at `evals/packs/<pack>/cases/smoke-*/`
      (see [Eval Authoring](references/eval-authoring.md))
- [ ] Engineer build manifest lists eval artifacts under
      `files_created` / `files_modified` and `evals_created`
- [ ] Critic verifies eval artifacts exist and reference paths
      resolve; missing eval artifacts are BLOCKING in implementation
      review
- [ ] Skill-visibility rule applied to every piece of extracted
      content (see system-design skill's
      [skill-visibility reference](../system-design/references/skill-visibility.md))
- [ ] For generated orchestrators: prompt contains both
      `## How to Delegate (Task Tool Mechanics)` and
      `## Hard Delegation Rule (STOP-and-delegate)` sections per
      [Task Tool Mechanics](references/task-tool-mechanics.md), and
      `tools:` is narrowest possible (no `["*"]`, no unjustified
      `execute`)
- [ ] User-facing questions with an enumerable answer set use
      `ask_user(choices=[...])` rather than prose-and-wait-for-reply;
      critical / irreversible gates set `allow_freeform: false`; no
      `"Other"` choice strings; one question per `ask_user` call;
      sub-agents do not call `ask_user` (they emit `open-questions`
      fenced blocks for the orchestrator to surface). See
      [User Interaction](references/user-interaction.md).

## Common Patterns

### Read-Only Agent
`tools: ["read", "search"]`

### Implementation Agent
`tools: ["read", "edit", "search"]`

### Orchestrator Agent (default)
`tools: ["read", "edit", "search", "agent"]`

Add `execute` only with architectural justification documented in the
generated pack's architecture document. `tools: ["*"]` is valid
Copilot CLI syntax (means "all tools") but is a pack-level
anti-pattern — narrow tools are required for predictable behaviour.

### Subagent (Agent-Only Invocation)
For sub-agents that should only be reachable via `task` delegation:

```yaml
user-invocable: false   # hides from /agents picker; users cannot select
# disable-model-invocation: ABSENT — sub-agents must remain in the
#   orchestrator's task-tool registry so it can call them.
```

`disable-model-invocation: true` controls **tool visibility to the
model** (the renamed `infer` flag — see Copilot CLI changelog: "Add
`infer` property to control custom agent tool visibility"; "Custom
agents use `disable-model-invocation` instead of `infer` (backward
compatible)"). Setting it on a subagent removes it from the calling
orchestrator's `task` / `agent_type` registry, making the subagent
un-invokable. Do **not** set it on subagents.

`user-invocable: false` is orthogonal: it hides the agent from the
`/agents` picker (Copilot CLI changelog: "Hide custom agents with
`user-invocable: false` from the `/agents` picker"). This is the
correct flag to prevent direct user invocation of a delegation-only
subagent.

As defence-in-depth, keep the prompt-level invocation guard
redirecting any direct user invocation back to the orchestrator —
this also covers `--agent <name>` non-interactive invocation, which
the picker flag does not block.

### Orchestrator (User-Facing)
```yaml
disable-model-invocation: true   # blocks model-side / sub-agent proxy invocation
user-invocable: true             # default; users invoke explicitly with @name
```

Setting `disable-model-invocation: true` on the orchestrator prevents
**other agents** (and the default Copilot CLI agent) from proxy-calling
it via the `task` tool. Users still invoke it explicitly with
`@orchestrator-name` from the `/agents` picker. This is the correct
setting for an entry-point orchestrator that should only run when the
user asks for it by name.

### Quick reference table

| Role | `disable-model-invocation` | `user-invocable` | Effect |
|---|---|---|---|
| Orchestrator | `true` | `true` (default) | User-only entry; cannot be proxy-called by other agents |
| Sub-agent | absent (default `false`) | `false` | Orchestrator-callable via `task`; hidden from user picker |

### File Access Boundaries

Every agent must have explicit path-scoped read/write boundaries. Add a "File Access Boundaries" table in the agent prompt (prompt-level guardrail):

```markdown
## File Access Boundaries

| Permission | Allowed Paths |
|------------|---------------|
| **Read** | `.my-stm/sessions/{session-id}/`, `.github/skills/` |
| **Write** | `.my-stm/sessions/{session-id}/artifacts/` only |

**Do NOT write to**: `src/`, `.github/agents/`, or any path outside the session artifacts directory.
```

**Rules**:
- Grant narrowest write scope possible per agent role
- Orchestrators: write only to STM directories
- Reviewers/critics: write only to STM artifacts
- Engineers: write to output dir + STM artifacts
- Agents exceeding their boundary must return control to the orchestrator

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Missing description | Agent won't trigger | Always include clear description |
| Too many tools | Security risk | Grant minimum needed |
| Huge prompts | Slow, unfocused | Defer to skills |
| No README | Unusable pack | Always include setup guide |
| Duplicated skill content in agents | Wasted tokens, maintenance drift | Reference skills, don't copy them |
| Missing invocation guard on subagent | Users bypass orchestrator | Add guard redirecting to orchestrator |
| No explicit skill loading section | Implicit dependencies | Add "Skills to Load" section to each agent |
| No iteration protocol in orchestrator | No path for user feedback | Add iteration and retry sections |
| No file access boundaries | Agents write outside scope, crash silently | Add File Access Boundaries section per agent |
| README drift from implementation | Misleading documentation | Verify README matches actual artifacts |
| Prose question + wait for free-text reply | Loses structured UI, brittle parsing of user input | Call `ask_user(question=..., choices=[...])`; see [User Interaction](references/user-interaction.md) |
| Sub-agent calling `ask_user` directly | Breaks orchestrator-only-talks-to-user delegation model | Sub-agent emits `open-questions` fenced block; orchestrator surfaces via `ask_user` |
| Including `"Other"` in `ask_user` choices | UI auto-adds freeform when `allow_freeform=true`; duplicates affordance | Omit `"Other"`; rely on `allow_freeform` |

## References

- [Copilot Artifacts](references/copilot-artifacts.md) - Detailed Copilot CLI formats
- [Delegation Templates](references/delegation-templates.md) - Orchestrator delegation patterns
- [Eval Authoring](references/eval-authoring.md) - Eval spec + case scaffolding for generated packs
- [Task Tool Mechanics](references/task-tool-mechanics.md) - Required orchestrator delegation sections + worked-example shapes
- [User Interaction](references/user-interaction.md) - `ask_user` tool policy: when to use structured choices vs freeform, anti-patterns, sub-agent boundary
