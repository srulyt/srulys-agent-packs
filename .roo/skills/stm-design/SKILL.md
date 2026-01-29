---
name: stm-design
description: Comprehensive expertise for designing and implementing git-friendly, multi-user Short-Term Memory (STM) systems. Load this skill when designing state management for multi-agent workflows, implementing session isolation patterns, or creating recovery-capable agent systems.
---

# STM Design Skill

Comprehensive expertise for designing and implementing git-friendly, multi-user Short-Term Memory (STM) systems.

---

## 1. STM Fundamentals

### What is STM?

**Short-Term Memory (STM)** is temporary state that:
- Persists within a session or workflow
- Lives in files (not in-memory) for git-friendliness
- Enables multi-step processes, agent handoffs, and recovery
- Is isolated per session to prevent conflicts

### STM vs LTM

| Aspect | STM | LTM |
|--------|-----|-----|
| **Lifetime** | Session/workflow | Permanent |
| **Isolation** | Per-session | Global |
| **Git impact** | Low (session dirs) | High (shared files) |
| **Use case** | Workflow state | Knowledge base |
| **Mutability** | Frequent updates | Rare updates |
| **Conflict risk** | Low (isolated) | High (shared) |

### When to Use STM

**Use STM when:**
- Multi-step workflow with handoffs between agents
- Recovery/resume capability needed after interruption
- Context exceeds what fits in a single prompt
- Multiple agents need shared workflow state

**Don't use STM when:**
- Single-shot operation (no handoffs)
- Context fits entirely in prompt
- No recovery requirements
- Read-only operations

---

## 2. Git-Friendly Patterns

### Core Principle

**Minimize merge conflicts in multi-user scenarios** by isolating mutable state.

### Pattern: Session-Isolated Directories

```
.state/
├── current-session.json      # Pointer to active session (minimal)
├── sessions/
│   └── {session-id}/         # Each user/workflow gets own directory
│       ├── state.json        # Session state
│       ├── context/          # Session input context
│       └── artifacts/        # Session outputs
└── history/                  # Archived sessions (read-only)
```

**Why Git-Friendly:**
- Different users touch different session directories
- No shared files modified during normal operation
- `current-session.json` only changes on session switch
- Merge conflicts only if two users claim same session ID (unlikely with UUIDs)

### Pattern: Pointer Files

```json
// current-session.json
{
  "active_session": "2026-01-21-a1b2c3d4",
  "updated_at": "2026-01-21T14:30:00Z"
}
```

**Why:** Decouples "what is current" from "session data". Session data can be added without touching the pointer file.

### Pattern: Session ID Format

```
{YYYY-MM-DD}-{8-char-uuid}
Example: 2026-01-21-a1b2c3d4
```

**Benefits:**
- Date prefix enables chronological sorting
- UUID suffix ensures uniqueness across users
- Readable for debugging
- Git-friendly (no special characters)

### Anti-Pattern: Shared Mutable State

```
❌ .state/global-state.json  # Everyone writes here → merge conflicts
❌ .state/queue.json         # Append-heavy → always conflicts
❌ .state/counters.json      # Frequent updates → conflicts
```

**Alternative:** Move mutable data into session-isolated directories.

---

## 3. Multi-User Concurrency Patterns

### Pattern: User-Namespaced Sessions

```
.state/sessions/
├── user-alice/
│   └── 2026-01-21-task1/
│       ├── state.json
│       └── artifacts/
└── user-bob/
    └── 2026-01-21-task2/
        ├── state.json
        └── artifacts/
```

**When to Use:** When user identity is known and isolation between users is important.

### Pattern: Lock Files (When Necessary)

```
.state/sessions/{session-id}/
├── state.json
└── state.lock              # Created when writing, deleted after
```

**When to Use:** Only when atomic multi-file updates are required.

**Warning:** File locks in git repos are advisory only—use sparingly. Git doesn't track lock files well.

### Pattern: Append-Only Logs

```
.state/sessions/{session-id}/
├── state.json              # Current state (single write)
└── history.jsonl           # Append-only log (one JSON per line)
```

**Why Git-Friendly:** Appends to different lines = auto-mergeable by git.

