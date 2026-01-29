---
name: system-design
description: Domain knowledge for designing multi-agent systems. Use this skill when architecting agent boundaries, determining orchestration patterns, assigning tool permissions, or evaluating whether single or multi-agent approaches are appropriate.
---

# System Design Skill

Domain knowledge for designing multi-agent systems.

## Agent Design Considerations

### What Makes a Good Agent Boundary

- Clear, non-overlapping responsibility
- Distinct expertise or tool requirements
- Natural handoff points in workflow
- Understandable role that a human could explain

### How Many Agents?

| Indicator | Recommendation |
|-----------|----------------|
| Single task, single expertise | 1 agent |
| 2-3 distinct phases | 2-3 agents |
| >5 distinct roles | Consider consolidation |
| Agents with 1-2 tasks | Merge with another |

Start with the minimum that works. Each agent should justify its existence.

### Role Definition Principles

| Do | Don't |
|----|-------|
| State WHAT agent accomplishes | Prescribe HOW step-by-step |
| Define outcome and constraints | Write scripts disguised as roles |
| Preserve decision authority | Micromanage agent behavior |

### Tool Assignment Reasoning

| Tool | Assign When |
|------|-------------|
| `edit` | Agent produces/modifies files |
| `command` | Shell operations needed |
| `browser` | Web research required |
| `mcp` | External integrations needed |
| `read` | Almost always (agents need context) |

## Communication Design

### Orchestration Trade-offs

| Approach | Good For | Costs |
|----------|----------|-------|
| Central orchestrator | Complex workflows, user-facing coordination | Single point of failure, overhead |
| Direct agent-to-agent | Simple handoffs, efficiency | Harder to trace, no central view |
| No coordination | Single agent tasks | N/A |

### Handoff Design Principles

1. Make data passed explicit
2. Define success criteria for each handoff
3. Consider: What if this step fails?
4. Document format expectations

### Error Handling Thinking

Questions to consider:
- What can go wrong at each step?
- How will errors propagate?
- Where should recovery happen?
- When should the user be informed?

## File Restriction Considerations

### Why Restrict Agent Editing

- Prevents accidental modification of system files
- Creates clear responsibility boundaries
- Enables safer parallel operation
- Makes debugging easier

### fileRegex Trade-offs

| Restrictive | Permissive |
|-------------|------------|
| Safer | More flexible |
| Clearer boundaries | Faster for simple cases |
| More configuration | Less overhead |

### Organization Principles

- Group related files
- Make paths predictable
- Consider what agents need to read vs write
- Plan for growth

## Design Thinking Prompts

Before finalizing any design, ask yourself:

1. "What's the simplest design that meets requirements?"
2. "If I had to explain this to a junior developer, would it make sense?"
3. "What happens when things go wrong?"
4. "Could a single well-prompted agent handle this?"
5. "What problems am I actually solving with multiple agents?"

## Complexity Indicators

Use these to assess if multi-agent is needed:

| Indicator | Suggests |
|-----------|----------|
| Multiple distinct tasks/phases | Multi-agent likely |
| Iteration or feedback loops | Orchestration needed |
| Multiple expertise areas | Separate agents |
| State persistence needed | STM design required |
| Concurrent users | Session isolation needed |
