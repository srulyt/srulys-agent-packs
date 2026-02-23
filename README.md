# Agent Packs Repository

A collection of agent packs for Roo Code, including the Agent Factory meta-system.

## Repository Structure

```
srulys-agent-packs/
├── init.cmd                 # Install factories to root (roo/copilot/both)
├── .gitignore               # Ignores installed factory files
├── .factory/                # Factory STM (gitignored)
├── docs/                    # Documentation for all packs
│   ├── README.md            # Table of contents
│   ├── factory.md           # Factory pack documentation
│   └── {pack-name}.md       # Per-pack documentation
└── agent-packs/             # All agent packs
    ├── roo-agent-factory/   # Roo Code agent factory
    ├── copilot-factory/     # GitHub Copilot CLI factory
    └── {pack-name}/
        ├── .roomodes        # Pack-specific modes
        ├── .roo/            # Pack-specific rules
        └── README.md
```

## Agent Factories

Two factory packs are available for creating agent systems:

| Factory | Target Platform | Location |
|---------|----------------|----------|
| Roo Agent Factory | Roo Code (VS Code) | `agent-packs/roo-agent-factory/` |
| Copilot Factory | GitHub Copilot CLI | `agent-packs/copilot-factory/` |

### Quick Start - Using the Factories

Run `init.cmd` to install the factories to the repository root:

```cmd
:: Install both factories (default)
init.cmd

:: Install only the Roo Agent Factory
init.cmd roo

:: Install only the Copilot Factory
init.cmd copilot
```

After installation:
- **Roo**: Open the repository in VS Code → Factory modes appear in the mode selector → Activate **Factory Orchestrator**
- **Copilot**: Use `gh copilot` and invoke `@copilot-factory`

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
| Roo Agent Factory | Multi-agent system for creating Roo Code agent packs | [docs/roo-agent-factory.md](docs/roo-agent-factory.md) |
| Copilot Factory | Multi-agent system for creating Copilot CLI agent packs | [docs/copilot-factory.md](docs/copilot-factory.md) |
| Example Pack | Starter template | [docs/example-pack.md](docs/example-pack.md) |

## Documentation

Full documentation is in the [`docs/`](docs/) folder:
- [docs/README.md](docs/README.md) - Table of contents
- [docs/factory.md](docs/factory.md) - Factory pack
- [docs/{pack-name}.md](docs/) - Individual pack docs

## Creating New Packs

Use the Factory Orchestrator to create new packs automatically (run `init.cmd roo` first), or create manually:

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
