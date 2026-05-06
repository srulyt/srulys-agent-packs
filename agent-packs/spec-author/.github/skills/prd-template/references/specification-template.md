# Neutral Specification Template (reference)

This is a worked, **fully generic** example showing every section
in the catalogue. It is reference material — the drafter does not
literal-copy from it. Use it to understand section intent and
shape; produce content tailored to the user's request.

The template is industry-neutral. It contains no domain-specific
section names, vocabulary, or rules.

> **Authoring conventions** (also enforced by the drafter and
> critic):
>
> - Use markdown footnotes (`[^name]`) for evidence; never an
>   inline numbered "Citations" appendix table.
> - Cross-reference other sections with anchored links, e.g.
>   `[Acceptance Criteria](#acceptance-criteria)` — never bare
>   section names.
> - Every footnote must point at a durable, authoritative URL
>   (web, SharePoint, ADO, RFC, vendor doc, etc.). Never cite a
>   path the workspace's `.gitignore` matches. See
>   `spec-driven-prd-best-practices` §8 for the canonical,
>   `.gitignore`-driven evidence-discipline policy.
> - Functional Requirements are written as **single EARS
>   shall-statements**; Acceptance Criteria are nested under each
>   FR as `AC-<FR>.<n>` Given/When/Then scenarios.
> - Use headers (`#` / `##` / `###` / `####`) for layout. Do not
>   use bolded lines as pseudo-headers. Bold is for emphasis only.
> - Do not hard-wrap body prose — let editors wrap. Tables, lists,
>   code blocks, and footnote text retain their natural multi-line
>   structure.
> - In `spec_kind: product` and `mixed` mode, FRs MUST NOT name
>   internal components, libraries, datastores, frameworks,
>   languages, or specific APIs. Implementation-shaped content
>   goes under the "Technical Considerations" appendix (mixed) or
>   is omitted (product).

---

# [Feature / Product Name] — Specification

## Document Information

<!--
  `Status:` and `Version:` semantics are governed by the
  `versioning-discipline` skill (V1, V2, V15). New specs MUST start
  at `Status: draft` / `Version: 0.0.1-draft`. The `-draft` suffix
  agrees with `Status:` (present iff status==draft, absent iff
  status==published). See `.github/skills/versioning-discipline/SKILL.md`.
-->

- **Author(s)**: [Name(s)]
- **Created**: [YYYY-MM-DD]
- **Last Updated**: [YYYY-MM-DD]
- **Status**: draft | published   <!-- two-value enum per versioning-discipline §V1 -->
- **Reviewers**: [Names or "Pending assignment"]
- **Version**: 0.0.1-draft         <!-- semver; carries -draft iff status == draft -->
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

Each FR is a single EARS shall-statement and carries its own
nested `#### Acceptance Criteria` block. Do NOT use a flat
FR / AC table.

### FR-01 — [short title]  *(P0, ubiquitous)*

The <system> shall <response>.

*Rationale (1 line, optional):* …

#### Acceptance Criteria

- **AC-01.1** — Given …, when …, then … .
- **AC-01.2** — Given …, when …, then … .

---

### FR-02 — [short title]  *(P0, event-driven)*

When <trigger>, the <system> shall <response>.

#### Acceptance Criteria

- **AC-02.1** — Given …, when …, then … .

---

### FR-03 — [short title]  *(P1, unwanted-behaviour)*

If <undesired condition>, then the <system> shall <response>.

#### Acceptance Criteria

- **AC-03.1** — Given …, when …, then … .

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

## Technical Considerations  <!-- gated: mixed mode only -->

[In `spec_kind: mixed` only. Carries any implementation-shaped
detail (technology choices, data shapes, API surface notes,
capacity figures) the user supplied — isolated from FRs so the
product contract stays behaviour-shaped. Drop this section
entirely in `product` mode; in `technical` mode the content lives
inline in the dedicated sections (Data Model, API Contract, etc.).]

---

## References  <!-- optional; omit entirely if no footnote earned its place -->

The default for most specs is **no References section and no
footnotes** (see `spec-driven-prd-best-practices` §8). Include
this section only if at least one inline footnote survived the
high-value / authoritative-primary / not-gitignored gates. Example
of a qualifying footnote (do NOT copy — replace with a real
source):

[^standard-rfc7322]: IETF RFC 7322 — RFC Style Guide.
    https://www.rfc-editor.org/rfc/rfc7322
