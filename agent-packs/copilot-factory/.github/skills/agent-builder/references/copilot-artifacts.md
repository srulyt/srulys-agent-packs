# Copilot CLI Artifact Reference

Detailed specifications for GitHub Copilot CLI agent pack artifacts.

## Agent File (.agent.md)

### Location
`.github/agents/{agent-name}.agent.md`

### Format
Markdown with YAML frontmatter.

### Full Schema

```yaml
---
name: "Agent Name"                    # Optional: friendly/display name (human-readable, e.g. "Spec Author Orchestrator"). The `@invocation-slug` users type comes from the kebab-case FILENAME (e.g. `spec-author.agent.md` → `@spec-author`), NOT from this field. They MAY differ.
description: "What and when"          # Required: triggers + purpose
tools: ["read", "edit"]               # Optional: tool restrictions
disable-model-invocation: true        # Optional: prevent auto-select
user-invocable: true   # Optional: hide from /agents picker (sub-agents set false)
target: "vscode"                       # Optional: vscode or github-copilot
model: "gpt-4"                        # Optional: model override (IDE only)
---
```

> **`name:` vs `@invocation-slug`** — `name:` is the friendly display
> name (human-readable, e.g. `"Spec Author Orchestrator"`). The
> `@invocation-slug` users type derives from the kebab-case filename
> (e.g. `spec-author.agent.md` → `@spec-author`). They MAY differ; do
> not force `name:` to match the slug.

> **⚠️ YAML Safety — MANDATORY**
> The `description` value **MUST** always be wrapped in double quotes (`"..."`). Bare strings containing `:` (e.g. `Trigger keywords: foo`) cause a **"Nested mappings are not allowed in compact mappings"** parse error and the agent **will not load**.
> The YAML frontmatter (`---` block) **MUST** start at line 1 of the file.

### Model Selection

The optional `model` field lets you specify which LLM model an agent uses. Useful for:
- **Fast/cheap models** for reviewers, linters, simple transformations
- **Powerful models** for architects, complex reasoning, code generation

When omitted, the IDE default model is used. Model availability varies by environment.

### Required Fields

Only `description` is required. Must include:
1. What the agent does
2. When to use it
3. Trigger keywords

Example:
```yaml
description: "Creates unit tests for Python code. Use when asked to write tests, generate test cases, or add test coverage. Triggers on: test, pytest, unittest, coverage."
```

### Tool Aliases

| Alias | Includes | Use For |
|-------|----------|---------|
| `execute` | `shell`, `Bash`, `powershell` | Running commands |
| `read` | `Read`, `NotebookRead` | Reading files |
| `edit` | `Edit`, `MultiEdit`, `Write`, `NotebookEdit` | Creating/modifying files |
| `search` | `Grep`, `Glob` | Finding files/text |
| `web` | `WebSearch`, `WebFetch` | Web access |
| `vision` | `Vision` | Analyzing images and diagrams |
| `agent` | `custom-agent`, `Task` | Invoking other agents |
| `github/*` | All GitHub MCP tools | Repository operations |

### Tool Restriction Patterns

**Read-only**:
```yaml
tools: ["read", "search"]
```

**Implementation**:
```yaml
tools: ["read", "edit", "search"]
```

**Full access with delegation**:
```yaml
tools: ["read", "edit", "search", "execute", "agent", "github/*"]
```

**No tools** (advisory only):
```yaml
tools: []
```

### Subagent / Orchestrator Configuration

The two invocation flags are **orthogonal** — they gate different
sides of the invocation graph:

| Flag | Effect | Default |
|---|---|---|
| `disable-model-invocation: true` | Removes the agent from the **task-tool registry** exposed to the model — i.e., other agents cannot proxy-call it as a sub-agent. (Renamed from `infer`; controls "custom agent tool visibility" per the Copilot CLI changelog.) | `false` (model CAN invoke) |
| `user-invocable: false` | Hides the agent from the **`/agents` picker** so users cannot select/switch to it. (Per Copilot CLI changelog: "Hide custom agents with `user-invocable: false` from the `/agents` picker".) | `true` (user CAN invoke) |

**Rule for orchestrators** (user-facing entry points):
```yaml
disable-model-invocation: true   # block model-side proxy invocation
user-invocable: true             # default; users invoke with @name
```

**Rule for subagents** (delegation-only, called via `task`):
```yaml
user-invocable: false            # hide from /agents picker
# disable-model-invocation: ABSENT — sub-agents MUST stay in the
#   orchestrator's task-tool registry. Setting it removes the agent
#   from the registry and makes it un-invokable.
```

> Always pair `user-invocable: false` with a prompt-level invocation
> guard (see template). The picker flag does not block
> `--agent <name>` non-interactive invocation, so the prose guard is
> defence-in-depth.

### Agent Prompt Body

After the `---` closing the frontmatter:
- Maximum 30,000 characters
- Standard markdown formatting
- Include identity, responsibilities, outputs

### Examples

