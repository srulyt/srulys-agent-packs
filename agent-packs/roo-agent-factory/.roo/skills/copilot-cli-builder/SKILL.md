---
name: copilot-cli-builder
description: Comprehensive guide for building agents, skills, and prompts for GitHub Copilot CLI. Use this skill when creating custom agents (.agent.md files), skills (SKILL.md files), or custom instructions for Copilot CLI. Covers tool reference, file structure, best practices, and prompt engineering patterns.
---

# Copilot CLI Builder Skill

Build agents, skills, and prompts for GitHub Copilot CLI.

## Copilot CLI Overview

GitHub Copilot CLI is a terminal-native AI agent that:
- Runs locally with full agentic capabilities (build, edit, debug, refactor)
- Has GitHub MCP server built-in for repository/issue/PR access
- Requires explicit user approval for file modifications
- Supports custom agents, skills, and instructions

## Customization Types

| Type | Purpose | File Format | Location |
|------|---------|-------------|----------|
| **Custom Agent** | Specialized agent with tailored tools/prompts | `*.agent.md` | `.github/agents/` or `~/.copilot/agents/` |
| **Skill** | Reusable knowledge/workflows/scripts | `SKILL.md` + resources | `.github/skills/` or `~/.copilot/skills/` |
| **Custom Instructions** | Repository-wide context | `*.instructions.md` | `.github/instructions/` or `.github/copilot-instructions.md` |

### When to Use Each

| Use Case | Recommended |
|----------|-------------|
| Restrict tools available | Custom Agent |
| Specialized workflow for specific task | Custom Agent |
| Reusable domain knowledge | Skill |
| Scripts/templates to include | Skill |
| Repository coding standards | Custom Instructions |
| General project context | Custom Instructions |

---

## Creating Custom Agents

Custom agents are markdown files with YAML frontmatter defining specialized Copilot behavior.

### Agent File Structure

```markdown
---
name: agent-name
description: Required. What the agent does and when to use it.
tools: ["tool1", "tool2"]
---

Agent prompt and instructions in markdown body.
Maximum 30,000 characters.
```

### YAML Properties

| Property | Required | Type | Description |
|----------|----------|------|-------------|
| `name` | No | string | Display name (defaults to filename) |
| `description` | **Yes** | string | Purpose and capabilities |
| `tools` | No | string[] or string | Allowed tools. Omit for all tools. Supports YAML array or comma-separated string. |
| `disable-model-invocation` | No | boolean | When `true`, agent must be manually selected (default: false). Preferred over `infer`. |
| `infer` | No | boolean | **Deprecated** — use `disable-model-invocation` instead. Auto-select based on context (default: true) |
| `target` | No | string | `vscode` or `github-copilot`. Omit for both. |
| `model` | No | string | AI model override (IDE environments only, ignored on GitHub.com) |
| `mcp-servers` | No | object | Additional MCP servers for this agent (org/enterprise level only) |
| `metadata` | No | object | Key-value pairs to annotate the agent with useful data |

### Agent Locations

| Scope | Location |
|-------|----------|
| Repository | `.github/agents/` |
| Personal | `~/.copilot/agents/` |
| Organization | `/agents/` in `.github-private` repo |

### Tool Configuration

**All tools (default):** Omit `tools` property or use `tools: ["*"]`

**Specific tools:**
```yaml
tools: ["read", "edit", "search", "execute"]
```

**Disable all tools:**
```yaml
tools: []
```

### Tool Reference

