# Example Pack

## Overview

A starter/template agent pack demonstrating the standard structure for agent packs in this repository. Use this as a reference when creating new packs or as a starting point for customization.

## Location

`agent-packs/example-pack/`

## Agents

| Agent | Slug | Responsibility |
|-------|------|----------------|
| Example Agent | `example-agent` | Placeholder demonstrating pack structure |

## Orchestration Logic

This pack contains a single agent for demonstration purposes. Multi-agent packs would define orchestration flow here:

```
User Request
    ↓
Entry Agent
    ├── → Worker Agent A
    └── → Worker Agent B
             ↓
        Result to User
```

## Skills Included

None - this is a minimal template.

## Installation

### Option 1: Direct Use (Recommended for Development)

Open the pack folder directly as your VS Code workspace:

```bash
code agent-packs/example-pack
```

### Option 2: Copy to Project

```bash
# Copy mode definitions
cp agent-packs/example-pack/.roomodes /path/to/your/project/

# Copy rules and configuration
cp -r agent-packs/example-pack/.roo /path/to/your/project/
```

### Option 3: Symlink (Development Only)

```bash
# From your target project directory
ln -s /absolute/path/to/agent-packs/example-pack/.roomodes .roomodes
ln -s /absolute/path/to/agent-packs/example-pack/.roo .roo
```

## Usage

1. Open the pack directory in VS Code (or copy/symlink as above)
2. Roo Code discovers modes from [`.roomodes`](../../agent-packs/example-pack/.roomodes)
3. Select `example-agent` from the mode picker
4. Begin interaction

## Pack Structure

```
example-pack/
├── .roomodes                          # Mode definitions
├── .roo/
│   └── rules-example-agent/
│       └── rules.md                   # Agent rules
└── README.md                          # Quick start
```

## Customization

To create your own pack based on this template:

1. **Copy the folder**: `cp -r agent-packs/example-pack agent-packs/my-pack`
2. **Rename mode slugs** in `.roomodes` (e.g., `my-pack-agent`)
3. **Rename rule directories** to match slugs (e.g., `.roo/rules-my-pack-agent/`)
4. **Update rule content** with your agent's identity and responsibilities
5. **Create documentation** at `docs/my-pack.md`
6. **Update docs TOC** in `docs/README.md`

## Configuration

### fileRegex Pattern

The example agent uses `^src/.*` to restrict edits to a `src/` directory. Adjust this pattern for your use case:

| Pattern | Allows Editing |
|---------|---------------|
| `^src/.*` | All files under `src/` |
| `^.*\\.py$` | All Python files |
| `^(src\|tests)/.*` | Files under `src/` or `tests/` |
| `^(?!node_modules/).*` | Everything except `node_modules/` |
