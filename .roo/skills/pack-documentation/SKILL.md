---
name: pack-documentation
description: Provides templates and guidance for creating consistent pack documentation. Load this skill when creating documentation for a new agent pack, updating existing pack documentation, or reviewing documentation for completeness.
---

# Pack Documentation Skill

## Purpose

Provides templates and guidance for creating consistent pack documentation.

## When to Use

Load this skill when:
- Creating documentation for a new agent pack
- Updating existing pack documentation
- Reviewing documentation for completeness

## Documentation Template

### docs/{pack-name}.md Structure

```markdown
# {Pack Name}

## Overview

{1-2 sentence description of what this pack does and its primary use case.}

## Location

`agent-packs/{pack-name}/`

## Agents

| Agent | Slug | Responsibility |
|-------|------|----------------|
| {Agent Name} | `{agent-slug}` | {Brief responsibility description} |

## Orchestration Logic

{Describe how agents interact. Use diagram if multi-agent:}

```
User Request
    ↓
Entry Agent
    ├── → Worker A
    └── → Worker B
           ↓
      Result to User
```

## Skills Included

{List skills or "None" if minimal pack}

## Installation

### Option 1: Direct Use (Recommended for Development)

Open the pack folder directly as your VS Code workspace:

```bash
code agent-packs/{pack-name}
```

### Option 2: Copy to Project

```bash
# Copy mode definitions
cp agent-packs/{pack-name}/.roomodes /path/to/your/project/

# Copy rules and configuration
cp -r agent-packs/{pack-name}/.roo /path/to/your/project/
```

## Usage

1. Open the pack directory in VS Code
2. Roo Code discovers modes from `.roomodes`
3. Select `{primary-agent-slug}` from the mode picker
4. Begin interaction

## Pack Structure

```
{pack-name}/
├── .roomodes
├── .roo/
│   └── rules-{slug}/
│       └── rules.md
└── README.md
```

## Configuration

### fileRegex Patterns

{Document any notable fileRegex patterns used by agents in this pack}

| Pattern | Allows Editing |
|---------|---------------|
| `{pattern}` | {description} |
```

### docs/README.md TOC Entry Format

Add to the table:

```markdown
| [{Pack Name}](./{pack-name}.md) | `agent-packs/{pack-name}/` | {Description} | {Status} |
```

Status options: `Stable`, `Beta`, `Template`, `Experimental`

## Quality Checklist

Before finalizing documentation:
- [ ] All placeholders replaced with actual values
- [ ] Agent table complete with all agents
- [ ] Installation commands tested/accurate
- [ ] All internal links work
- [ ] Code blocks have language specifiers
- [ ] Pack structure diagram matches actual structure
