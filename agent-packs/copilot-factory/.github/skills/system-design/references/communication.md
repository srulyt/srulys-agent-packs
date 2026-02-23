# Inter-Agent Communication Patterns

How agents pass information and coordinate work.

## Delegation Pattern

```
Orchestrator                    Specialist
     │                               │
     │──── Invoke with context ─────▶│
     │                               │
     │                         (work happens)
     │                               │
     │◀──── Return with result ─────│
     │                               │
```

**Use When**: Assigning discrete tasks to specialists

**Implementation**:
```markdown
Invoke @{agent} to {task}.

Context:
- File: path/to/input.md
- Parameters: ...

Requirements:
1. Step one
2. Step two

Return: Summary of what was done
```

**Copilot CLI**: Use `agent` tool
**Roo Code**: Use `new_task` or manual mode switch

## Artifact-Based Handoff

```
Agent A                     Agent B
   │                           │
   │── Write artifact.md ─────▶│
   │                           │
   │                     (reads artifact)
   │                           │
   │◀── Write result.md ──────│
   │                           │
```

**Use When**: Passing complex structured data

**Best Practices**:
- Use consistent file locations
- Include metadata (timestamps, author)
- Document expected schema

**Example Structure**:
```
artifacts/
├── architecture.md      # Agent A outputs
├── implementation/      # Agent B outputs
│   ├── file1.md
│   └── file2.md
└── manifest.json        # Tracks all artifacts
```

## State-Based Coordination

```
state.json: phase = "design"
           │
Agent A ───┴───▶ Updates state: phase = "review"
                          │
                 Agent B ◀┘ Reads state, proceeds
```

**Use When**: Multi-phase workflows need synchronization

**State File Pattern**:
```json
{
  "phase": "design|review|build|complete",
  "current_agent": "architect",
  "iteration": 1,
  "artifacts": {
    "design": "path/to/design.md",
    "build": null
  }
}
```

## Broadcast Pattern

```
Orchestrator
     │
     ├────▶ Agent A (notification)
     │
     ├────▶ Agent B (notification)
     │
     └────▶ Agent C (notification)
```

**Use When**: Multiple agents need the same update

**Implementation**: Write to shared location, each agent monitors

## Error Signaling

When an agent cannot complete:

**Success Response**:
```markdown
## Complete

Created:
- file1.md
- file2.md

Summary: Brief description

Ready for next phase.
```

**Error Response**:
```markdown
## Error

Cannot proceed: {reason}

Missing: {what's needed}

Recommendation: {next step}
```

**Questions Response**:
```markdown
## Clarification Needed

Questions:
1. {question}
2. {question}

Context: Why these matter

Defaults: What I'll assume if no answer
```

## Platform Considerations

### Copilot CLI
- Subagents return automatically (no boomerang protocol)
- Use `agent` tool for delegation
- Results flow back through tool response

### Roo Code
- Explicit boomerang protocol required
- Subagents must use `attempt_completion`
- Orchestrator processes returns manually

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Implicit handoff | No clear signal | Always write status |
| Lost context | Agent doesn't know state | Pass full context |
| Blocking waits | Agent hangs waiting | Timeout + retry |
| Silent failures | Errors not reported | Always signal status |
