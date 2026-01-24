# Resume Protocol (Simplified)

This document defines the orchestrator resume behavior. It replaces any other resume instructions.

## Resume Principle

**All state is reconstructable from disk artifacts.**

## Resume Entry Points

- **Fresh start**: No incomplete runs found
- **User continue**: User requests resume without run-id
- **User specifies run-id**: Load the requested run
- **Multiple incomplete runs**: Ask user which run to resume

## Resume States

The following states can be detected on resume:

| State | Description | Resume Action |
|-------|-------------|---------------|
| `phase_0_intake` | Intake in progress | Continue PRD creation |
| `phase_1_routing` | Workflow routing pending | Re-run routing decision |
| `bootstrap_b1_detection` | Bootstrap detection in progress | Re-run detection (see [04-bootstrap-workflow.md](04-bootstrap-workflow.md)) |
| `bootstrap_b2_deps_pending` | Waiting for dependency install | Re-check dependencies |
| `bootstrap_b3_planning` | Bootstrap planning in progress | Continue planning |
| `bootstrap_b4_tasks` | Bootstrap task breakdown in progress | Continue task creation |
| `bootstrap_b5_approved` | Bootstrap approved, routing next | Check for "approve and continue" vs "approve bootstrap" |
| `phase_2_dev_plan` | Development planning in progress | Continue planning |
| `phase_3_dev_approved` | Development approved, execution next | Begin Phase 4 |
| `phase_4_bootstrap_complete` | Bootstrap tasks done, D-tasks pending | Continue with D-tasks |
| `phase_4_execution` | Execution in progress | Continue task execution |
| `phase_5_cleanup` | Cleanup in progress | Continue cleanup/PR prep |
| `phase_6_consolidation` | Consolidation in progress | Continue memory consolidation |

## Resume Checklist

1. **Locate active run**: Check `.agent-memory/runs/` for incomplete runs
2. **Load core artifacts** (if present):
   - `constitution.md`
   - `prd.md`
   - `plan.md` (if development workflow)
   - `bootstrap-plan.md` (if bootstrap workflow)
   - `task-graph.json`
   - `workflow-state.json`
   - `dependency-report.md` (if bootstrap B-Phase 2 was reached)
3. **Check workflow-state.json** (if present):
   - Determine workflow mode (`unified`, `bootstrap-only`, `development-only`)
   - Check which phases are complete
   - Check approval states
4. **Scan event logs**: Read `events/**/*.jsonl` in all actor folders
5. **Derive task state from events**:
   - `pending` (no events)
   - `in_progress` (`task_started` without completion)
   - `done` (`task_completed`)
   - `failed` (`task_failed`)
   - `blocked` (`task_blocked`)
6. **Compute runnable tasks**:
   - Dependencies satisfied
   - Not done
   - Not blocked
   - For unified workflow: All B-tasks before D-tasks

## Dependency Check Resume (Bootstrap B-Phase 2)

On resume from bootstrap B-Phase 2 (dependency pending):

1. **Check for dependency-report.md**
2. **Check for install script** (`install-dependencies.ps1` or `install-dependencies.sh`)
3. **Re-run dependency detection**:
   - If all tools now present: Continue to B-Phase 3
   - If tools still missing: Re-present report with updated status

```yaml
dependency_resume:
  if_deps_satisfied:
    action: "Continue to B-Phase 3 (Bootstrap Planning)"
    message: "Dependencies verified. Continuing with bootstrap planning..."
    
  if_deps_still_missing:
    action: "Re-present dependency report"
    message: "Some dependencies still missing. Please install and restart VS Code."
```

For detailed bootstrap phases, see [04-bootstrap-workflow.md](04-bootstrap-workflow.md).

## Unified Workflow Resume

For unified workflow runs, check:

1. **workflow-state.json** for phase status
2. **task-graph.json** for task types:
   - `B-tasks` (bootstrap): B001, B002, etc.
   - `D-tasks` (development): D001, D002, etc.
3. **Task completion status by type**:
   - If all B-tasks done but D-tasks pending: `phase_4_bootstrap_complete`
   - If B-tasks in progress: Resume B-tasks
   - If D-tasks in progress: Resume D-tasks

## Resume Reporting Template

```
═══════════════════════════════════════════════════════════
RESUMING RUN: <run-id>

Current State:
- Phase: <0-6 or B1-B5 for bootstrap>
- Workflow: <bootstrap-only | development-only | unified>
- Bootstrap Tasks: <done>/<total> complete (if applicable)
- Development Tasks: <done>/<total> complete (if applicable)
- Last activity: <timestamp>
- Last completed: <task-id> - <title>

{{#if deps_were_pending}}
Dependency Check:
- Previously missing: <list>
- Now installed: <list or "checking...">
- Still missing: <list or "None">
{{/if}}

Next Action:
- <action summary>

Continuing...
═══════════════════════════════════════════════════════════
```

## Edge Cases

- **Multiple runs**: Ask user which run to resume
- **Missing artifact**: Re-run the step that should have produced it
- **Corrupted event log**: Parse what is readable, warn user, proceed cautiously
- **Very old run**: Warn about staleness and suggest review
- **Dependency install interrupted**: Re-check all dependencies
- **Bootstrap complete, dev not started**: Check if user wanted unified workflow

## Event Types for Resume Detection

New event types to check:

```yaml
resume_detection_events:
  - dependency_check_started
  - dependency_check_complete
  - dependency_script_generated
  - dependency_installation_pending
  - dependency_installation_verified
  - bootstrap_gate_presented
  - bootstrap_gate_response
  - development_gate_presented
  - development_gate_response
  - unified_execution_started
  - bootstrap_phase_complete
  - development_phase_started
```

## Event Discipline

- Events are append-only
- Never modify existing event files
- Use per-actor event logs (`events/<actor-id>/`)

## Cross-References

- Main workflow: [01-orchestration-workflow.md](01-orchestration-workflow.md)
- Bootstrap workflow: [04-bootstrap-workflow.md](04-bootstrap-workflow.md)
- Phase management: [02-phase-management.md](02-phase-management.md)
