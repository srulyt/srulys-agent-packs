# Boomerang Orchestration Protocol

This document defines the standard boomerang orchestration pattern for all Factory agents.

## Core Principle

All sub-agents (non-root) MUST return control to their orchestrator. The orchestrator is the single point of user communication.

## For Sub-Agents (any agent other than the orchestrator)

### Mandatory Rules

1. **ALWAYS** return control via `attempt_completion`
2. **NEVER** ask the user questions directly
3. **NEVER** use `ask_followup_question` tool
4. Report status clearly in one of three categories:
   - **Success**: Task completed, deliverables ready
   - **Questions**: Need clarification from orchestrator
   - **Failure**: Cannot proceed, explain why

### Response Templates

**Success Response:**
```markdown
Task complete.

Deliverables:
- [path/to/file1]
- [path/to/file2]

Summary:
[Brief description of what was accomplished]

Ready for next phase.
```

**Questions Response:**
```markdown
Task paused - clarification needed.

Questions:
1. [Specific question]
2. [Specific question]

Context: [Why these answers are needed]

Recommendation: [Suggested defaults if applicable]
```

**Failure Response:**
```markdown
Task failed - unable to proceed.

Error: [What went wrong]

Impact: [Why this blocks progress]

Recommendation: [Suggested recovery action]
```

## For Root Orchestrator

### Delegation Pattern

Use `new_task` tool with structured context:

```markdown
Switch to @{agent-mode} to {task description}.

Context:
- {relevant file paths}
- {key parameters}

Task:
{Clear objective statement}

Requirements:
- {Requirement 1}
- {Requirement 2}
```

### Processing Returns

1. **Success**: Verify deliverables exist, proceed to next phase
2. **Questions**: Answer directly or gather from user, then re-delegate
3. **Failure**: Decide recovery strategy (retry, alternate path, or escalate)

## Anti-Patterns

❌ Sub-agent asks user "What format would you prefer?"
❌ Sub-agent uses ask_followup_question
❌ Agent proceeds without returning status
❌ Vague completion like "Done" without deliverable paths

