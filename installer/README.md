# @srulyt/agent-packs

CLI installer for Roo Code agent packs. Install agent packs from GitHub directly into your project.

## Features

- 🚀 Zero-config installation with `npx`
- 🔐 Multiple authentication methods (GCM, GitHub CLI, env vars)
- 📦 Installs latest versions from GitHub main branch
- 🔄 Safe reinstallation (removes old files first)
- 🗑️ Clean uninstallation
- 📋 List available packs

## Installation

No installation required! Use with `npx`:

```bash
npx @srulyt/agent-packs install <pack-name>
```

## Usage

### Install Agent Packs

Install one or more agent packs:

```bash
# Install a single pack
npx @srulyt/agent-packs install agentic-developer

# Install multiple packs
npx @srulyt/agent-packs install agentic-developer context-packs spec-creator
```

### List Available Packs

See all available agent packs:

```bash
npx @srulyt/agent-packs list
```

### Uninstall Agent Packs

Remove installed packs:

```bash
# Uninstall a single pack
npx @srulyt/agent-packs uninstall agentic-developer

# Uninstall multiple packs
npx @srulyt/agent-packs uninstall agentic-developer context-packs
```

## Authentication

The installer supports multiple authentication methods (tried in order):

### 1. Environment Variable (Highest Priority)

```bash
GITHUB_TOKEN=ghp_xxxx npx @srulyt/agent-packs install my-pack
```

### 2. Git Credential Manager (GCM)

If you've cloned any GitHub repo, GCM credentials are used automatically. No setup needed!

### 3. GitHub CLI

If you have `gh` CLI installed and logged in:

```bash
gh auth login
npx @srulyt/agent-packs install my-pack
```

### 4. Unauthenticated (Public Repos Only)

Works automatically for public repositories.

## Advanced Options

### Custom Repository

Install from a different repository:

```bash
npx @srulyt/agent-packs install my-pack --repo myorg/my-agent-packs
```

### Custom Branch

Install from a specific branch (useful for testing):

```bash
npx @srulyt/agent-packs install my-pack --branch feature/new-pack
```

## What Gets Installed

When you install an agent pack, the installer:

1. **Fetches files** from GitHub (main branch by default)
2. **Creates/updates `.roomodes`** - Adds agent modes to your project
3. **Installs rules folders** - Creates `.roo/rules-{agent-slug}/` directories
4. **Updates registry** - Tracks installed packs in `.roo/.agent-packs-registry.json`

### Example File Structure After Installation

```
your-project/
├── .roomodes                           # Created/updated with modes
├── .roo/
│   ├── .agent-packs-registry.json      # Tracks installed packs
│   ├── rules-agentic-orchestrator/
│   │   └── rules.md
│   ├── rules-agentic-spec-writer/
│   │   └── rules.md
│   └── ... (other rules folders)
└── (your project files)
```

## Available Packs

Run `npx @srulyt/agent-packs list` to see all available packs.

Popular packs include:

- **agentic-developer** - Workflow-first, spec-driven development system
- **context-packs** - Multi-agent system for creating context packs
- **spec-creator** - AI-powered product specification writing team
- **simple-agent-factory** - Single-task prompt generation

## Troubleshooting

### Private Repository Access

If you're accessing a private repository and get authentication errors:

1. **Use Git Credential Manager** (easiest): Clone any repo from GitHub once
2. **Use GitHub CLI**: Run `gh auth login`
3. **Use environment variable**: Set `GITHUB_TOKEN=ghp_xxxx`

### TypeScript Errors

The TypeScript errors you see during development are normal - they'll be resolved when dependencies are installed via `npm install`.

## Development

To contribute or modify this installer:

```bash
cd installer
npm install
npm run build
npm link

# Test locally
agent-packs list
```

## License

MIT