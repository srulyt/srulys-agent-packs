# Neutral Specification Template (reference)

This is a worked, **fully generic** example showing every section
in the catalogue. It is reference material — the drafter does not
literal-copy from it. Use it to understand section intent and
shape; produce content tailored to the user's request.

The template is industry-neutral. It contains no domain-specific
section names, vocabulary, or rules.

---

# [Feature / Product Name] — Specification

## Document Information

- **Author(s)**: [Name(s)]
- **Created**: [YYYY-MM-DD]
- **Last Updated**: [YYYY-MM-DD]
- **Status**: [Draft | In Review | Approved | Archived]
- **Reviewers**: [Names or "Pending assignment"]
- **Version**: [vX.Y]
- **Updates**: [vN.M]   <!-- update mode only; RFC-style -->
- **Obsoletes**: [vN.M] <!-- update mode, full replacement only -->

---

## Changes since vN  <!-- update mode only -->

- [One-line summary per change visible in this revision.]

---

## Problem Statement

[What problem is this solving? Who feels it? What evidence — usage
data, support volume, qualitative research — supports the claim?
Why now?]

---

## Goals & Success Metrics

### Business outcomes
- [Outcome — measurable]

### User outcomes
- [Outcome — measurable]

### Technical outcomes
- [Outcome — measurable]

### Success metrics
| Metric | Baseline | Target | Measurement window |
|--------|----------|--------|--------------------|
| ...    | ...      | ...    | ...                |

---

## Users & Personas

| Persona | Primary needs | Expected outcome |
|---------|---------------|------------------|
| ...     | ...           | ...              |

---

## Stakeholders & Reviewers  <!-- gated: cross-team-scope -->

| Team / Org | Role | What they own | Sign-off required? |
|------------|------|---------------|--------------------|

---

## Solution Summary

[2–4 paragraphs. What will be built. How it addresses the problem.
Key trade-offs.]

---

## Functional Requirements

| ID    | Requirement | Priority |
|-------|-------------|----------|
| FR-01 | [statement] | P0       |
| FR-02 | [statement] | P0       |
| FR-03 | [statement] | P1       |

---

## Acceptance Criteria

| ID    | For       | Given / When / Then |
|-------|-----------|---------------------|
| AC-01 | FR-01     | Given …, when …, then … |
| AC-02 | FR-02     | … |

---

## Non-Functional Requirements  <!-- gated: infra-platform-change -->

| ID     | Category | Requirement | Target |
|--------|----------|-------------|--------|
| NFR-01 | Latency  | …           | p95 ≤ … ms |
| NFR-02 | Availability | …       | ≥ … % |
| NFR-03 | Accessibility | …      | WCAG 2.x AA where applicable |

---

## Capacity & Performance Targets  <!-- gated: infra-platform-change -->

| Dimension | Day-1 target | 12-month target |
|-----------|--------------|-----------------|

---

## Security & Compliance  <!-- gated: security-surface -->

[Trust boundaries, auth flows, data classification, key
management. Defer to consumer-supplied instructions for
domain-specific guidance.]

---

## Threat Model Summary  <!-- gated: security-surface -->

| Threat | Mitigation | Owner |
|--------|------------|-------|

---

## Regulatory & Privacy  <!-- gated: regulatory-load -->

[Identify the specific regulatory regime(s) the user named (e.g.
GDPR, HIPAA, SOC2, accessibility). Defer specifics to user-supplied
instructions; do not encode a regime's conventions here.]

---

## Data Model  <!-- gated: persistence-data -->

[Entities, relationships, retention, lifecycle.]

---

## Telemetry & Analytics  <!-- gated: persistence-data -->

| Event | Trigger | Properties | Purpose |
|-------|---------|------------|---------|

---

## API Contract  <!-- gated: public-api-surface -->

[Public endpoints / SDK surface. Versioning policy below.]

---

## Versioning & Deprecation Policy  <!-- gated: public-api-surface -->

[Semver, support window, deprecation notice cadence.]

---

## Dependencies & Assumptions  <!-- gated: cross-team-scope -->

| Dependency | Owner | Status | Risk if blocked |
|------------|-------|--------|-----------------|

---

## Rollout Plan  <!-- gated: rollout-risk -->

| Phase | Audience | Gate | Owner |
|-------|----------|------|-------|
| Internal | … | … | … |
| Limited GA | … | … | … |
| GA       | … | … | … |

---

## Rollback Strategy  <!-- gated: rollout-risk -->

[Feature-flag kill switch, data-migration reversal plan, rollback
window.]

---

## Test Scenarios  <!-- gated: cross-team-scope OR infra-platform-change -->

| ID    | Scenario | Type (unit/integration/e2e) |
|-------|----------|------------------------------|
| TS-01 | …        | …                            |

---

## Risks & Mitigations

| ID   | Risk | Likelihood | Impact | Mitigation |
|------|------|------------|--------|------------|
| R-01 | …    | …          | …      | …          |

---

## Open Questions

| ID    | Question | Owner | Resolution due |
|-------|----------|-------|----------------|
| OQ-01 | …        | …     | …              |

---

## Out of Scope

- [Explicit non-goal 1]
- [Explicit non-goal 2]

---

## Appendix: Glossary  <!-- optional -->

| Term | Definition |
|------|------------|

---

## Appendix: NFR↔FR Traceability  <!-- gated: infra-platform-change -->

| NFR    | Touches FR(s) |
|--------|----------------|
| NFR-01 | FR-01, FR-02   |

---

## Appendix: Aliases & Deprecations  <!-- update-mode rename history -->

| Current name | Former name | Since | Notes |
|--------------|-------------|-------|-------|

---

## Appendix: Citations

| ID | Source | Used for |
|----|--------|----------|
| S1 | …      | …        |
