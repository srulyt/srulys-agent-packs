---
description: "Run a self-improvement cycle on the Copilot Factory's own agent and skill prompts based on latest Copilot features, model capabilities, and industry best practices"
agent: "Copilot Factory"
---

## Self-Improvement Cycle: Copilot Factory Prompts

I need you to run an **improvement cycle on your own agent and skill prompts** — the files that define the Copilot Factory system itself.

**Mode**: `improvement`

**Target pack**: `agent-packs/copilot-factory` (this pack — your own source files)

### Scope

Discover and analyze ALL Copilot Factory source files by scanning:

- All `.agent.md` files under `.github/agents/`
- All `SKILL.md` files and reference materials under `.github/skills/*/`
- All `.instructions.md` files under `.github/instructions/`
- All `.prompt.md` files under `.github/prompts/` (excluding this one)

### Research Areas

Before proposing changes, research the current state of:

1. **GitHub Copilot platform** — Fetch the latest docs to find new or changed agent/skill capabilities, frontmatter fields, tool aliases, artifact specs, limits, or features. 

2. **Model capabilities** — Current models available in Copilot and prompting techniques optimized for them (structured reasoning, tool-use patterns, context window management, multi-turn delegation)

3. **Agentic best practices** — Industry patterns for multi-agent orchestration, prompt compression, guardrails, error recovery, state management, and self-correction loops

### Improvement Criteria

Evaluate each file against the research findings for:
- **Platform alignment** — Using all available features; no deprecated patterns
- **Prompt quality** — Conciseness, clarity, structured directives, no redundancy
- **Orchestration** — Delegation clarity, handoff protocols, error handling
- **Model optimization** — Prompts tuned for current model capabilities
- **Completeness** — Missing guardrails, edge cases, or quality checks
- **Self-consistency** — Agents, skills, instructions, and prompts align with each other

### Constraints

- Do NOT change the fundamental agent architecture unless research strongly justifies it
- Do NOT change session directory structure or state management format without explicit approval
- Preserve backward compatibility with existing sessions where possible
- Every change must be traceable to a specific research finding or best-practice principle