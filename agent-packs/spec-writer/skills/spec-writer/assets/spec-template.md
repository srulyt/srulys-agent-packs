# Specification template

Shape reference, not literal copy. Keep every mandatory section; include a gated section only when its axis fires (see [sections and gating](../references/sections-and-gating.md)). Remove HTML comments and gate markers from the delivered spec.

---

# [Feature / Product Name] — Specification

## Document Information

- **Author(s)**: [Name(s)]
- **Created**: [YYYY-MM-DD]
- **Last Updated**: [YYYY-MM-DD]
- **Status: draft**
- **Reviewers**: [Names or "Pending assignment"]
- **Version: 0.0.1-draft**
- **Updates**: [vN.M]   <!-- update of a published spec only -->
- **Obsoletes**: [vN.M] <!-- full replacement only -->

<!-- Bold the field name AND value together (`**Status: draft**`, `**Version: 0.0.1-draft**`), never `**Status**: draft`. The `-draft` suffix is present iff Status is draft. No change-tracking content while draft. See lifecycle.md. -->

---

## Problem Statement

[Lead with the problem; then who feels it, the strongest evidence (numbers preferred), and why now. No solution vocabulary. ≤ ~400 words.]

---

## Goals & Success Metrics

[Brief framing only when provenance or measurement caveats change interpretation. ≤ ~200 words.]

| Metric | Baseline | Target | Measurement window | Type (business / user / technical) |
|--------|----------|--------|--------------------|------------------------------------|
| …      | …        | …      | …                  | …                                  |

---

## Users & Personas

[Optional one-paragraph framing, ≤ ~150 words.]

| Persona | Role / context | Primary job (JTBD) | Top pains | Expected outcome |
|---------|----------------|--------------------|-----------|------------------|
| …       | …              | When <situation>, I want to <motivation>, so I can <outcome> | … | … |

<!-- This is the ONLY persona table in the spec. Leave a JTBD cell blank rather than fabricate a job. -->

---

## User Experience: Journeys & Roles  <!-- gated: experience-surface -->

<!-- Do not restate personas here; reference them by name from Users & Personas. -->

### Job opportunity  <!-- optional; only with importance/satisfaction evidence -->

| # | Job (from Users & Personas) | Importance | Satisfaction | Opportunity |
|---|-----------------------------|------------|--------------|-------------|
| J1 | … | 9/10 | 3/10 | 15 |

<!-- Opportunity = Importance + max(Importance − Satisfaction, 0). -->

### User journey(s)

**Actor:** <persona> — **Scenario:** <triggering context> — **Goal:** <end state>

| Step / Phase | Actor / Role | Trigger | System response | Success signal | What can go wrong |
|--------------|--------------|---------|-----------------|----------------|-------------------|
| …            | …            | …       | …               | …              | → FR-NN           |

<!-- Each step maps to an event-driven FR; each "what can go wrong" maps to an unwanted-behaviour FR. -->

### Roles & permissions

**Access-control model:** RBAC (add ABAC/ReBAC only when needed). **Posture:** deny-by-default, least-privilege, server-side enforcement.

| Role | Can | Cannot | Notes |
|------|-----|--------|-------|
| …    | …   | …      | …     |

- **ACR-01** — <attribute/relationship exception, if any>.

---

## Stakeholders & Reviewers  <!-- gated: cross-team-scope -->

| Team / Org | Role | What they own | Sign-off required? |
|------------|------|---------------|--------------------|

---

## Solution Summary

[Lead with the chosen approach in 1–2 sentences; then what changes for the user or system at the highest level. Per-FR reasoning goes in FR rationale lines; trade-offs and their consequences go in Risks & Mitigations. ≤ ~350 words, ≤ 3 paragraphs.]

---

## Assumptions  <!-- optional, any spec -->

- **A-01** — [A condition the spec relies on that, if false, would change requirements.]

---

## Functional Requirements

Each FR is one EARS shall-statement with nested acceptance criteria. Cover the happy path **and** what can go wrong: invalid input, boundaries, empty and partial states, concurrency, dependency failure, permission denial, limits, and recovery — derived even when the input never mentions them (see [what-if coverage](../references/what-if-coverage.md)). Where the correct response is a business decision, write the FR with `[TBD — reason]` and a matching Open Question.

### FR-01 — [short title]  *(P0, event-driven)*

