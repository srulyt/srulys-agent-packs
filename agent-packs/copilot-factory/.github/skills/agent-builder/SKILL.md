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
disable-model-invocation: true   # blocks auto-selection by the model
user-invocable: false            # blocks direct user selection
```

Both fields are platform-supported (see [Copilot docs](https://docs.github.com/en/copilot/reference/custom-agents-configuration)).
The agent remains invokable via `task` / `agent_type` — these flags
do **not** remove it from the calling agent's task registry, contrary
to a previously documented (incorrect) claim. As defence-in-depth,
keep the prompt-level invocation guard redirecting any direct user
invocation back to the orchestrator.

### Orchestrator (User-Facing)
`disable-model-invocation: true`
Set this on the user-facing orchestrator to prevent **automatic**
model-driven routing to it. Users can still invoke it explicitly with
`@orchestrator-name`. This is the correct setting for an entry-point
orchestrator that should only run when the user asks for it by name.

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

## References

- [Copilot Artifacts](references/copilot-artifacts.md) - Detailed Copilot CLI formats
- [Delegation Templates](references/delegation-templates.md) - Orchestrator delegation patterns
- [Eval Authoring](references/eval-authoring.md) - Eval spec + case scaffolding for generated packs
- [Task Tool Mechanics](references/task-tool-mechanics.md) - Required orchestrator delegation sections + worked-example shapes
