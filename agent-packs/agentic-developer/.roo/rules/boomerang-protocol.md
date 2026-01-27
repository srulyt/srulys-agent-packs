# Boomerang Return Protocol

**MANDATORY FOR ALL DELEGATED AGENTS**

This is the canonical boomerang protocol. All agents in the agentic-developer pack MUST follow this protocol.

---

## Core Principle

All delegated agents (non-orchestrator) MUST return control to the orchestrator. The orchestrator is the single point of user communication.

---

## CRITICAL RULES

| # | Rule | Violation |
|---|------|-----------|
| 1 | ALWAYS return via `attempt_completion` | Hanging without returning |
| 2 | NEVER ask user questions directly | Using `ask_followup_question` |
| 3 | NEVER use `ask_followup_question` tool | Bypassing orchestrator |
| 4 | ALWAYS report status in structured format | Vague "Done" responses |
| 5 | ALWAYS include artifact paths | Missing deliverables |

---

## Return Status Categories

Return exactly ONE of these status types:

### SUCCESS
Task completed, all deliverables ready.

### BLOCKED
Cannot proceed due to missing information or external dependency.

### PARTIAL
Some work completed, but task cannot be fully finished.

### FAILED
Task failed, explain why.

---

## Return Message Templates

### Success Response

```markdown
Task complete.

Deliverables:
- [path/to/artifact1]
- [path/to/artifact2]

Summary: [1-2 sentence description of what was accomplished]

Ready for [next phase / verification / cleanup].
```

### Blocked Response

```markdown
Task blocked - cannot proceed.

Blocker: [Specific issue]
- What I tried: [Actions taken]
- What I need: [Specific resolution required]

Recommendation: [Suggested path forward]
```

### Partial Response

```markdown
Task partially complete.

Completed:
- [What was done]

Remaining:
- [What could not be done]
- Reason: [Why]

Recommendation: [How to proceed]
```

### Failed Response

```markdown
Task failed.

Error: [What went wrong]
Cause: [Root cause if known]

Impact: [Why this blocks progress]

Recommendation: [Suggested recovery action]
```

---

## Forbidden Patterns

| ❌ Pattern | Why It's Wrong |
|-----------|----------------|
| Asking user "What format would you prefer?" | Bypasses orchestrator |
| Using `ask_followup_question` | Forbidden for delegated agents |
| Proceeding without returning status | Leaves orchestrator waiting |
| Returning "Done" without artifacts | Unverifiable completion |
| Asking questions orchestrator can answer | Unnecessary escalation |
| Switching modes to "help" | Role violation |

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│                    BOOMERANG CHECKLIST                       │
├─────────────────────────────────────────────────────────────┤
│ Before returning, verify:                                    │
│                                                              │
│ [ ] Status is clear (SUCCESS/BLOCKED/PARTIAL/FAILED)        │
│ [ ] All artifact paths are listed                           │
│ [ ] Summary describes what was done                         │
│ [ ] Recommendation for next step is included                │
│ [ ] Using attempt_completion (NOT ask_followup_question)    │
└─────────────────────────────────────────────────────────────┘
```

---

## Agent-Specific Notes

### Executor
Returns after implementing task. Include:
- Files modified
- Any unexpected findings
- Build/test status if run

### Verifier
Returns after verification. Include:
- PASSED/FAILED/BLOCKED result
- Issue count and summary
- Path to verification report

### Planner
Returns after planning. Include:
- Plan artifact path
- Phase count and summary
- Any ADRs created

### Task Breaker
Returns after task breakdown. Include:
- Task graph path
- Task count
- Any dependency concerns

### Cleanup
Returns after cleanup. Include:
- Files cleaned
- Tech debt documented
- Any issues found

### PR Prep
Returns after preparation. Include:
- PR checklist path
- Final verification status
- Any blockers for submission

---

## For Orchestrator: Processing Returns

When processing agent returns:

1. **On SUCCESS**: Verify artifacts exist, proceed to next step
2. **On BLOCKED**: Resolve or gather info, then re-delegate
3. **On PARTIAL**: Decide: retry, complete differently, or accept partial
4. **On FAILED**: Apply retry protocol or escalate to user
