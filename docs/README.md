# Agent Packs Documentation

## Available Packs

| Pack | Location | Description | Status |
|------|----------|-------------|--------|
| [Roo Agent Factory](./roo-agent-factory.md) | `agent-packs/roo-agent-factory/` | Multi-agent factory for creating Roo Code agent systems | Stable |
| [Factory (legacy)](./factory.md) | See roo-agent-factory | Legacy documentation — see Roo Agent Factory | Deprecated |
| [Example Pack](./example-pack.md) | `agent-packs/example-pack/` | Starter template demonstrating pack structure | Template |
| [Agentic Developer](./agentic-developer.md) | `agent-packs/agentic-developer/` | Workflow-first, spec-driven development system | Stable |
| [Context Packs](./context-packs.md) | `agent-packs/context-packs/` | Multi-agent system for creating context packs from legacy codebases | Stable |
| [Customer Sentiment Analysis](./customer-sentiment-analysis.md) | `agent-packs/customer-sentiment-analysis/` | Multi-agent sentiment analysis from public sources with trend tracking | Stable |
| [Product Feedback Gatherer](./product-feedback-gatherer.md) | `agent-packs/product-feedback-gatherer/` | Multi-agent feedback collection with quality scoring and trend tracking | Stable |
| [Spec Creator](./spec-creator.md) | `agent-packs/spec-creator/` | AI-powered product specification writing team for Microsoft Fabric | Stable |
| [Simple Agent Factory](./simple-agent-factory.md) | `agent-packs/simple-agent-factory/` | Single-task prompt generation for AI platforms | Stable |
| [SaaS Design Studio](./saas-design-studio.md) | `agent-packs/saas-design-studio/` | High-fidelity UI/UX engineering with React, Tailwind, Shadcn/UI | Stable |
| [Ralph Copilot CLI](./ralph-copilot-cli.md) | `agent-packs/ralph-copilot-cli/` | Agentic developer for GitHub Copilot CLI | Stable |
| [Copilot Factory](./copilot-factory.md) | `agent-packs/copilot-factory/` | Multi-agent factory for Copilot CLI targeting Roo or Copilot | Stable |

## Copilot Plugins

Installable GitHub Copilot plugins (manifest + skills/agents, registered in
`.github/plugin/marketplace.json`). Install with
`copilot plugin marketplace add srulyt/srulys-agent-packs` then
`copilot plugin install <name>@srulys-agent-packs`.

| Plugin | Location | Description |
|--------|----------|-------------|
| eval-pilot | `agent-packs/eval-pilot/` | Portable evals for Copilot agents/skills: binary **rubric** pass/fail checks, LLM-as-judge, and numeric **metric** history compared over time. Bundles the pip-installable `evalpilot` engine + `eval-author` / `eval-runner` / `eval-metrics` skills. See its [README](../agent-packs/eval-pilot/README.md). |
| prd-pilot | `agent-packs/prd-pilot/` | Guided EARS-style PRD authoring workflow. |
| product-knowledge-brain | `agent-packs/product-knowledge-brain/` | Maintain and evolve a Product Management knowledge base / living wiki. |

## Quick Start

### Using the Factories (creating agent packs)

1. Run `init.cmd` from the repository root (installs both factories)
2. Open this repository in VS Code
3. Use Factory Orchestrator to create new packs

### Using other packs

1. Navigate to `agent-packs/{pack-name}/`
2. Follow the installation instructions in the pack's documentation
3. Copy or symlink to your target project, or open the pack folder directly

## Pack Structure

Each pack under `agent-packs/` contains:

```
{pack-name}/
├── .roomodes           # Mode definitions
├── .roo/               # Rules, skills, templates
│   └── rules-{slug}/   # Per-agent rules
└── README.md           # Quick start guide
```

## Adding New Packs

Use the Factory Orchestrator to create new packs:

1. Activate Factory Orchestrator mode
2. Describe the agent system you want to create
3. Factory creates the pack under `agent-packs/`
4. Documentation is added to this folder

## Documentation Convention

Each pack has a dedicated doc file: `docs/{pack-name}.md`

Documentation includes:
- Overview and use cases
- Agent roster with responsibilities
- Orchestration flow diagram
- Installation instructions
- Usage guide