**JSONL Format:**
```jsonl
{"timestamp": "2026-01-21T14:00:00Z", "event": "created", "phase": "init"}
{"timestamp": "2026-01-21T14:05:00Z", "event": "phase_change", "phase": "design"}
{"timestamp": "2026-01-21T14:30:00Z", "event": "phase_change", "phase": "review"}
```

### Pattern: Optimistic Concurrency

```json
{
  "session_id": "2026-01-21-abc123",
  "version": 3,
  "updated_at": "2026-01-21T14:30:00Z",
  "data": { ... }
}
```

**How It Works:**
1. Read state including version
2. Make changes
3. Write back with version+1
4. If file changed during operation, version mismatch triggers recovery

**When to Use:** When multiple processes might update the same session concurrently.

---

## 4. Schema Design Patterns

### Pattern: Minimal Required State

```json
{
  "session_id": "required - must match directory name",
  "created_at": "required - ISO-8601 timestamp",
  "updated_at": "required - ISO-8601 timestamp", 
  "phase": "required for workflows - current phase name",
  "domain_data": "keep minimal - only essential fields"
}
```

**Why:** Less state = less conflict surface, faster operations, easier debugging.

### Pattern: Phase-Based State Machine

```json
{
  "phase": "design",
  "valid_phases": ["init", "design", "review", "build", "complete"],
  "phase_history": [
    {"phase": "init", "entered_at": "2026-01-21T14:00:00Z", "exited_at": "2026-01-21T14:05:00Z"},
    {"phase": "design", "entered_at": "2026-01-21T14:05:00Z", "exited_at": null}
  ]
}
```

**Why:** Clear workflow position, supports recovery and audit trail.

### Pattern: Reference Over Copy

```json
{
  "context": {
    "user_request": "context/user-request.md",
    "decisions": "context/decisions.md",
    "architecture": "artifacts/system_architecture.md"
  }
}
```

**Why:** 
- Avoid duplicating data in state.json
- Keep state.json small
- Single source of truth for content
- References are stable, content can evolve

### Format Decision Guide

| Format | Use When | Avoid When |
|--------|----------|------------|
| **JSON** | Structured data, schemas matter, machine processing | Human editing needed frequently |
| **YAML** | Human-readable config, simple structures | Deep nesting, performance critical |
| **Markdown** | Documentation, context, human-readable content | Machine processing needed |
| **JSONL** | Append-only logs, event streams | Random access needed |

---

## 5. Directory Structure Patterns

### Pattern: Separation of Concerns

```
.state/sessions/{session-id}/
├── state.json       # Workflow state (machine-written, small)
├── context/         # Input context (machine + human readable)
│   ├── request.md   # Original user request
│   └── clarifications.md
└── artifacts/       # Outputs (machine-generated)
    ├── design.md
    └── build-manifest.json
```

**Why:**
- Clear purpose for each area
- Different retention policies possible
- Easy to understand what goes where
- Supports different access patterns

### Pattern: Archival Strategy

```
.state/
├── sessions/        # Active sessions
│   └── 2026-01-21-abc123/
└── history/         # Completed sessions (can be pruned)
    └── 2026-01/     # Monthly grouping
        └── 2026-01-15-def456/
```

**Why:**
- Easy cleanup of old sessions
- Clear lifecycle (active → archived)
- Monthly grouping enables bulk operations
- Keeps active directory fast

### Pattern: README Documentation

```
.state/
├── README.md        # Documents the STM structure
├── sessions/
└── history/
```

**README.md Contents:**
- Purpose of the STM directory
- Session ID format
- Directory structure explanation
- Cleanup/archival policy

---

## 6. Recovery Patterns

### Pattern: Checkpoint State

```json
{
  "phase": "build",
  "checkpoint": {
    "last_completed_step": "create-modes",
    "pending_steps": ["create-rules", "create-skills"],
    "can_resume": true,
    "resume_instruction": "Continue from create-rules step"
  }
}
```

**Why:** Enables recovery from interruption at specific points.

### Pattern: Idempotent Operations

Design state updates so repeating them produces the same result:

```
✅ Check if file exists before creating
✅ Use upsert semantics for state updates  
✅ Track "completed" vs "started" separately
✅ Include operation IDs to detect duplicates
```

**Why:** Safe to retry operations after failures.

### Pattern: Recovery Metadata

