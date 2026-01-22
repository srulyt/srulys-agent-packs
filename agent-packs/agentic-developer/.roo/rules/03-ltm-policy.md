# Long-Term Memory (LTM) Update Policy

This document defines when and how context packs are updated.

---

## LTM Update Principles

1. **Conservative Updates**: Only add information with lasting value
2. **Reviewed Changes**: All LTM updates should be reviewable
3. **Minimal Disruption**: Small, focused updates over large rewrites
4. **No Speculation**: Only document verified facts and patterns

---

## When to Update LTM

### SHOULD Update

```yaml
should_update:
  - type: "Discovered gotcha"
    example: "Method X fails silently when Y is null"
    target_pack: "Relevant area context pack"
  
  - type: "Pattern confirmation"
    example: "Verified that all services use ILogger injection"
    target_pack: "patterns_context.md"
  
  - type: "Architectural insight"
    example: "Component A depends on B for authorization"
    target_pack: "architecture_context.md"
  
  - type: "API contract clarification"
    example: "Endpoint returns 204 on empty result, not 404"
    target_pack: "Relevant service context pack"
```

### SHOULD NOT Update

```yaml
should_not_update:
  - type: "Task-specific decisions"
    example: "Used camelCase for this variable"
    reason: "Not generalizable"
  
  - type: "Temporary workarounds"
    example: "Disabled validation for testing"
    reason: "Will be removed"
  
  - type: "Unverified assumptions"
    example: "Think this method is deprecated"
    reason: "Not confirmed"
  
  - type: "Obvious information"
    example: "C# uses semicolons"
    reason: "No value added"
```

---

## Update Format

### Promotion Candidate

```yaml
# .agent-memory/runs/<run-id>/promotion-candidates/pc-001.yaml
candidate_id: pc-001
source_run: 20260122-1430-user-api-abc123
discovered_by: executor
timestamp: 2026-01-22T15:45:00Z

learning:
  type: gotcha
  summary: "UserService.GetUser returns null for inactive users"
  context: |
    When calling GetUser(id), if the user is inactive,
    the method returns null instead of throwing.
    Callers must handle this case explicitly.
  
  evidence:
    - file: "src/Services/UserService.cs"
      line: 142
      observation: "Returns null without logging"

target:
  pack: ".context-packs/user-service_context.md"
  section: "Gotchas"

promotion_status: pending
```

---

## Context Pack Update Process

1. **Memory Consolidator reviews candidates**
2. **Filters out low-value items**
3. **Groups related updates**
4. **Applies minimal edits to target packs**
5. **Logs what was promoted vs rejected**

### Update Event

```yaml
event_type: ltm-update
run_id: 20260122-1430-user-api-abc123
updates:
  - pack: ".context-packs/user-service_context.md"
    section: "Gotchas"
    change: "Added null handling note for GetUser"
    lines_added: 4
rejected:
  - candidate_id: pc-002
    reason: "Too specific to this task"
```
