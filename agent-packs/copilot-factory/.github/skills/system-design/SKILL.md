---
name: system-design
description: "Multi-agent system design patterns and guidance. Use when designing agent architectures, planning agent boundaries, determining communication patterns, or evaluating single vs multi-agent approaches. Keywords: architecture, topology, orchestration, agent design."
---

# System Design Skill

Design patterns and guidance for multi-agent systems.

## When to Use This Skill

Load this skill when:
- Designing a new multi-agent system
- Evaluating single-agent vs multi-agent approaches
- Planning agent boundaries and responsibilities
- Designing communication patterns
- Setting up state management

## Decision Framework

### Single Agent vs Multi-Agent

**Use Single Agent When:**
- Task is focused on one domain
- No parallel workstreams needed
- Simple input → output workflow
- Context fits in one conversation

**Use Multi-Agent When:**
- Multiple specialized domains
- Parallel or sequential handoffs
- Complex workflows with distinct phases
- Separation of concerns improves quality

### Agent Count Guidelines

| Complexity | Agents | Example |
|------------|--------|---------|
| Simple | 1 | Code reviewer, doc writer |
| Moderate | 2-3 | Design + implement, or orchestrator + specialist |
| Complex | 4-6 | Factory pattern (orchestrator, architect, engineer, critic) |
| Enterprise | 6+ | Rare; consider decomposition |

## Core Design Principles

### 1. Clear Boundaries

Each agent should have:
- **Single responsibility**: One clear purpose
- **Defined inputs**: What it needs to start
- **Defined outputs**: What it produces
- **Tool restrictions**: Only tools it needs

### 2. Minimal Coupling

Agents communicate through:
- File-based artifacts (documents, configs)
- Structured state (JSON files)
- Clear handoff points

Avoid:
- Shared in-memory state
- Implicit dependencies
- Circular communications

### 3. Fail-Safe Communication

Design for:
- Incomplete handoffs (agent stops mid-task)
- Recovery from any phase
- Clear error signals

### 4. Skills as Single Source of Truth

When a multi-agent system includes skills:
- Skills contain the authoritative domain rules
- Agent prompts reference skills, never duplicate their content
- Each agent declares its skill dependencies in a "Skills to Load" section
- This prevents token waste and maintenance drift

### 5. Orchestrator Resilience

Every orchestrator must plan for:
- **Iteration protocol**: How to handle user feedback after completion (which specialist to re-invoke, whether to re-run quality gates)
- **Retry bounds**: Maximum re-requests to a specialist before the orchestrator takes direct action (recommended: 2)
- **Invocation guards**: Subagents redirect direct user invocations to the orchestrator

### 6. File Access Boundaries

Every agent in a multi-agent system must have explicit path-scoped read/write boundaries defined in its prompt. This prevents agents from writing outside their designated scope, which can cause silent crashes, permission hangs, or corrupted state.

**Design rules**:
- Each agent's architecture entry must specify which directories it may **read** and which it may **write**
- Grant the **narrowest write scope** possible (e.g., STM session dir only, or output dir only)
- Agents that exceed their boundary must return control to the orchestrator with the request
- Enforce via a "File Access Boundaries" section in the agent prompt (prompt-level guardrail, since the runtime has no path-scoping)

**Common boundary patterns**:

| Agent Role | Read Scope | Write Scope |
|------------|-----------|-------------|
| Orchestrator | STM, output dir, skills | STM only |
| Architect/Designer | STM context, skills | STM artifacts only |
| Reviewer/Critic | STM, output dir, skills | STM artifacts only |
| Engineer/Builder | STM, skills/templates | Output dir + STM artifacts |

**Copilot CLI example** (include in agent prompt body):
```markdown
## File Access Boundaries

| Permission | Allowed Paths |
|------------|---------------|
| **Read** | `.my-stm/sessions/{session-id}/`, `.github/skills/` |
| **Write** | `.my-stm/sessions/{session-id}/artifacts/` only |

**Do NOT write to**: `src/`, `.github/agents/`, or any path outside the session artifacts directory.
```

## Topology Patterns

