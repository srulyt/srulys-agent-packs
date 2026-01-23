# Simple Agent Factory

**Location**: `agent-packs/simple-agent-factory/`  
**Status**: Stable

## Overview

The Simple Agent Factory is a lightweight pack for generating single-task agent prompts suitable for external AI platforms. Unlike multi-agent systems, this factory produces one prompt per request—a standalone text artifact that users can copy directly into their target platform.

### Supported Platforms

- **Gemini Gems** (Google)
- **Custom GPTs** (OpenAI)
- **GitHub Copilot Agents**
- **Claude Projects** (Anthropic)
- Other AI assistant/agent platforms

### When to Use

Use this pack when you need to:
- Create a prompt for an external AI platform
- Build a single-task agent (not a multi-agent system)
- Generate tool-agnostic or platform-specific prompts
- Structure complex workflows using Chain-of-Thought patterns

### When NOT to Use

- Creating multi-agent Roo Code packs (use the main Factory instead)
- Building systems that require state management or orchestration
- Generating code or non-prompt artifacts

---

## Agents

This pack contains a single agent:

| Mode | Slug | Purpose |
|------|------|---------|
| 🎯 Prompt Crafter | `prompt-crafter` | Creates single-task agent prompts |

### Prompt Crafter

The Prompt Crafter specializes in:
- Crafting clear, effective system prompts
- Using Chain-of-Thought (CoT) structuring for complex multi-phase tasks
- Respecting platform-specific formatting conventions
- Building tool-agnostic prompts that work without assumed capabilities

---

## Installation

### Option 1: Open Directly

Open the pack folder in VS Code:
```
code agent-packs/simple-agent-factory/
```

### Option 2: Symlink to Your Project

```bash
# From your project root
ln -s /path/to/agent-packs/simple-agent-factory/.roomodes .roomodes
ln -s /path/to/agent-packs/simple-agent-factory/.roo .roo
```

### Option 3: Copy to Your Project

```bash
cp -r agent-packs/simple-agent-factory/.roomodes your-project/
cp -r agent-packs/simple-agent-factory/.roo your-project/
```

---

## Usage

### Basic Usage

1. Activate the **🎯 Prompt Crafter** mode
2. Describe the agent you want to create
3. Receive a ready-to-use prompt file

### Example Conversation

```
User: Create an agent that helps debug Python code

Prompt Crafter: I'll create a Python debugging assistant. A few quick questions:

1. Target platform? (Gemini Gem, Custom GPT, Claude Project, or generic)
2. Will it have access to any tools? (e.g., code execution, file access)

Or I can create a generic, tool-agnostic prompt right now.

User: Generic is fine

Prompt Crafter: [Generates prompt file at ./generated-prompts/python-debugger-prompt.md]
```

### Specifying Platform

```
User: Create a code review agent for a Custom GPT with browsing enabled

Prompt Crafter: [Generates GPT-formatted prompt with browsing capability notes]
```

### Tool-Aware Prompts

```
User: Create a research assistant for Gemini with Google Search access

Prompt Crafter: [Generates Gemini-formatted prompt with search tool references]
```

---

## Output Format

Generated prompts are written to markdown files with this structure:

```markdown
# [Agent Name] - Prompt

**Platform**: Generic
**Generated**: 2026-01-22

---

## System Prompt

```
[The actual prompt text to copy]
```

---

## Usage Notes

- [Platform-specific instructions]
- [Tool configuration notes]
- [Constraints or limitations]

---

## Prompt Breakdown

### Identity
[Agent persona]

### Core Task
[Primary capability]

### Workflow
[CoT phases if applicable]

### Constraints
[Boundaries]
```

### Output Location

- Default: `./generated-prompts/[agent-name]-prompt.md`
- Or user-specified location

---

## Key Behaviors

### Tool-Agnostic by Default

The Prompt Crafter **never assumes tools are available** unless:
1. User specifies the target platform AND the Crafter knows its capabilities
2. OR user explicitly lists available tools

This ensures prompts work on any platform, regardless of whether it has web search, code execution, file access, etc.

### Platform-Aware Formatting

When a platform is specified, the Crafter adapts:

| Platform | Adaptations |
|----------|-------------|
| **Generic** | Markdown-compatible, no tool assumptions |
| **Gemini Gems** | Conversational tone, Google Search mentions if confirmed |
| **Custom GPTs** | System prompt format, Actions/browsing if specified |
| **Copilot Agents** | Technical focus, workspace-aware language |
| **Claude Projects** | XML tags optional, artifact-aware |

### Chain-of-Thought Structuring

For complex multi-phase tasks, the Crafter embeds CoT patterns:

```markdown
## How I Work

When you give me [input], I follow these steps:

### Phase 1: [Name]
I first [action]. I look for [criteria].

### Phase 2: [Name]
Based on my analysis, I then [action].

### Phase 3: [Name]
Finally, I [action] and present [output].
```

---

## Examples

### Example 1: Meeting Summarizer (Generic)

**Request**: "Create an agent that summarizes meeting notes"

**Generated prompt excerpt**:
```
You are a Meeting Summarizer. Your role is to transform raw meeting notes 
into clear, actionable summaries.

When you receive meeting notes, I:
1. Identify Key Topics: Extract main subjects discussed
2. Capture Decisions: Note any decisions made
3. List Action Items: Identify tasks, owners, deadlines
4. Summarize Discussion: Condense to key points
```

### Example 2: Security Reviewer with Tools

**Request**: "Create a security code reviewer for a Custom GPT with code interpreter"

**Generated prompt excerpt**:
```
You are a Security Code Reviewer. You analyze code for vulnerabilities 
and provide actionable remediation guidance.

## How I Work

### Phase 1: Threat Assessment
I identify the code's context and attack surfaces.

### Phase 2: Vulnerability Scan
Using code interpreter, I can run static analysis patterns...
[References code interpreter capability]
```

### Example 3: Research Assistant for Gemini

**Request**: "Create a research assistant for Gemini Gem with Google Search"

**Generated prompt excerpt**:
```
You are a Research Assistant. You help users find, synthesize, and 
summarize information on any topic.

When researching a topic, I:
1. Search for current, authoritative sources
2. Cross-reference multiple sources
3. Synthesize findings into clear summaries
[References Google Search capability]
```

---

## Structure

```
simple-agent-factory/
├── .roomodes                           # Mode definition
├── .roo/
│   └── rules-prompt-crafter/
│       └── rules.md                    # Agent behavior + platform knowledge
└── README.md                           # Quick start guide
```

---

## Design Notes

### Why Single-Agent?

This factory intentionally uses a single-agent design because:
1. **Output simplicity**: One markdown file per request
2. **Conversation pattern**: Natural information gathering → generation
3. **No handoffs needed**: Prompt crafting is one cohesive skill
4. **Minimal overhead**: No orchestration, no state management

### Stateless Design

No session management or persistent state. Each prompt request is independent. If users want to iterate, they continue the conversation or start fresh.

### Platform Knowledge Embedded

Platform-specific conventions are embedded in the rules file rather than a separate skill, keeping the pack minimal and self-contained.

---

## Comparison with Main Factory

| Aspect | Simple Agent Factory | Main Factory |
|--------|---------------------|--------------|
| Output | Single prompt text file | Multi-file agent pack |
| Agents | 1 (Prompt Crafter) | 4+ (Orchestrator, Architect, etc.) |
| State | None | Session-based |
| Orchestration | None | Full boomerang pattern |
| Use case | External AI platforms | Roo Code environments |
