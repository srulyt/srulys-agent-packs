# Roo Code Artifact Reference

Detailed specifications for Roo Code agent pack artifacts.

## .roomodes File

### Location
Root of agent pack: `{pack-name}/.roomodes`

### Format
YAML with `customModes` array.

### Full Schema

```yaml
customModes:
  - slug: "agent-slug"           # Required: unique identifier
    name: "🎯 Display Name"      # Required: shown in UI
    groups:                       # Required: tool permissions
      - "read"
      - "edit"
      - "browser"
      - "command"
      - "mcp"
    fileRegex: "^pattern/.*$"    # Optional: file edit restrictions
    customInstructions: |        # Required: agent behavior
      - See rules: .roo/rules-agent-slug/rules.md
      - Additional inline instructions
```

### Slug Requirements
- Lowercase only
- Hyphens for word separation
- No spaces or special characters
- Must match rules directory name

### Tool Groups

| Group | Permissions |
|-------|-------------|
| `read` | Read file contents |
| `edit` | Create, modify, delete files |
| `browser` | Access web URLs |
| `command` | Execute shell commands |
| `mcp` | Access MCP server tools |

### fileRegex Patterns

Common patterns:
```yaml
# Allow all files
fileRegex: ".*"

# Only markdown
fileRegex: "\\.md$"

# Specific directory
fileRegex: "^src/.*$"

# Multiple patterns (OR)
fileRegex: "^(src|tests)/.*\\.(ts|js)$"

# Exclude patterns (negative lookahead)
fileRegex: "^(?!node_modules/).*$"
```

### Examples

**Single Agent Pack**:
```yaml
customModes:
  - slug: code-reviewer
    name: "🔍 Code Reviewer"
    groups: ["read"]
    customInstructions: |
      - See rules: .roo/rules-code-reviewer/rules.md
```

**Multi-Agent Pack**:
```yaml
customModes:
  - slug: project-orchestrator
    name: "🎭 Project Orchestrator"
    groups: ["read", "edit", "command"]
    fileRegex: "^\\.project-state/.*$"
    customInstructions: |
      - See rules: .roo/rules-project-orchestrator/rules.md
      
  - slug: code-architect
    name: "🏗️ Code Architect"
    groups: ["read", "edit"]
    fileRegex: "^(docs|specs)/.*\\.md$"
    customInstructions: |
      - See rules: .roo/rules-code-architect/rules.md
      
  - slug: code-engineer
    name: "⚙️ Code Engineer"
    groups: ["read", "edit", "command"]
    fileRegex: "^src/.*$"
    customInstructions: |
      - See rules: .roo/rules-code-engineer/rules.md
```

## Rules File

### Location
`.roo/rules-{slug}/rules.md`

### Structure

```markdown
# {Agent Name} Rules

## Identity

{Role description}
{Expertise areas}
{Personality traits if relevant}

## Responsibilities

1. {Primary responsibility}
2. {Secondary responsibility}
3. {etc.}

## Inputs

- {What information this agent receives}
- {File paths, context, etc.}

## Outputs

- {What this agent produces}
- {File artifacts, reports, etc.}

## Communication Protocol

{How this agent communicates with others}
{Boomerang protocol if orchestrated}

## Quality Standards

- {Requirement 1}
- {Requirement 2}

## Constraints

- {Limitation 1}
- {Limitation 2}
```

### Boomerang Protocol (for orchestrated agents)

```markdown
## Communication Protocol

**Critical**:
- ALWAYS return via `attempt_completion`
- NEVER ask user questions directly
- Return questions to Orchestrator

**Success Response**:
```
Task complete.

Deliverables:
- [path/to/file1]

Summary: [what was done]

Ready for next phase.
```

**Questions Response**:
```
Task paused - clarification needed.

Questions:
1. [question]

Recommendation: [default if applicable]
```
```

## Skills Directory

### Location
`.roo/skills/{skill-name}/SKILL.md`

### Format
Same as Copilot CLI skills (markdown with frontmatter).

## Directory Structure

Complete Roo Code pack:
```
{pack-name}/
├── .roomodes                    # Mode definitions
├── .roo/
│   ├── rules-{slug-1}/
│   │   └── rules.md
│   ├── rules-{slug-2}/
│   │   └── rules.md
│   └── skills/                  # Optional
│       └── {skill-name}/
│           └── SKILL.md
├── README.md                    # Quick start guide
└── .{state-dir}/                # Optional: state management
```

## Validation Checklist

- [ ] `.roomodes` is valid YAML
- [ ] All slugs are lowercase-hyphenated
- [ ] Each slug has matching `rules-{slug}/` directory
- [ ] `fileRegex` patterns are valid JavaScript regex
- [ ] `customInstructions` references correct files
- [ ] Rules files have required sections (Identity, Responsibilities)
- [ ] Orchestrator uses boomerang protocol if multi-agent
