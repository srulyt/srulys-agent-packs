---
name: ralph-planning
description: Planning expertise for agentic development. Load this skill during context discovery (Phase 1), specification writing (Phase 2), and implementation planning (Phase 3). Provides guidance on codebase exploration, spec creation, and phase-based planning.
---

# Ralph Planning Skill

You're in a planning phase. This skill guides you through discovery, specification, and planning.

## Phase Detection

Check `state.json` phase to determine your specific task:

| Phase | Your Focus |
|-------|------------|
| 1 (discovery) | Explore codebase, gather context |
| 2 (spec) | Write detailed specification |
| 3 (planning) | Create implementation plan |

---

## Phase 1: Context Discovery

### Goal

Understand the codebase well enough to write a meaningful spec and plan.

### Discovery Checklist

1. **Project Structure**
   - Scan directory tree
   - Identify main entry points
   - Note package manager (npm, pip, cargo, etc.)

2. **Technology Stack**
   - Framework(s) in use
   - Language version
   - Key dependencies

3. **Existing Patterns**
   - Code organization conventions
   - Naming patterns
   - Test structure

4. **Context Packs**
   - Check for `.context-packs/` directory
   - Load relevant context if available

5. **Related Code**
   - Find code related to the user's request
   - Identify files that will need changes
   - Note dependencies between components

### Discovery Output

Document findings in your event log:

```markdown
# Event: {N} - Discovery - Codebase Analysis

## Project Overview
- Type: {web app, CLI, library, etc.}
- Language: {language} {version}
- Framework: {framework} {version}

## Relevant Components
- {path/to/component1} - {what it does}
- {path/to/component2} - {what it does}

## Patterns Observed
- {Pattern 1}
- {Pattern 2}

## Integration Points
- {Where new code will connect}

## Risks/Considerations
- {Potential issues to address}
```

### Transition

After discovery, update state to Phase 2 (spec).

---

## Phase 2: Specification Writing

### Goal

Create a clear, testable specification that captures what needs to be built.

### Spec Structure

Write to `.ralph-stm/spec.md`:

```markdown
# Specification: {Feature Name}

## Overview
{Brief description of what this feature does}

## User Request
{Original user request verbatim}

## Requirements

### Functional Requirements
1. {Requirement 1}
2. {Requirement 2}
...

### Non-Functional Requirements
- Performance: {constraints}
- Security: {considerations}
- Compatibility: {requirements}

## Acceptance Criteria

### AC1: {Criterion Name}
**Given** {precondition}
**When** {action}
**Then** {expected result}

### AC2: {Criterion Name}
**Given** {precondition}
**When** {action}
**Then** {expected result}

{Continue for all criteria}

## Constraints
- {Constraint 1}
- {Constraint 2}

## Out of Scope
- {What this does NOT include}

## Dependencies
- {External dependency 1}
- {Existing code dependency}

## Open Questions
- {Any remaining ambiguities - should be minimal}
```

### Specification Principles

1. **Testable Criteria**
   - Every acceptance criterion must be verifiable
   - Use Given/When/Then format for clarity

2. **Scope Boundaries**
   - Explicitly state what's out of scope
   - Prevents scope creep during execution

3. **Minimal Assumptions**
   - Document assumptions clearly
   - Make reasonable defaults for minor decisions

4. **Connection to Codebase**
   - Reference actual files/components discovered
   - Ground requirements in reality

### Handling Ambiguity

| Ambiguity Level | Action |
|-----------------|--------|
| Minor (styling, naming) | Make choice, document |
| Medium (approach) | Choose best option, note alternatives |
| Major (core requirement) | Ask user (rare) |

### Transition

After spec complete, update state to Phase 3 (planning).

---

## Phase 3: Implementation Planning

### Goal

Create a phase-based plan that guides execution. NOT micro-tasks—logical phases.

### Plan Structure

Write to `.ralph-stm/plan.md`:

```markdown
# Implementation Plan: {Feature Name}

## Overview
{How this feature will be implemented}

## Prerequisites
- {Any setup needed before starting}

## Implementation Phases

### Phase 1: {Phase Name}
**Objective**: {What this phase achieves}
**Scope**:
- {Component/file 1}
- {Component/file 2}
**Approach**: {How to implement}
**Verification**: {How to know it's done}

### Phase 2: {Phase Name}
**Objective**: {What this phase achieves}
**Scope**:
- {Component/file 1}
- {Component/file 2}
**Approach**: {How to implement}
**Verification**: {How to know it's done}

{Continue for all phases}

## Testing Strategy
- {Unit tests}
- {Integration tests}
- {Manual verification}

## Risk Mitigation
- Risk: {risk 1}
  Mitigation: {approach}

## Rollback Plan
{How to undo if needed}

## Total Phases: {N}
```

### Planning Principles

1. **Phase-Based, Not Task-Based**
   - Each phase = logical unit of work
   - One phase per execution invocation
   - NOT "create file X, modify line Y"

2. **Dependency Order**
   - Plan phases in dependency order
   - Earlier phases don't depend on later ones

3. **Verification Built-In**
   - Each phase has clear completion criteria
   - Tests run as part of phases when appropriate

4. **Appropriate Granularity**
   - Small feature: 2-4 phases
   - Medium feature: 4-8 phases
   - Large feature: 8-15 phases
   - Too many phases = too granular

### Example Phase Breakdown

For "Add JWT authentication to API":

| Phase | Name | Scope |
|-------|------|-------|
| 1 | Auth Infrastructure | JWT utilities, types, config |
| 2 | Auth Middleware | Verification middleware, error handling |
| 3 | Auth Endpoints | Login, register, refresh endpoints |
| 4 | Route Protection | Apply middleware to protected routes |
| 5 | Testing | Unit tests, integration tests |

### Transition

After plan complete:
1. Update `state.json` with `total_plan_phases` count
2. Transition to Phase 4 (approval)

---

## State Updates

### After Discovery (Phase 1 → 2)

```json
{
  "phase": "spec",
  "phase_id": 2,
  "last_task": "discovery-complete",
  "checkpoint": {
    "can_resume": true,
    "resume_hint": "Write specification based on discovery findings"
  }
}
```

### After Spec (Phase 2 → 3)

```json
{
  "phase": "planning",
  "phase_id": 3,
  "last_task": "spec-complete",
  "checkpoint": {
    "can_resume": true,
    "resume_hint": "Create implementation plan based on spec"
  }
}
```

### After Planning (Phase 3 → 4)

```json
{
  "phase": "approval",
  "phase_id": 4,
  "status": "waiting_for_user",
  "last_task": "plan-complete",
  "total_plan_phases": {N},
  "checkpoint": {
    "can_resume": true,
    "resume_hint": "Waiting for user approval of spec and plan"
  }
}
```

---

## Quality Checklist

Before transitioning out of planning phases:

### Discovery Complete?
- [ ] Project structure understood
- [ ] Tech stack identified
- [ ] Relevant code located
- [ ] Patterns documented
- [ ] Risks noted

### Spec Complete?
- [ ] All requirements listed
- [ ] Acceptance criteria testable
- [ ] Scope clearly bounded
- [ ] Dependencies identified
- [ ] Written to spec.md

### Plan Complete?
- [ ] Phases in dependency order
- [ ] Each phase has clear objective
- [ ] Each phase verifiable
- [ ] Testing strategy included
- [ ] Written to plan.md
- [ ] total_plan_phases updated

---

## Remember

- You're gathering information and creating documents
- Don't implement yet—that's Phase 5
- Be thorough but not exhaustive
- Document decisions in event logs
- One complete task per invocation, then exit
