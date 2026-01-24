# Constitution Template

## Document Metadata

```yaml
# Constitution Metadata
constitution_id: "CONST-[run-id]"
created: "YYYY-MM-DDTHH:MM:SSZ"
author: "planner"
source_prd: "[prd-id]"
run_id: "[run-id]"
```

---

# Constitution: [Feature Name]

## Purpose

This constitution defines the immutable constraints, quality standards, and architectural boundaries for this implementation run. All agents must adhere to these rules. It layers on top of `.roo/rules/agentic-global.md`—do not duplicate global commit/PR hygiene here; reference and add only run-specific constraints.

---

## 1. Architectural Constraints

### 1.1 Allowed Modifications

_Files and areas that CAN be modified:_

```yaml
allowed_areas:
  - path: "[path/pattern]"
    reason: "[why this area is in scope]"
    change_types: [create, modify, delete]
```

### 1.2 Forbidden Modifications

_Files and areas that MUST NOT be modified:_

```yaml
forbidden_areas:
  - path: "[path/pattern]"
    reason: "[why this is forbidden]"
    exception_process: "[how to request exception if needed]"
```

### 1.3 Architectural Boundaries

_System boundaries that must be respected:_

| Boundary | Description        | Enforcement    |
| -------- | ------------------ | -------------- |
| [Name]   | [What it protects] | [How enforced] |

---

## 2. Code Standards

### 2.1 Language-Specific Standards

**[Primary Language]:**

```yaml
standards:
  naming:
    classes: "[Convention, e.g., PascalCase]"
    methods: "[Convention]"
    variables: "[Convention]"
    constants: "[Convention]"

  formatting:
    indentation: "[spaces/tabs]"
    line_length: "[max characters]"
    braces: "[style]"

  documentation:
    public_apis: "[requirement]"
    internal_methods: "[requirement]"
    complex_logic: "[requirement]"
```

### 2.2 Error Handling Standards

```yaml
error_handling:
  exceptions:
    use: "[when to throw]"
    avoid: "[when not to throw]"
    custom_exceptions: "[guidelines]"

  logging:
    required_events: "[what must be logged]"
    format: "[log format]"
    levels: "[when to use each level]"

  null_handling:
    approach: "[strategy]"
    validation: "[where to validate]"
```

### 2.3 Testing Standards

```yaml
testing:
  unit_tests:
    coverage_requirement: "[percentage or policy]"
    naming_convention: "[pattern]"
    structure: "[Arrange/Act/Assert or similar]"

  integration_tests:
    when_required: "[criteria]"
    isolation: "[requirements]"

  test_data:
    location: "[where test data lives]"
    cleanup: "[cleanup requirements]"
```

---

## 3. Forbidden Patterns

### 3.1 Code Anti-Patterns

_Patterns that MUST NOT be introduced:_

| Pattern     | Why Forbidden | Alternative          |
| ----------- | ------------- | -------------------- |
| [Pattern 1] | [Reason]      | [What to do instead] |
| [Pattern 2] | [Reason]      | [What to do instead] |

### 3.2 Dependency Restrictions

```yaml
dependencies:
  forbidden_packages:
    - name: "[package]"
      reason: "[why forbidden]"

  restricted_packages:
    - name: "[package]"
      requires_approval: true
      reason: "[why restricted]"

  preferred_packages:
    - category: "[category, e.g., logging]"
      preferred: "[package name]"
      reason: "[why preferred]"
```

### 3.3 Security Anti-Patterns

```yaml
security_forbidden:
  - pattern: "Hardcoded credentials"
    detection: "[how to detect]"
    alternative: "[what to use instead]"

  - pattern: "SQL string concatenation"
    detection: "[how to detect]"
    alternative: "[parameterized queries]"
```

---

## 4. Quality Levels

Quality levels define the expected standards for different types of work. The constitution specifies which level applies to this run.

### 4.1 Bronze (Minimum Viable)

_Quick fixes, prototypes, or low-risk changes:_

- [ ] Code compiles/runs without errors
- [ ] Basic functionality works
- [ ] No tests required
- [ ] Linter warnings allowed

**Use when**: Prototyping, spike solutions, internal tools

### 4.2 Silver (Standard)

_Normal development work:_

- [ ] All Bronze requirements
- [ ] Unit tests required for new code
- [ ] Integration tests optional
- [ ] Build must pass
- [ ] No new linter warnings

**Use when**: Regular feature development, bug fixes

### 4.3 Gold (Production Ready)

_Production releases, public APIs, critical paths:_

- [ ] All Silver requirements
- [ ] Comprehensive test coverage (>80%)
- [ ] Integration tests required
- [ ] Performance benchmarks pass
- [ ] Documentation complete
- [ ] Security review passed

**Use when**: Production releases, breaking changes, security-sensitive code

### 4.4 Quality Level Selection

```yaml
# Set in constitution based on run scope
quality_level: <Bronze|Silver|Gold>
rationale: "<Why this level was selected>"
```

**Selection Criteria:**
- Bronze: Internal tool, spike, prototype
- Silver: Regular feature, non-breaking change (default)
- Gold: Public API, breaking change, security-sensitive

---

## 5. Commit Standards

> **Reference**: See `.roo/rules/agentic-global.md` Section 6 for full commit/PR hygiene rules.

Only document run-specific additions or stricter requirements below:

```yaml
run_specific_commit_rules:
  # Add only rules that are STRICTER than global defaults
  # Examples:
  # - require_issue_reference: true
  # - required_reviewers: ["@security-team"]
  # - branch_protection: "require-linear-history"
```

---

## 6. Review Requirements

### 6.1 Self-Review Checklist

Before requesting verification:

- [ ] Code matches requirements
- [ ] Tests pass locally
- [ ] No debug code left behind
- [ ] No commented-out code
- [ ] No TODO comments for this task

### 6.2 Verification Requirements

What verifier must check:

- [ ] Acceptance criteria met
- [ ] Constitution rules followed
- [ ] Quality gate requirements satisfied
- [ ] No scope violations

---

## 7. Exception Process

### 7.1 Requesting Exceptions

If a constitution rule must be violated:

1. Document the specific rule
2. Explain why violation is necessary
3. Describe mitigation measures
4. Request approval via escalation event

### 7.2 Approval Authority

| Exception Type          | Approver     | Process                    |
| ----------------------- | ------------ | -------------------------- |
| Scope expansion         | Human        | Requires Plan Mode         |
| Code standard deviation | Orchestrator | Document in task           |
| Architectural boundary  | Human        | Requires explicit approval |

---

## 8. Run-Specific Additions

_Space for run-specific constraints discovered during planning:_

### 8.1 Technical Discoveries

- [Discovery 1]
- [Discovery 2]

### 8.2 Additional Constraints

- [Constraint 1]
- [Constraint 2]

---

## Acknowledgment

By proceeding with this run, all agents agree to:

1. Follow this constitution without exception
2. Escalate any conflicts or ambiguities
3. Document any discovered constraints
4. Maintain quality standards throughout

---

_Template Version: 1.0_
_Generated by Agentic Planner_