See [references/tools.md](references/tools.md) for complete tool documentation and the [Available Tools Reference](#available-tools-reference) section below for tool aliases used in the `tools` property.

### Agent Prompt Guidelines

1. **Define Role Clearly**: State expertise and responsibilities
2. **Set Boundaries**: What the agent should/shouldn't do
3. **Specify Outputs**: Expected formats and quality standards
4. **Include Context**: Domain-specific knowledge

### Agent Examples

**Read-Only Explorer:**
```markdown
---
name: code-explorer
description: Analyzes codebases without modifications
tools: ["read", "search"]
---

You explore and explain code. Never modify files.
Focus on architecture, patterns, and dependencies.
```

**Implementation Specialist:**
```markdown
---
name: implementation-planner
description: Creates implementation plans without coding
tools: ["read", "search", "edit"]
---

You create detailed technical plans in markdown.
Never write production code directly.
Focus on specifications, not implementation.
```

---

## Creating Skills

Skills are packages of knowledge, scripts, and resources that Copilot loads when relevant.

### Skill File Structure

```
skill-name/
├── SKILL.md (required)
└── Optional resources:
    ├── scripts/      - Executable code
    ├── references/   - Documentation for context
    └── assets/       - Templates, images, files
```

### SKILL.md Format

```markdown
---
name: skill-name
description: What this skill does and when to use it. Include trigger keywords.
license: Optional license info
---

# Skill Title

Instructions and guidance in markdown.
Keep under 5000 words for efficiency.
```

### Skill Locations

| Scope | Location |
|-------|----------|
| Repository | `.github/skills/` or `.claude/skills/` |
| Personal | `~/.copilot/skills/` or `~/.claude/skills/` |

### Skill Design Principles

1. **Concise is Key**: Only include what Copilot doesn't already know
2. **Progressive Disclosure**: Core info in SKILL.md, details in references
3. **Trigger Description**: Description determines when skill activates

### Skill Resource Types

| Directory | Purpose | Example |
|-----------|---------|---------|
| `scripts/` | Executable code for repeatable tasks | `rotate_pdf.py` |
| `references/` | Documentation loaded on demand | `api_docs.md` |
| `assets/` | Files used in output (not loaded) | `template.html` |

### Skill Example

```markdown
---
name: api-testing
description: Patterns for testing REST APIs. Use when writing API tests, mocking HTTP responses, or validating API contracts.
---

# API Testing

## Quick Start

Use `requests` for synchronous tests:
```python
response = requests.get(url)
assert response.status_code == 200
```

## Patterns

For detailed patterns, see:
- [references/mocking.md](references/mocking.md) - Mock strategies
- [references/assertions.md](references/assertions.md) - Validation patterns
```

---

## Creating Custom Instructions

Custom instructions provide repository-wide context.

### Instruction File Format

```markdown
---
applyTo: "**/*.ts"  # Optional: glob pattern
---

Instructions for Copilot when working in this repository.
```

### Instruction Locations

| File | Scope |
|------|-------|
| `.github/copilot-instructions.md` | Entire repository |
| `.github/instructions/*.instructions.md` | Path-specific |
| `AGENTS.md` | Repository root (git root & cwd) |
| `CLAUDE.md` | Repository root (git root & cwd) |
| `GEMINI.md` | Repository root (git root & cwd) |
| `~/.copilot/copilot-instructions.md` | All projects (personal) |
| `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` env var | Additional directories |

### Instruction Content Guidelines

- Repository architecture overview
- Coding standards and conventions
- Technology stack details
- Testing requirements
- Common patterns to follow

---

## Prompt Engineering Best Practices

### Structure Patterns

**Role + Task + Constraints:**
```markdown
You are a [role] specializing in [domain].
Your task is to [specific objective].
Constraints:
- Never [prohibited action]
- Always [required behavior]
- Output format: [expected structure]
```

**Context + Examples + Format:**
```markdown
## Context
[Background information]

## Examples
Input: X → Output: Y

## Expected Format
[Template or structure]
```

### Quality Patterns

| Pattern | Purpose |
|---------|---------|
| Explicit boundaries | Prevent scope creep |
| Output templates | Consistent results |
| Error handling | Graceful failures |
| Step-by-step | Complex workflows |

### Anti-Patterns to Avoid

- Vague descriptions ("help with code")
- Contradictory instructions
- Excessive length (>30K chars for agents)
- Duplicating Copilot's built-in knowledge

---

## Design Guidance

For best practices on designing effective agents, skills, and instructions, see [references/best-practices.md](references/best-practices.md). Covers:

- **When to use each customization type** — agents vs skills vs instructions vs hooks vs plugins
- **Subagent architecture** — how custom agents run as subagents with separate context
- **Writing effective descriptions** — trigger keywords, inference design, description patterns
- **Writing effective prompts** — structure patterns, boundaries, anti-patterns
- **Skill design patterns** — progressive disclosure, script-backed skills, trigger design
- **Custom instructions best practices** — modular organization, path-specific rules
- **Hooks and plugins** — guardrails, lifecycle automation, packaging
- **Testing and iteration** — deployment strategy, iterative refinement

---

## Available Tools Reference

For detailed tool documentation including parameters and examples, see [references/tools.md](references/tools.md).

### Tool Categories

These are the tool categories available when configuring the `tools` property. Use the **aliases** (left column) in agent frontmatter, not the actual tool names.

| Alias | Compatible Aliases | Purpose |
|-------|-------------------|---------|
| `execute` | `shell`, `Bash`, `powershell` | Shell commands |
| `read` | `Read`, `NotebookRead` | Read file contents |
| `edit` | `Edit`, `MultiEdit`, `Write`, `NotebookEdit` | Create/modify files |
| `search` | `Grep`, `Glob` | Find files/text |
| `web` | `WebSearch`, `WebFetch` | Fetch URLs, web search |
| `agent` | `custom-agent`, `Task` | Invoke other agents |

**MCP Server Tools (in `tools` property):**
- `github/*` - All GitHub tools (issues, PRs, repos, actions)
- `github/list_issues` - Specific GitHub tool
- `playwright/*` - All Playwright tools (localhost only)
- `some-mcp-server/tool-name` - Specific MCP tool

> **Note:** The `sql`, `ide-get_selection`, `ide-get_diagnostics`, `report_intent`, `store_memory`, and other utility tools are always available and cannot be restricted via the `tools` property. See [references/tools.md](references/tools.md) for the full tool inventory.

---

## Decision Framework

### Agent vs Skill vs Instructions

```
Need to restrict available tools?
  → Custom Agent

Need reusable scripts/templates?
  → Skill

Need to teach domain-specific workflow?
  → Skill (with references/)

Need repo-wide coding standards?
  → Custom Instructions

Need path-specific rules?
  → Path Instructions (.github/instructions/)
```

### Tool Selection for Agents

```
Agent only analyzes code?
  → tools: ["read", "search"]

Agent creates files?
  → tools: ["read", "edit", "search"]

Agent runs tests/builds?
  → tools: ["read", "execute"]

Agent needs structured data/tracking?
  → tools: ["read", "search", "sql"]

Agent needs full capability?
  → Omit tools property
```

---

## Validation Checklist

### Before Deploying Agent

- [ ] Description clearly states purpose and triggers
- [ ] Tools list matches actual needs (restrictive is safer)
- [ ] Prompt under 30,000 characters
- [ ] Tested with representative prompts
- [ ] File in correct location for scope

### Before Deploying Skill

- [ ] SKILL.md has required frontmatter (name, description)
- [ ] Description includes trigger keywords
- [ ] Instructions under 5000 words
- [ ] Scripts tested and working
- [ ] References organized with clear navigation