**Simple Agent**:
```markdown
---
name: Code Reviewer
description: "Reviews code for bugs, style issues, and best practices. Use when asked to review code, check for issues, or audit changes. Triggers on: review, audit, check code."
tools: ["read", "search"]
---

You are a code reviewer. Analyze code for:
- Logic errors
- Security vulnerabilities
- Performance issues
- Style violations

Provide specific, actionable feedback with line references.
```

**Orchestrator Agent**:
```markdown
---
name: Project Manager
description: "Coordinates development workflows across multiple specialists. Use for complex multi-step tasks requiring planning, implementation, and review."
tools: ["read", "edit", "search", "execute", "agent"]
disable-model-invocation: true
user-invocable: true
---

You are a project coordinator. For complex tasks:

1. Analyze requirements
2. Create implementation plan
3. Delegate to specialists via @{agent-name}
4. Verify deliverables
5. Report completion

Available specialists:
- @code-architect - Design decisions
- @code-engineer - Implementation
- @code-reviewer - Quality checks
```

**Subagent**:
```markdown
---
name: Implementation Specialist
description: "Implements features based on specifications. Called by Project Manager for coding tasks. Not for direct use."
tools: ["read", "edit", "search"]
user-invocable: false
---

You implement features based on provided specifications.

## Invocation Guard

You are invoked exclusively by `@project-manager` via the `task` tool.
If invoked by a user OR another agent (default Copilot CLI,
`general-purpose`, or any role-play proxy):
respond "Please use @project-manager to coordinate implementation. I
am a specialist agent invoked by the orchestrator." and take no
further action.

> Frontmatter rule: subagents set `user-invocable: false` (hides from
> `/agents` picker). They MUST NOT set `disable-model-invocation:
> true` — that would remove them from the orchestrator's task-tool
> registry. The prose guard above is defence-in-depth and catches
> `--agent <name>` non-interactive invocations.

## File Access Boundaries

| Permission | Allowed Paths |
|------------|---------------|
| **Read** | `.project-stm/sessions/{session-id}/` (specs, context), `.github/skills/` |
| **Write** | `src/` (implementation output), `.project-stm/sessions/{session-id}/artifacts/` (build manifest) |

**Do NOT write to**: `.github/agents/`, `.github/skills/`, or any path outside the designated output and session directories. If you need a file created elsewhere, return control to `@project-manager` with the request.

## Skills to Load

- `coding-standards` — language-specific coding conventions and quality rules

Expected input:
- Specification document path
- Target files/directories
- Quality requirements

Output:
- Created/modified files
- Summary of changes
- Any blockers encountered
```

### File Access Boundaries

Copilot CLI does not support path-scoped permissions at the runtime level. To prevent agents from writing outside their designated scope, include a **File Access Boundaries** section in every agent prompt.

**Format**:
```markdown
## File Access Boundaries

| Permission | Allowed Paths |
|------------|---------------|
| **Read** | `{paths agent may read from}` |
| **Write** | `{paths agent may write to}` |

**Do NOT write to**: {explicitly list forbidden paths}. If you need a file created elsewhere, return control to `@{orchestrator-name}` with the request.
```

**Common boundary patterns**:

| Agent Role | Read Scope | Write Scope |
|------------|-----------|-------------|
| Orchestrator | STM, output dir, skills | STM only |
| Architect/Designer | STM context, skills | STM artifacts only |
| Reviewer/Critic | STM, output dir, skills | STM artifacts only |
| Engineer/Builder | STM, skills/templates | Output dir + STM artifacts |