When <trigger>, the <system> shall <response>.

*Rationale (optional, one line):* …

#### Acceptance Criteria

- **AC-01.1** — Given …, when …, then … .
- **AC-01.2** — Given <boundary value>, when …, then … .

---

### FR-02 — [failure-handling title]  *(P0, unwanted-behaviour)*

If <dependency is unavailable / input is invalid / limit is reached>, then the <system> shall <observable, recoverable response>.

#### Acceptance Criteria

- **AC-02.1** — Given <failure condition>, when …, then <user-visible outcome>, and <no data is lost / state is unchanged>.

---

### FR-03 — [business-decision what-if]  *(P1, unwanted-behaviour)*

If <two users edit the same item concurrently>, then the <system> shall [TBD — conflict policy is a product decision; see OQ-01].

#### Acceptance Criteria

- **AC-03.1** — Given …, when …, then [TBD — pending OQ-01].

---

## Non-Functional Requirements  <!-- gated: infra-platform-change -->

<!-- Only feature-specific requirements that exceed or differ from the platform baseline. Do not restate inherited baseline. -->

| ID     | Category | Requirement | Target | Verification |
|--------|----------|-------------|--------|--------------|
| NFR-01 | Latency  | …           | p95 ≤ … ms | … |

---

## Capacity & Performance Targets  <!-- gated: infra-platform-change; technical|mixed -->

| Dimension | Day-1 target | 12-month target |
|-----------|--------------|-----------------|

---

## Security & Compliance  <!-- gated: security-surface -->

[Trust boundaries, auth flows, data classification, key management.]

---

## Threat Model Summary  <!-- gated: security-surface; technical|mixed -->

| Threat | Mitigation | Owner |
|--------|------------|-------|

---

## Regulatory & Privacy  <!-- gated: regulatory-load -->

[Name the specific regime(s) in scope; defer specifics to user-supplied guidance.]

---

## Data Model  <!-- gated: persistence-data; technical|mixed -->

[Entities, relationships, retention, lifecycle.]

---

## Telemetry & Analytics  <!-- gated: persistence-data -->

| Event | Trigger | Properties | Purpose |
|-------|---------|------------|---------|

---

## API Contract  <!-- gated: public-api-surface; technical|mixed -->

[Public endpoints / SDK surface.]

---

## Versioning & Deprecation Policy  <!-- gated: public-api-surface; technical|mixed -->

[Semver, support window, deprecation notice cadence.]

---

## Dependencies  <!-- gated: cross-team-scope -->

| Dependency | Owner | Status | Risk if blocked |
|------------|-------|--------|-----------------|

---

## Rollout Plan  <!-- gated: rollout-risk -->

| Phase | Audience | Gate | Owner |
|-------|----------|------|-------|

---

## Rollback Strategy  <!-- gated: rollout-risk -->

[Kill switch, data-migration reversal, rollback window.]

---

## Test Scenarios  <!-- gated: cross-team-scope OR infra-platform-change -->

| ID    | Scenario | Covers | Type (unit/integration/e2e/perf/security) |
|-------|----------|--------|-------------------------------------------|
| TS-01 | …        | FR-01, AC-02.1 | … |

---

## Risks & Mitigations

| ID   | Risk | Likelihood | Impact | Mitigation |
|------|------|------------|--------|------------|
| R-01 | …    | …          | …      | …          |

---

## Open Questions

| ID    | Question | Owner | Resolution due |
|-------|----------|-------|----------------|
| OQ-01 | What should happen when …? | … | … |

---

## Out of Scope

<!-- Empty is acceptable. Add an item only when surrounding language would lead a reader to assume it is in scope. -->

---

## Appendix: Glossary  <!-- optional -->

| Term | Definition |
|------|------------|

---

## Appendix: NFR↔FR Traceability  <!-- gated: infra-platform-change; technical|mixed -->

| NFR    | Touches FR(s) |
|--------|---------------|

---

## Appendix: Aliases & Deprecations  <!-- update of a published spec with renames -->

| Current name | Former name | Since | Notes |
|--------------|-------------|-------|-------|

---

## Technical Considerations  <!-- mixed spec_kind only -->

[Implementation-shaped detail the user supplied, isolated from behaviour-shaped FRs.]

---

## References  <!-- optional; omit when no footnote earned its place -->

[^example]: Title — durable authoritative URL.
