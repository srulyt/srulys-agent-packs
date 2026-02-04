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
infer: true
---

Agent prompt and instructions in markdown body.
Maximum 30,000 characters.
```

### YAML Properties

| Property | Required | Type | Description |
|----------|----------|------|-------------|
| `name` | No | string | Display name (defaults to filename) |
| `description` | **Yes** | string | Purpose and capabilities |
| `tools` | No | string[] | Allowed tools. Omit for all tools. |
| `infer` | No | boolean | Auto-select based on context (default: true) |
| `target` | No | string | `vscode` or `github-copilot` |

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

See [references/tools.md](references/tools.md) for complete tool documentation.

**Core Tool Aliases:**

| Alias | Purpose |
|-------|---------|
| `execute` | Shell commands (bash/powershell) |
| `read` | Read file contents |
| `edit` | Create/modify files |
| `search` | Find files/text |
| `web` | Fetch URLs, web search |
| `agent` | Invoke other agents |

**MCP Server Tools:**
- `github/*` - All GitHub tools (issues, PRs, repos)
- `playwright/*` - Browser automation

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
| Repository | `.github/skills/` |
| Personal | `~/.copilot/skills/` |

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
| `AGENTS.md` | Repository root |
| `~/.copilot/copilot-instructions.md` | All projects (personal) |

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

## Complete Tool Reference

For detailed tool documentation including parameters and examples, see [references/tools.md](references/tools.md).

### Tool Categories

| Category | Tools | Purpose |
|----------|-------|---------|
| File System | `read`, `edit`, `search` | File operations |
| Execution | `execute` | Shell commands |
| Web | `web_fetch`, `web_search` | Internet access |
| GitHub | `github/*` | Repository, issues, PRs |
| Agents | `agent`, `task` | Sub-agent delegation |

### Commonly Used Tools

**File Operations:**
- `view` - Read file contents with line numbers
- `create` - Create new files
- `edit` - Modify existing files (string replacement)
- `glob` - Find files by pattern
- `grep` - Search file contents (ripgrep-based)

**Execution:**
- `powershell` - Run shell commands (works on all platforms)
- Supports sync/async modes
- Can run Python, Node.js, Go via shell

**GitHub MCP Tools:**
- `github-mcp-server-list_issues` - List issues
- `github-mcp-server-list_pull_requests` - List PRs
- `github-mcp-server-search_code` - Search code
- `github-mcp-server-get_file_contents` - Get remote files
- `github-mcp-server-get_job_logs` - Get CI/CD logs

---

## CLI Slash Commands Reference

| Command | Purpose |
|---------|---------|
| `/agent` | Select custom agent |
| `/skills` | Manage skills |
| `/model` | Select AI model |
| `/plan` | Enter plan mode |
| `/review` | Code review agent |
| `/context` | Show token usage |
| `/compact` | Summarize history |
| `/diff` | Review changes |

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
