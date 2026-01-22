# Example Pack

A starter/template agent pack demonstrating the standard pack structure.

## Quick Start

1. **Open this directory in VS Code** as your workspace root
2. Roo Code will discover the [`.roomodes`](.roomodes) file automatically
3. Available modes will appear in the mode selector

## Structure

```
example-pack/
├── .roomodes                    # Mode definitions
├── .roo/
│   └── rules-example-agent/     # Agent rules
│       └── rules.md
└── README.md                    # This file
```

## Agents

| Agent | Slug | Description |
|-------|------|-------------|
| Example Agent | `example-agent` | Placeholder demonstrating pack structure |

## Using This Pack

### Option 1: Direct Use (Development)

Open this folder directly in VS Code:

```bash
code agent-packs/example-pack
```

### Option 2: Copy to Project

Copy the configuration files to your project:

```bash
# From repository root
cp agent-packs/example-pack/.roomodes /path/to/your/project/
cp -r agent-packs/example-pack/.roo /path/to/your/project/
```

### Option 3: Symlink (Development)

```bash
# From your project directory
ln -s /path/to/agent-packs/example-pack/.roomodes .roomodes
ln -s /path/to/agent-packs/example-pack/.roo .roo
```

## Customizing

Replace the placeholder content with your actual agent definitions:

1. Edit [`.roomodes`](.roomodes) with your mode definitions
2. Create rule files in [`.roo/rules-{slug}/`](.roo/) for each mode
3. Add skills in `.roo/skills/` if needed
4. Update this README with your pack documentation

## Documentation

Full documentation: [`docs/example-pack.md`](../../docs/example-pack.md)
