---
description: "Analyze existing agent packs and suggest improvements"
---

## Input verification

- Verify that the user has pointed to an existing agent pack either by name or by providing a path
- If no agent pack was provided **Stop** and tell the user to specify which agent pack to analyze before you continue.

## Agent Pack Review & Improvement Task

Analyze the provided **agent pack**, including:
- Agent rules / system instructions
- `.roomodes` configurations
- Inter-agent coordination patterns
- Task decomposition and control flow

Your goal is to **identify concrete, high‑impact improvements** based on modern prompting, agentic design, and orchestration best practices.

### Evaluation Dimensions
Review the agent pack across the following dimensions:

1. **Clarity & Intent**
   - Are agent responsibilities, boundaries, and success criteria unambiguous?
   - Are system instructions concise while remaining complete?
   - Are implicit assumptions made explicit where useful?

2. **Prompt Quality & Efficiency**
   - Opportunities to reduce prompt size without losing capability
   - Removal of redundancy or overlapping instructions
   - Use of structured directives (steps, constraints, guardrails)

3. **Agent Architecture & Orchestration**
   - Appropriateness of the agent split (too coarse vs. too granular)
   - Quality of task handoff, delegation, and return signals
   - Opportunities to improve parallelism, reuse, or specialization

4. **Business Logic & Reasoning Flow**
   - Correctness and robustness of decision logic
   - Handling of edge cases, failure states, or ambiguity
   - Use of verification, reflection, or corrective loops where appropriate

5. **Agentic Best Practices**
   - Use of clearly defined inputs/outputs
   - Deterministic vs. creative behavior alignment
   - Memory, state, or context management considerations
   - Alignment with current agentic and LLM prompting best practices

### Output Requirements
- Provide **specific, actionable improvement suggestions**
- Group suggestions by category (e.g., Prompting, Orchestration, Logic)
- When possible, include **example rewrites or diffs**
- Prioritize improvements by **expected impact**
- Do **not** re‑explain the original content unless relevant to a suggestion

### Tone & Constraints
- Be precise, critical, and constructive
- Optimize for maintainability, scalability, and correctness
- Assume the audience is experienced with multi‑agent systems

Begin the analysis now.
