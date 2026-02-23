---
name: agent-builder
description: Templates and patterns for creating Roo Code or Copilot CLI artifacts. Use when generating .roomodes files, agent rules, custom agents, or skills. Supports both target platforms based on user selection. Keywords: roomodes, agent.md, rules.md, SKILL.md, implementation.
---

# Agent Builder Skill

Templates and patterns for implementing multi-agent systems.

## When to Use This Skill

Load this skill when:
- Generating `.roomodes` files (Roo Code)
- Creating `rules.md` files (Roo Code)
- Writing `.agent.md` files (Copilot CLI)
- Building `SKILL.md` files (Copilot CLI)
- Creating README documentation

## Target Platform Selection

The target platform is set during intake and stored in `state.json`:
- `target_platform: "roo"` → Generate Roo Code artifacts
- `target_platform: "copilot"` → Generate Copilot CLI artifacts

**Important**: Generate artifacts for ONE target only. Do not mix platforms.

## Roo Code Artifacts

For detailed Roo Code patterns, see [references/roo-artifacts.md](references/roo-artifacts.md).

### Quick Reference

**.roomodes** (YAML):
```yaml
customModes:
  - slug: agent-slug
    name: "🎯 Agent Name"
    groups: ["read", "edit", "browser", "command"]
    fileRegex: "^allowed/path/.*$"
    customInstructions: "- See rules: .roo/rules-agent-slug/rules.md"
```

**rules.md** structure:
```markdown
# Agent Name Rules

## Identity
Role and expertise

## Responsibilities
What this agent does

## Communication Protocol
How to return results
```

### Tool Groups (Roo Code)
| Group | Capabilities |
|-------|-------------|
| `read` | Read files |
| `edit` | Create/modify files |
| `browser` | Web access |
| `command` | Execute shell commands |
| `mcp` | MCP server tools |

## Copilot CLI Artifacts

For detailed Copilot patterns, see [references/copilot-artifacts.md](references/copilot-artifacts.md).

### Quick Reference

**.agent.md** format:
```markdown
---
name: Agent Name
description: What it does. When to use. Trigger keywords.
tools: ["read", "edit", "search"]
---

Agent prompt body (max 30,000 chars)
```

**SKILL.md** format:
```markdown
---
name: skill-name
description: What skill does. Trigger keywords.
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
| `agent` | Invoke other agents |

## Template Assets

### Roo Code Templates
- [assets/roo/roomode-template.yaml](assets/roo/roomode-template.yaml)
- [assets/roo/rules-template.md](assets/roo/rules-template.md)

### Copilot CLI Templates
- [assets/copilot/agent-template.md](assets/copilot/agent-template.md)
- [assets/copilot/skill-template.md](assets/copilot/skill-template.md)

## Quality Checklist

### Roo Code
- [ ] Valid YAML syntax in `.roomodes`
- [ ] Slugs are lowercase with hyphens
- [ ] Slug matches rules directory name
- [ ] `fileRegex` is valid JavaScript regex
- [ ] `customInstructions` points to rules file

### Copilot CLI
- [ ] `description` field present (required)
- [ ] `tools` uses correct aliases
- [ ] Agent prompt under 30,000 characters
- [ ] Skill under 5,000 words
- [ ] Descriptions include trigger keywords

### Both Platforms
- [ ] README has clear usage instructions
- [ ] All file paths are correct
- [ ] Build manifest is accurate

## Common Patterns

### Read-Only Agent
**Roo**: `groups: ["read"]`
**Copilot**: `tools: ["read", "search"]`

### Implementation Agent
**Roo**: `groups: ["read", "edit"]`
**Copilot**: `tools: ["read", "edit", "search"]`

### Orchestrator Agent
**Roo**: `groups: ["read", "edit", "command"]` + orchestration rules
**Copilot**: `tools: ["read", "edit", "search", "execute", "agent"]`

### Subagent (No Direct Invocation)
**Roo**: Set `customInstructions` with delegation rules
**Copilot**: `disable-model-invocation: true`

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Missing description | Agent won't trigger | Always include clear description |
| Too many tools | Security risk | Grant minimum needed |
| Huge prompts | Slow, unfocused | Defer to skills |
| Mixed platforms | Confusion | One target per pack |
| No README | Unusable pack | Always include setup guide |

## References

- [Roo Artifacts](references/roo-artifacts.md) - Detailed Roo Code formats
- [Copilot Artifacts](references/copilot-artifacts.md) - Detailed Copilot CLI formats
