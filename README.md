# Agent Packs Repository

A collection of agent packs for Roo Code, including the Agent Factory meta-system.

## Repository Structure

```
srulys-agent-packs/
├── init.cmd                 # Install the skill-first factory for Copilot
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

The skill-first factory and two legacy factory packs are available:

| Factory | Target Platform | Location |
|---------|----------------|----------|
| Agent Factory (skill-first) | Copilot, Codex, Claude Code | `agent-packs/agent-factory/` |
| Roo Agent Factory | Roo Code (VS Code) | `agent-packs/roo-agent-factory/` |
| Copilot Factory | GitHub Copilot CLI | `agent-packs/copilot-factory/` |

### Quick Start - Using the Factories

Install the [Agent Factory](agent-packs/agent-factory/README.md) as a project-local
Copilot skill:

```powershell
.\init.cmd
```

It chooses the smallest useful customization, including no artifact.
Ask the default agent to use the **`agent-factory` skill**.

`init.cmd` copies only the new skill to `.github\skills\agent-factory`, overwriting
matching files. It no longer installs the legacy factories or accepts `roo`,
`copilot`, or `both` switches. Existing legacy installations are left alone;
their packs remain available for manual installation.

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
| Agent Factory | Portable skill-first customization creation and knowledge-preserving modernization | [docs/agent-factory.md](docs/agent-factory.md) |
| Roo Agent Factory | Multi-agent system for creating Roo Code agent packs | [docs/roo-agent-factory.md](docs/roo-agent-factory.md) |
| Copilot Factory | Multi-agent system for creating Copilot CLI agent packs | [docs/copilot-factory.md](docs/copilot-factory.md) |
| Example Pack | Starter template | [docs/example-pack.md](docs/example-pack.md) |

## Copilot Plugins

Installable GitHub Copilot plugins (`plugin.json` + skills/agents), registered in
[`.github/plugin/marketplace.json`](.github/plugin/marketplace.json). Install with:

```bash
copilot plugin marketplace add srulyt/srulys-agent-packs
copilot plugin install <name>@srulys-agent-packs
```

| Plugin | Description | Docs |
|--------|-------------|------|
| agent-factory | Skill-first customization creation and semantic modernization; no fixed agent hierarchy. | [agent-packs/agent-factory/README.md](agent-packs/agent-factory/README.md) |
| **eval-pilot** | Portable evals for Copilot agents/skills: binary **rubric** pass/fail checks, LLM-as-judge, and numeric **metric** history compared over time. Bundles the TypeScript `evalpilot` engine + `eval-author` / `eval-runner` / `eval-metrics` skills. | [agent-packs/eval-pilot/README.md](agent-packs/eval-pilot/README.md) |
| prd-pilot | Guided EARS-style PRD authoring workflow. | [agent-packs/prd-pilot/README.md](agent-packs/prd-pilot/README.md) |
| spec-writer | Single-skill EARS spec authoring with what-if coverage and draft/publish lifecycle (supersedes spec-author, spec-creator, prd-pilot). | [agent-packs/spec-writer/README.md](agent-packs/spec-writer/README.md) |
| brief-writer | Single-skill product brief / one-pager creation and editing: audience-calibrated, championing-ready, no filler or AI-isms (supersedes product-brief). | [agent-packs/brief-writer/README.md](agent-packs/brief-writer/README.md) |
| product-knowledge-brain | Maintain and evolve a Product Management knowledge base / living wiki. | [agent-packs/product-knowledge-brain/README.md](agent-packs/product-knowledge-brain/README.md) |
| context-pack-builder | Generate and update codebase **context packs** as progressively-disclosed Copilot Skills: multi-agent multi-layer discovery, idempotent update-over-rewrite, and a write+copy-back round-trip. | [agent-packs/context-pack-builder/README.md](agent-packs/context-pack-builder/README.md) |
| story-telling-agent | Evidence-led storytelling and deterministic PPTX/Marp deck production. | [agent-packs/story-telling-agent/README.md](agent-packs/story-telling-agent/README.md) |
| ux-interaction-spec | Turn a PRD, brief, notes or a rough concept into a research-backed **Experience Interaction Specification**, a UX pattern research document and a decision log — specifying behaviour before interface. | [agent-packs/ux-interaction-spec/README.md](agent-packs/ux-interaction-spec/README.md) |

## Documentation

Full documentation is in the [`docs/`](docs/) folder:
- [docs/README.md](docs/README.md) - Table of contents
- [docs/factory.md](docs/factory.md) - Factory pack
- [docs/{pack-name}.md](docs/) - Individual pack docs

## Creating New Packs

Use the `agent-factory` skill to create the smallest useful customization (run `init.cmd` first). For a legacy Roo pack, the manual structure is:

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
