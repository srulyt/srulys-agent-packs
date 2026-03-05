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
│   └── instructions/
│       └── workspace.instructions.md
├── README.md
└── .{state-dir}/            # Optional: state management
```

## Validation Checklist

- [ ] All agents have `description` in frontmatter
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
- [ ] File paths follow conventions
