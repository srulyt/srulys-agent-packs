---
description: "Analyze an existing agent pack and suggest improvements using the Copilot Factory"
agent: "Copilot Factory"
---

## Analyze & Improve Agent Pack

I need you to analyze and improve an existing agent pack.

**Mode**: `improvement`

### Input Verification

- Verify that the user has pointed to an existing agent pack either by name or by providing a path
- If no agent pack was provided, **stop** and ask the user to specify which agent pack to analyze before continuing

### Analysis Scope

Analyze the provided **agent pack**, including all of its artifacts:
- Agent definitions (`.agent.md` files)
- Skills / instructions
- Inter-agent coordination patterns
- Task decomposition and control flow
- README and documentation

### Evaluation Dimensions

Review the agent pack across the following dimensions:

1. **Platform Alignment** — Correct use of frontmatter, tools, trigger keywords, size limits
2. **Prompt Quality & Efficiency** — Conciseness, redundancy, structured directives
3. **Orchestration & Handoffs** — Delegation clarity, return signals, error handling
4. **Completeness & Guardrails** — Invocation guards, file access boundaries, skill loading, retry bounds
5. **Self-Consistency** — Cross-file alignment of names, references, counts, protocols
6. **README Accuracy** — Documentation matches actual implementation

### Output Requirements

- Provide **specific, actionable improvement suggestions**
- Group suggestions by category (e.g., Prompting, Orchestration, Logic, Platform)
- When possible, include **example rewrites or diffs**
- Prioritize improvements by **expected impact**
- Do **not** re-explain the original content unless relevant to a suggestion

### After Analysis

Emit the versioned improvement-analysis contract, then ask the user to choose:

- **incremental** — apply only approved findings, then implementation review
  and changed evals;
- **rebuild** — design → architecture review → approval → build →
  implementation review → evals;
- **cancel** — stop without modifying the pack.

Any automatic eval-fix loop has its own user approval and cap of 3.

### Tone & Constraints

- Be precise, critical, and constructive
- Optimize for maintainability, scalability, and correctness
- Assume the audience is experienced with multi-agent systems
