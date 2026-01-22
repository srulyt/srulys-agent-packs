# Resume Protocol (Simplified)

This document defines the orchestrator resume behavior. It replaces any other resume instructions.

## Resume Principle

**All state is reconstructable from disk artifacts.**

## Resume Entry Points

- **Fresh start**: No incomplete runs found
- **User continue**: User requests resume without run-id
- **User specifies run-id**: Load the requested run
- **Multiple incomplete runs**: Ask user which run to resume

## Resume Checklist

1. **Locate active run**: Check `.agent-memory/runs/` for incomplete runs
2. **Load core artifacts** (if present):
   - `constitution.md`
   - `prd.md`
   - `plan.md`
   - `task-graph.json`
3. **Scan event logs**: Read `events/**/*.jsonl` in all actor folders
4. **Derive task state from events**:
   - `pending` (no events)
   - `in_progress` (`task_started` without completion)
   - `done` (`task_completed`)
   - `failed` (`task_failed`)
   - `blocked` (`task_blocked`)
5. **Compute runnable tasks**:
   - Dependencies satisfied
   - Not done
   - Not blocked
6. **Resume execution**:
   - If in Phase 0/1: continue PRD/plan or wait for approval
   - If in Phase 2: execute next runnable task
   - If in Phase 3: re-run cleanup/PR prep
   - If in Phase 4: run memory consolidation

## Resume Reporting Template

```
═══════════════════════════════════════════════════════════
RESUMING RUN: <run-id>

Current State:
- Phase: <0-4>
- Tasks: <done>/<total> complete
- Last activity: <timestamp>
- Last completed: <task-id> - <title>

Next Action:
- <action summary>

Continuing...
═══════════════════════════════════════════════════════════
```

## Edge Cases (Short)

- **Multiple runs**: Ask user which run to resume
- **Missing artifact**: Re-run the step that should have produced it
- **Corrupted event log**: Parse what is readable, warn user, proceed cautiously
- **Very old run**: Warn about staleness and suggest review

## Event Discipline

- Events are append-only
- Never modify existing event files
- Use per-actor event logs (`events/<actor-id>/`)
