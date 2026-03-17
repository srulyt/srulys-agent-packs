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
name: "Agent Name"                    # Optional: display name
description: "What and when"          # Required: triggers + purpose
tools: ["read", "edit"]               # Optional: tool restrictions
disable-model-invocation: true        # Optional: prevent auto-select
target: "vscode"                       # Optional: vscode or github-copilot
model: "gpt-4"                        # Optional: model override (IDE only)
---
```

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

### Subagent Configuration

For agents that should only be called by other agents:
```yaml
disable-model-invocation: true
```

This prevents:
- Auto-selection based on user prompt
- Direct invocation by name

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
disable-model-invocation: true
---

You implement features based on provided specifications.

## Invocation Guard

Do not invoke directly. If a user invokes you, respond:
"Please use @project-manager to coordinate implementation. I am a specialist agent invoked by the orchestrator."

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
mode: "agent"                          # Optional: agent | edit | ask
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
- Specify target platform: `roo` or `copilot`
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
- [ ] Subagents have `disable-model-invocation: true`
- [ ] Subagents have invocation guard section
- [ ] Each agent has "Skills to Load" section if it references skills
- [ ] Agent prompts reference skills rather than duplicating their content
- [ ] Orchestrator agents include iteration protocol and retry bounds
- [ ] README accurately reflects all agents, skills, and implementation details
- [ ] Prompt files have `description` and optional `agent` field
- [ ] Memory files (if used) are plain markdown, no frontmatter
- [ ] File paths follow conventions