For detailed topology patterns, see [references/agent-patterns.md](references/agent-patterns.md).

### Quick Reference

| Pattern | Structure | Best For |
|---------|-----------|----------|
| Hierarchical | Orchestrator → Specialists | Complex workflows |
| Flat | Peer agents | Independent tasks |
| Pipeline | A → B → C | Sequential processing |
| Hub-and-Spoke | Hub ↔ Spokes | Centralized coordination |

## Communication Patterns

For detailed communication guidance, see [references/communication.md](references/communication.md).

### Quick Reference

| Pattern | Flow | Use Case |
|---------|------|----------|
| Delegation | Parent → Child → Parent | Task assignment |
| Pipeline | Agent → Agent → Agent | Sequential processing |
| Broadcast | One → Many | Notifications |
| Request-Response | A ↔ B | Data exchange |

## State Management

For detailed state management patterns, see [references/state-management.md](references/state-management.md).

### Quick Reference

**Session-Based State**:
```
.{system-name}/
├── current-session.json    # Points to active session
├── sessions/               # Active sessions
│   └── {session-id}/
│       ├── state.json      # Workflow state
│       ├── context/        # Input files
│       └── artifacts/      # Output files
└── history/                # Archived sessions
```

**Session ID Format**: `{YYYY-MM-DD}-{8-char-hex}`

**Agent-Scoped STM Directories (Recommended)**:
- Use a pack-unique STM root directory (for example, `.product-brief-agent-stm/`) to avoid collisions with other packs.
- Keep one pointer file at the root: `current-session.json`.
- Store run data under `runs/{session-id}/`.
- Create one directory per agent under each run to isolate artifacts and handoffs.

Example tree:
```
.product-brief-agent-stm/
├── current-session.json
└── runs/
	└── {session-id}/
		└── agents/
			├── brief-orchestrator/
			├── evidence-analyst/
			├── strategy-modeler/
			└── brief-composer/
```

## Tool Assignment

### Read-Only Agents
```yaml
tools: ["read", "search"]
```
Use for: Reviewers, analyzers, explorers that only report findings verbally.

### Review Agents with Artifact Output
```yaml
tools: ["read", "edit", "search"]
```
Use for: Critics or reviewers that write structured review artifacts to STM directories. Restrict write scope via File Access Boundaries.

### Implementation Agents
```yaml
tools: ["read", "edit", "search"]
```
Use for: Engineers, builders, writers

### Coordinators
```yaml
tools: ["read", "edit", "search", "execute", "agent"]
```
Use for: Orchestrators, coordinators

### Full Access
```yaml
tools: ["*"]  # or omit tools property
```
Use for: General-purpose agents, root agents

## Quality Checklist

Before finalizing design:

- [ ] Each agent has clear, non-overlapping responsibility
- [ ] All agents have appropriate tool restrictions
- [ ] All agents have file access boundaries defined (read/write paths)
- [ ] Communication paths are documented
- [ ] State management handles interruptions
- [ ] Error recovery paths defined
- [ ] Skills identified as single source of truth for domain rules
- [ ] Each agent's skill dependencies are specified
- [ ] Orchestrator includes iteration protocol for user feedback
- [ ] Orchestrator includes retry bounds on specialist re-requests
- [ ] Subagents have invocation guards specified

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| God Agent | One agent does everything | Decompose by responsibility |
| Chatty Agents | Too many handoffs | Batch related work |
| Shared State | Race conditions | Session isolation |
| Implicit Deps | Hidden coupling | Document all dependencies |
| Over-Engineering | Too many agents | Start simple, add complexity as needed |
| Duplicated rules | Skills and agents repeat same content | Skills are truth; agents reference them |
| No feedback loop | Users cannot iterate on completed work | Add iteration protocol to orchestrator |
| Unbounded retries | Infinite loops on failing specialists | Add max retry count with fallback |
| No file access boundaries | Agents write outside scope, silent crashes | Add read/write path guards per agent |

## References

- [Agent Patterns](references/agent-patterns.md) - Detailed topology patterns
- [Communication](references/communication.md) - Inter-agent communication
- [State Management](references/state-management.md) - STM/LTM patterns
