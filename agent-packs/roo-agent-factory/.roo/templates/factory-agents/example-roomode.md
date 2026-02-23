# .roomodes Entry - Format Reference

This file shows the YAML syntax for a mode entry.
It is NOT a template to copy - design your own structure.

## YAML Syntax Example

```yaml
  - slug: "example-agent"
    name: "📋 Example Agent"
    description: "Brief description of agent purpose"
    roleDefinition: |
      Multi-line role definition.
      Describe who this agent is.
    whenToUse: |
      When to activate this agent.
      What triggers its use.
    groups:
      - read
      - edit        # if agent modifies files
      - command     # if agent runs shell commands
      - browser     # if agent does web research
      - mcp         # if agent uses external integrations
    fileRegex: "pattern"  # if agent has edit group
    customInstructions: |
      - Additional instructions
      - Usually points to rules file
```

## Field Reference

| Field | Required | Type | Purpose |
|-------|----------|------|---------|
| slug | Yes | string | Unique identifier |
| name | Yes | string | Display name with emoji |
| description | Yes | string | One-line summary |
| roleDefinition | Yes | multiline | Who the agent is |
| whenToUse | Yes | multiline | Activation triggers |
| groups | Yes | list | Tool permissions |
| fileRegex | Conditional | string | File edit restrictions (if edit group) |
| customInstructions | Optional | multiline | Additional context |

## Notes

- `slug` must be lowercase with hyphens
- `slug` should match rules directory name
- `fileRegex` uses JavaScript regex syntax
- Multiline strings use `|` for literal blocks

---

## Common fileRegex Patterns

```yaml
# Single directory and subdirectories
fileRegex: "^\\.mydir/.*"

# Specific file types in directory
fileRegex: "^\\.mydir/.*\\.md$"

# Multiple directories
fileRegex: "^(\\.dir1/.*|\\.dir2/.*\\.md)$"

# Session-based STM paths
fileRegex: "^\\.factory/runs/[^/]+/(context|artifacts)/.*"
```
