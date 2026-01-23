# Simple Agent Factory

A lightweight pack for generating single-task agent prompts for AI platforms.

## Overview

The Simple Agent Factory creates effective, standalone prompts for:
- **Gemini Gems** (Google)
- **Custom GPTs** (OpenAI)
- **GitHub Copilot Agents**
- **Claude Projects** (Anthropic)
- Other AI assistant platforms

Unlike multi-agent systems, this factory produces **one prompt per request**—a text artifact you can copy directly into your target platform.

## Quick Start

1. Activate the **🎯 Prompt Crafter** mode
2. Describe the agent you want to create
3. Optionally specify target platform and available tools
4. Receive a ready-to-use prompt file

## Key Features

- **Tool-agnostic by default**: No assumptions about web search, code execution, etc.
- **Platform-aware**: Adapts formatting for different AI platforms
- **CoT structuring**: Complex multi-phase tasks via Chain-of-Thought patterns
- **Copyable output**: Prompts ready to paste into your platform

## Structure

```
simple-agent-factory/
├── .roomodes                           # Mode definition
├── .roo/
│   └── rules-prompt-crafter/
│       └── rules.md                    # Agent behavior rules
└── README.md                           # This file
```

## Agent

| Mode | Purpose |
|------|---------|
| 🎯 Prompt Crafter | Creates single-task agent prompts |

## Documentation

See [docs/simple-agent-factory.md](../../docs/simple-agent-factory.md) for complete documentation.

## Installation

### Option 1: Open directly
```
Open agent-packs/simple-agent-factory/ folder in VS Code
```

### Option 2: Symlink to your project
```bash
# From your project root
ln -s /path/to/agent-packs/simple-agent-factory/.roomodes .roomodes
ln -s /path/to/agent-packs/simple-agent-factory/.roo .roo
```

### Option 3: Copy to your project
```bash
cp -r agent-packs/simple-agent-factory/.roomodes your-project/
cp -r agent-packs/simple-agent-factory/.roo your-project/
```
