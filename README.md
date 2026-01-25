# Agent Packs Repository

A collection of agent packs for Roo Code, including the Agent Factory meta-system.

## Repository Structure

```
srulys-agent-packs/
├── .roomodes                # Factory pack modes (root-level)
├── .roo/                    # Factory pack rules, skills, templates
├── .factory/                # Factory STM (gitignored)
├── docs/                    # Documentation for all packs
│   ├── README.md            # Table of contents
│   ├── factory.md           # Factory pack documentation
│   └── {pack-name}.md       # Per-pack documentation
└── agent-packs/             # All other agent packs
    └── {pack-name}/
        ├── .roomodes        # Pack-specific modes
        ├── .roo/            # Pack-specific rules
        └── README.md
```

## The Factory Pack (Root)

The **Agent Factory** is a multi-agent system that creates other agent packs. It's the singular exception to the isolation pattern, living at repository root.

### Quick Start - Using the Factory

1. Open this repository in VS Code
2. Factory modes are available immediately
3. Activate **Factory Orchestrator** mode
4. Describe the agent pack you want to create
5. Factory creates the pack under `agent-packs/`

Factory agents:
- **Factory Orchestrator** - Coordinates workflow
- **Factory Architect** - Designs system architecture
- **Factory Engineer** - Implements modes and rules
- **Factory Critic** - Reviews for quality

See [docs/factory.md](docs/factory.md) for full documentation.

## Installing Agent Packs

### Quick Install with NPX (Recommended)

Install agent packs directly into your project using the CLI installer:

```bash
# Install a single pack
npx @srulyt/agent-packs install agentic-developer

# Install multiple packs
npx @srulyt/agent-packs install agentic-developer context-packs spec-creator

# List available packs
npx @srulyt/agent-packs list

# Uninstall packs
npx @srulyt/agent-packs uninstall agentic-developer
```

**Features:**
- 🚀 Zero-config installation with `npx`
- 🔐 Multiple authentication methods (GCM, GitHub CLI, env vars)
- 📦 Always installs latest from GitHub main branch
- 🔄 Safe reinstallation (removes old files first)
- 🗑️ Clean uninstallation

See [installer/README.md](installer/README.md) for full documentation.

### Alternative: Manual Installation

#### Option 1: Open Directly

Open the pack folder as your VS Code workspace:

```bash
code agent-packs/{pack-name}
```

#### Option 2: Copy to Project

```bash
cp agent-packs/{pack-name}/.roomodes /path/to/your/project/
cp -r agent-packs/{pack-name}/.roo /path/to/your/project/
```

#### Option 3: Symlink

```bash
# From your target project
ln -s /path/to/agent-packs/{pack-name}/.roomodes .roomodes
ln -s /path/to/agent-packs/{pack-name}/.roo .roo
```

## Available Packs

| Pack | Description | Docs |
|------|-------------|------|
| Factory | Multi-agent system for creating agent packs | [docs/factory.md](docs/factory.md) |
| Example Pack | Starter template | [docs/example-pack.md](docs/example-pack.md) |

## Documentation

Full documentation is in the [`docs/`](docs/) folder:
- [docs/README.md](docs/README.md) - Table of contents
- [docs/factory.md](docs/factory.md) - Factory pack
- [docs/{pack-name}.md](docs/) - Individual pack docs

## Creating New Packs

Use the Factory Orchestrator to create new packs automatically, or create manually:

1. Create `agent-packs/{pack-name}/`
2. Add `.roomodes` with mode definitions
3. Add `.roo/rules-{slug}/rules.md` for each mode
4. Add `README.md` with quick start
5. Create `docs/{pack-name}.md` with full documentation
6. Update `docs/README.md` TOC

## STM Directories

Short-term memory (STM) directories are gitignored:
- `/.factory/` - Factory's session state
- `agent-packs/**/*-stm/` - Pack STM directories

## License

[Add your license here]