```json
{
  "recovery": {
    "last_agent": "factory-engineer",
    "last_action": "creating rules files",
    "interrupted_at": "2026-01-21T14:30:00Z",
    "recovery_notes": "Rules for mode-a completed, mode-b pending"
  }
}
```

**Why:** Human or agent can understand state and resume.

### Pattern: Graceful Degradation

```json
{
  "optional_data": {
    "analytics": null,
    "cache": null
  },
  "required_data": {
    "session_id": "2026-01-21-abc123",
    "phase": "build"
  }
}
```

**Why:** Missing optional data shouldn't block workflow.

---

## 7. Anti-Patterns to Avoid

| Anti-Pattern | Problem | Alternative |
|--------------|---------|-------------|
| **Global mutable state** | Merge conflicts inevitable | Session isolation |
| **Large state.json** | Slow, conflict-prone, hard to read | Reference external files |
| **Nested deep objects** | Hard to merge, hard to update | Flat structures, max 2-3 levels |
| **Timestamps only for ID** | Collision risk with multiple users | Add UUID suffix |
| **Shared queues** | Always conflicts on append | Per-session queues |
| **Binary files in STM** | Git unfriendly, can't diff | Text-based formats only |
| **Hardcoded paths** | Breaks session isolation | Relative paths from session dir |
| **Storing derived data** | Stale data, wasted space | Recalculate when needed |
| **Missing timestamps** | Can't debug, can't audit | Always include created_at, updated_at |
| **Partial JSON updates** | Corruption risk | Always write complete files |

### Code Smell Indicators

```
🚩 state.json > 10KB → Too much data, use references
🚩 Multiple agents write same file → Concurrency risk
🚩 No session ID in paths → Missing isolation
🚩 Shared directory for outputs → Merge conflict risk
🚩 No timestamps → Can't track or debug
🚩 No phase tracking → Can't recover
```

---

## 8. Decision Framework

### Do You Need STM?

```
Question 1: Multi-step workflow?
  Yes → Likely need STM
  No  → Question 2

Question 2: Agent handoffs with context?
  Yes → Need STM
  No  → Question 3

Question 3: Recovery/resume needed?
  Yes → Need STM
  No  → Question 4

Question 4: Context fits in single prompt?
  Yes → No STM needed
  No  → Need STM
```

### Which Isolation Level?

```
Scenario: Single user, single workflow
  → Session-isolated (default)

Scenario: Single user, multiple concurrent workflows
  → Session-isolated (each workflow gets ID)

Scenario: Multiple users, same repository
  → User-namespaced sessions

Scenario: High concurrency requirements
  → Consider external state management (database)
```

### What to Store in State?

```
✅ STORE:
  - Workflow phase/position
  - Timestamps (created, updated)
  - Agent outputs (as file paths, not content)
  - Iteration counts
  - Validation results (pass/fail, not details)
  - Recovery checkpoints

❌ DON'T STORE:
  - Large content (use separate files)
  - Duplicated context (use references)
  - Derived data (recalculate)
  - Sensitive data (security risk)
  - Binary data (git unfriendly)
  - Full error logs (use separate log files)
```

### STM Design Checklist

Before finalizing an STM design:

- [ ] Sessions are isolated (no shared mutable files during normal operation)
- [ ] Session IDs include UUID component (collision prevention)
- [ ] State files are small (<10KB typical)
- [ ] Large content stored in separate files with path references
- [ ] Pointer files are minimal (just ID + timestamp)
- [ ] No append-heavy shared files (use JSONL in session if needed)
- [ ] Archive strategy defined (where completed sessions go)
- [ ] Recovery strategy defined (how to resume interrupted workflows)
- [ ] All timestamps use ISO-8601 format
- [ ] Directory structure has clear separation of concerns

---

## Quick Reference

### Minimal STM Structure

```
.state/
├── current-session.json
└── sessions/
    └── {YYYY-MM-DD}-{uuid}/
        ├── state.json
        ├── context/
        └── artifacts/
```

### Minimal state.json

```json
{
  "session_id": "2026-01-21-a1b2c3d4",
  "created_at": "2026-01-21T14:00:00Z",
  "updated_at": "2026-01-21T14:30:00Z",
  "phase": "current-phase"
}
```

### Minimal current-session.json

```json
{
  "active_session": "2026-01-21-a1b2c3d4",
  "updated_at": "2026-01-21T14:30:00Z"
}
```
