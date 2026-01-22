# Parallelization Analysis

This document details how to analyze tasks for safe parallel execution.

## Parallelization Principles

### Benefits of Parallelization

- Faster execution for large task sets
- Better utilization of multiple contributors
- Clear separation of concerns

### Risks of Parallelization

- Merge conflicts
- Race conditions in shared resources
- Inconsistent intermediate states
- More complex coordination

## Parallelization Safety Analysis

### Area Path Analysis

Tasks can be parallelized when they touch **non-overlapping area paths**:

```
Example: Safe to parallelize

Task A:
  area_paths: ["src/Api/Controllers/Auth"]
  files: ["AuthController.cs", "AuthService.cs"]

Task B:
  area_paths: ["src/Api/Controllers/Users"]
  files: ["UserController.cs", "UserService.cs"]

Result: ✅ SAFE - No overlap
```

```
Example: NOT safe to parallelize

Task A:
  area_paths: ["src/Api/Controllers"]
  files: ["BaseController.cs", "AuthController.cs"]

Task B:
  area_paths: ["src/Api/Controllers"]
  files: ["BaseController.cs", "UserController.cs"]

Result: ❌ CONFLICT - Both modify BaseController.cs
```

### Conflict Hotspot Detection

Identify files/resources that are common conflict sources:

**High-risk hotspots:**

- Shared configuration files (`appsettings.json`, `web.config`)
- Common base classes
- Shared utility classes
- Database migration scripts
- SQL stored procedures in same schema
- Dependency injection registrations
- Resource files (`.resx`, `.json` resources)

**Detection approach:**

1. List all files modified by each task
2. Find intersection between tasks
3. Flag tasks with shared files
4. Mark hotspot files for serialization

### Dependency Chain Analysis

Tasks with dependency relationships CANNOT run in parallel:

```
T001 → T003 → T005
      ↘
T002 → T004

Parallel groups:
- [T001, T002] - Can run together (no deps)
- [T003, T004] - Can run together (T001, T002 done)
- [T005] - Must run alone (depends on T003)
```

## Parallelization Decision Matrix

| Criteria                | Weight   | Safe        | Unsafe          |
| ----------------------- | -------- | ----------- | --------------- |
| Overlapping area_paths  | High     | No overlap  | Any overlap     |
| Shared files            | Critical | None        | Any shared      |
| Dependency relationship | Critical | Independent | Any dependency  |
| Shared SQL objects      | High     | None        | Same table/proc |
| Shared config sections  | Medium   | None        | Same section    |
| Integration points      | Medium   | Different   | Same service    |

## Lane Branch Strategy

When parallelization is safe and enabled:

### Lane Branch Naming

```
<feature-branch>/lane-<task-id>

Example:
feature/add-auth/lane-T001
feature/add-auth/lane-T002
```

### Lane Branch Lifecycle

1. **Create**: Branch from feature branch at parallel start
2. **Work**: Execute task on lane branch
3. **Merge**: Merge back to feature branch immediately on completion
4. **Delete**: Remove lane branch after successful merge

### Lane Merge Protocol

```
1. Complete task on lane branch
2. Pull latest from feature branch
3. Resolve any conflicts (should be minimal if analysis was correct)
4. Run verification on merged result
5. Push to feature branch
6. Delete lane branch
```

## Parallel Group Definition

In task-graph.json, define parallel groups:

```json
{
  "parallel_groups": [
    {
      "id": "PG001",
      "tasks": ["T001", "T002"],
      "safe": true,
      "confidence": "high",
      "reason": "Non-overlapping area_paths, no shared files",
      "recommendations": {
        "lane_branches": true,
        "verification_after": true
      }
    },
    {
      "id": "PG002",
      "tasks": ["T005", "T006"],
      "safe": false,
      "confidence": "high",
      "reason": "Both modify Config.cs",
      "recommendations": {
        "serialize": true,
        "order": ["T005", "T006"]
      }
    }
  ]
}
```

## Conflict Hotspot Documentation

Document known hotspots:

```json
{
  "conflict_hotspots": [
    {
      "path": "src/Shared/Config.cs",
      "type": "shared_config",
      "affected_tasks": ["T005", "T007", "T009"],
      "recommendation": "serialize",
      "notes": "Central configuration, high merge conflict risk"
    },
    {
      "path": "sql/Migrations/",
      "type": "migration_scripts",
      "affected_tasks": ["T003", "T008"],
      "recommendation": "serialize",
      "notes": "Migrations must be sequential"
    },
    {
      "path": "src/DI/ServiceRegistration.cs",
      "type": "di_registration",
      "affected_tasks": ["T002", "T004", "T006"],
      "recommendation": "serialize_or_combine",
      "notes": "DI registrations often conflict"
    }
  ]
}
```

## Parallelization in Task Contract

Each task contract should indicate parallelization status:

```markdown
## Parallelization

**Parallel Group**: PG001
**Can Run With**: T002, T003
**Must Wait For**: T001 (dependency)
**Conflicts With**: T005 (shared file: Config.cs)

**Lane Branch Recommended**: Yes/No
**Reason**: <explanation>
```

## Handling Parallel Execution Failures

If parallel execution causes issues:

### Merge Conflict Resolution

1. Pull both lane branches
2. Identify conflict source
3. Resolve manually or re-serialize
4. Update conflict hotspot documentation
5. Consider adding to LTM for future reference

### Race Condition Detection

1. Unexpected test failures after merge
2. Inconsistent state in shared resources
3. Build failures from incompatible changes

### Recovery Protocol

1. Revert to pre-parallel state
2. Mark tasks as needing re-execution
3. Update task graph to serialize
4. Re-execute sequentially
5. Document for future planning

## Recommendations to Orchestrator

Task breaker should provide:

```json
{
  "parallelization_summary": {
    "total_tasks": 10,
    "parallelizable": 6,
    "must_serialize": 4,
    "parallel_groups": 2,
    "estimated_time_savings": "40%",
    "risk_level": "low",
    "recommendations": [
      "Tasks T001, T002 can run in parallel",
      "Serialize T005, T006 due to shared config",
      "Consider lane branches for parallel groups"
    ]
  }
}
```

## User Override Options

Users may override parallelization:

- **Force serial**: Run all tasks sequentially regardless of analysis
- **Force parallel**: Allow specified parallel groups (user accepts risk)
- **No lane branches**: Parallel execution but on same branch (higher risk)

Document user preferences in constitution.md for resume consistency.