**Rules**:
- Every agent must have this section — including orchestrators
- Grant the narrowest write scope possible
- Explicitly list forbidden paths (don't just rely on "only X")
- Include fallback: "return control to @orchestrator with the request"

## Skill File (SKILL.md)

### Location
`.github/skills/{skill-name}/SKILL.md`

### Format
Markdown with YAML frontmatter.

### Schema

```yaml
---
name: "skill-name"                    # Required: identifier
description: "What and when"          # Required: triggers — MUST be double-quoted
license: "MIT"                        # Optional: license info
---
```

> **YAML Safety Rules**
> - `description` MUST always be wrapped in double quotes (`"..."`). Bare strings containing `:` (e.g. `Trigger keywords: foo`) cause a parse error.
> - The YAML frontmatter (`---` block) MUST start at line 1. Never wrap a SKILL.md in a code fence (e.g. ` ```skill `).

### Content Guidelines

- Maximum ~5,000 words in SKILL.md
- Use `references/` for detailed content
- Use `assets/` for templates, scripts
- Use `scripts/` for executable code

### Structure

```
{skill-name}/
├── SKILL.md                # Core instructions
├── references/             # Detailed documentation
│   ├── patterns.md
│   └── examples.md
├── assets/                 # Templates, images
│   └── template.md
└── scripts/                # Executable code
    └── helper.py
```

### Example

```markdown
---
name: api-design
description: "REST API design patterns and OpenAPI specification guidance. Use when designing APIs, writing OpenAPI specs, or reviewing API contracts. Triggers on: API, REST, OpenAPI, swagger."
---

# API Design Skill

Patterns for designing RESTful APIs.

## Quick Start

Use RESTful conventions:
- `GET /resources` - List
- `POST /resources` - Create
- `GET /resources/{id}` - Read
- `PUT /resources/{id}` - Update
- `DELETE /resources/{id}` - Delete

## Detailed References

- [OpenAPI Patterns](references/openapi.md)
- [Error Handling](references/errors.md)
- [Versioning Strategies](references/versioning.md)
```

## Custom Instructions

### Location
`.github/instructions/{name}.instructions.md`

### Format
Markdown with optional `applyTo` frontmatter.

### Schema

```yaml
---
applyTo: "**/*.py"           # Optional: glob pattern
---
```

### Example

```markdown
---
applyTo: ".copilot-factory/**"
---

## Factory Context

This workspace uses the Copilot Factory pattern.

- Sessions in `.copilot-factory/sessions/`
- State in `state.json`
- Artifacts in `artifacts/`
```

### applyTo Behavior

- When `applyTo` is set, the instructions are included only when the user is working with files matching the glob pattern
- Standard glob syntax: `*` matches within a directory, `**` matches across directories
- When `applyTo` is omitted, the instructions are always included as context
- Only one `applyTo` pattern per file; use multiple instruction files for multiple patterns

## Prompt Files (.prompt.md)

### Location
`.github/prompts/{prompt-name}.prompt.md`

### Format
Markdown with YAML frontmatter.

### Schema

```yaml
---
description: "What this prompt does"   # Required: shown in prompt picker
agent: "Agent Name"                    # Optional: route to specific agent
---
```

### Purpose

Reusable prompt templates for common workflows. Users invoke them from the prompt picker or command palette. Useful for:
- Guided multi-step workflows (e.g., "create a new feature")
- Pre-filled context for repetitive tasks
- Routing complex requests to the right agent

### Example

```markdown
---
description: "Create a new agent pack using the Copilot Factory workflow"
agent: "Copilot Factory"
---

## Create Agent Pack

I need you to create a new agent pack.

**Mode**: `creation`

### Requirements

- Describe the agents needed and their responsibilities
- Include any specific tool requirements or constraints
```

## Memory Files

### Location
`.github/memory/*.md`

### Purpose

Persistent storage for cross-session learnings. Memory files survive between conversations and are automatically loaded as context. Useful for:
- Recording architectural decisions and rationale
- Tracking patterns that work well in a codebase
- Storing user preferences discovered during sessions
- Accumulating domain-specific knowledge

### Format

Plain markdown. No frontmatter required. Content is appended over time.

### Guidelines

- Keep entries concise and factual
- Use timestamped entries for traceability
- Organize by topic (one file per knowledge domain)
- Periodically prune stale or superseded entries

### Example

```markdown
# Architecture Decisions

## 2026-03-10 — Agent topology
Hierarchical pattern chosen over flat because specialists need coordinated sequencing.

## 2026-03-12 — State management
Session-based STM with JSON state files. Filesystem-based for recovery.
```

### Structure

```
.github/memory/
├── decisions.md          # Key decisions and rationale
├── patterns.md           # Patterns that work well
└── preferences.md        # User/project preferences
```

## Directory Structure

Complete Copilot CLI pack:
```
{pack-name}/
├── .github/
│   ├── agents/
│   │   ├── main-agent.agent.md
│   │   └── sub-agent.agent.md
│   ├── skills/
│   │   └── {skill-name}/
│   │       ├── SKILL.md
│   │       └── references/
│   ├── instructions/               # Optional: file-scoped context
│   │   └── workspace.instructions.md
│   ├── prompts/                    # Optional: reusable workflows
│   │   └── common-task.prompt.md
│   └── memory/                     # Optional: persistent learnings
│       └── decisions.md
├── README.md
└── .{state-dir}/                   # Optional: state management
```

## Validation Checklist

- [ ] All agents have `description` in frontmatter
- [ ] All `description` values are double-quoted (YAML safety)
- [ ] Tool aliases are correct (`edit` not `write`)
- [ ] Agent prompts under 30,000 characters
- [ ] Skills under 5,000 words
- [ ] Descriptions include trigger keywords
- [ ] Orchestrators set `disable-model-invocation: true` AND have `user-invocable: true` (default; explicit recommended)
- [ ] Subagents set `user-invocable: false` and do **NOT** set `disable-model-invocation: true` (so the orchestrator can invoke them via `task`)
- [ ] Subagents have invocation guard section that refuses BOTH direct user invocation AND non-orchestrator agent proxying
- [ ] Every agent has "File Access Boundaries" section with read/write path table
- [ ] Each agent has "Skills to Load" section if it references skills
- [ ] Agent prompts reference skills rather than duplicating their content
- [ ] Orchestrator agents include iteration protocol and retry bounds
- [ ] README accurately reflects all agents, skills, and implementation details
- [ ] Prompt files have `description` and optional `agent` field
- [ ] Memory files (if used) are plain markdown, no frontmatter
- [ ] File paths follow conventions
