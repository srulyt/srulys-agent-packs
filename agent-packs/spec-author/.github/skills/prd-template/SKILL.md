---
name: prd-template
description: "Adaptive PRD section catalogue and complexity heuristic. Declares each section as mandatory or complexity-gated:<axis>, with industry-neutral names. Single source of truth for which sections to include and how to name them. Triggers on: PRD section list, PRD template, complexity heuristic, mandatory vs gated sections, adaptive sectioning."
---

# PRD Template — Adaptive Sectioning

This skill is the **single source of truth** for the section
catalogue and the complexity heuristic the `prd-drafter` and
`prd-critic` use. Both agents apply the identical rules so that
inclusion/omission decisions are reproducible and reviewable.

The template is **not a frozen byte-for-byte contract**. It is a
catalogue of section names + a heuristic. Simple specs are
correctly trimmed; complex specs retain everything.

## When to Use This Skill

Load this skill when:

- Building a `proposed-structure` to surface at Stop A
  (`@context-detective`).
- Deciding which sections to author (`@prd-drafter`).
- Scoring `mandatory-coverage` (D1) and `gated-appropriateness`
  (D2) (`@prd-critic`).

## Domain neutrality (read first)

Every section name in this catalogue is industry-neutral. The pack
does **not** ship industry-specific naming. If the user's
environment requires specific section vocabulary (regulated
workloads, vendor-specific quality attributes, particular
compliance regimes), the user supplies that framing via the prompt
or `.github/copilot-instructions.md`. The drafter respects
user-approved overrides at Stop A; otherwise it stays neutral.

## Section catalogue

### Mandatory sections (always present)

| Section | Purpose | ID convention |
|---------|---------|---------------|
| Document Information | Status, version, owners, reviewers, last-updated | — |
| Problem Statement | What problem, who feels it, evidence | — |
| Goals & Success Metrics | Business / user / technical outcomes; measurable | — |
| Users & Personas | Primary users, their needs, expected outcome | — |
| Solution Summary | Proposed approach at a high level | — |
| Functional Requirements | What the system does | `FR-NN` |
| Acceptance Criteria | Testable conditions for FRs | `AC-NN` |
| Risks & Mitigations | Identified risks + mitigation per risk | `R-NN` |
| Open Questions | Unresolved decisions; nothing silent | `OQ-NN` |
| Out of Scope | Explicit non-goals | — |

A `mandatory` section is present in every spec. If content is
genuinely unknown, the drafter writes `[TBD — <reason>]` and adds
a corresponding `OQ-NN` entry to "Open Questions".

### Complexity-gated sections (include only when an axis triggers)

| Section | Triggering axis | ID convention |
|---------|-----------------|---------------|
| Stakeholders & Reviewers | cross-team-scope | — |
| Dependencies & Assumptions | cross-team-scope | — |
| Non-Functional Requirements | infra-platform-change | `NFR-NN` |
| Capacity & Performance Targets | infra-platform-change | — |
| Security & Compliance | security-surface | — |
| Threat Model Summary | security-surface | — |
| Regulatory & Privacy | regulatory-load | — |
| Data Model | persistence-data | — |
| Telemetry & Analytics | persistence-data | — |
| API Contract | public-api-surface | — |
| Versioning & Deprecation Policy | public-api-surface | — |
| Rollout Plan | rollout-risk | — |
| Rollback Strategy | rollout-risk | — |
| Test Scenarios | cross-team-scope OR infra-platform-change | `TS-NN` |
| Appendix: Glossary | optional polish | — |
| Appendix: NFR↔FR Traceability | infra-platform-change | — |
| Appendix: Aliases & Deprecations | update-mode rename history | — |

A `complexity-gated` section is included only when at least one
triggering axis fires. Each include / omit decision is justified
in `section-decisions-json`.

## Complexity heuristic

For each axis, score the spec request:

| Axis | "High" signal — include the gated section(s) |
|------|----------------------------------------------|
| **cross-team-scope** | More than one engineering team owns delivery; named partner orgs; cross-org dependencies. |
| **security-surface** | Auth flow change, new data egress, PII handling, supply-chain change, new trust boundary. |
| **infra-platform-change** | New service, new region, new datastore, breaking API, capacity-shaping change. |
| **regulatory-load** | Any regulatory or compliance review is in scope (the user names the regime — e.g. GDPR, HIPAA, SOC2, accessibility). Defer specifics to user-supplied instructions; do not encode any specific regime's conventions. |
| **persistence-data** | New schema, retention policy change, new analytics events. |
| **public-api-surface** | External consumers, SDK changes, webhooks, customer-visible API. |
| **rollout-risk** | Phased release, feature flags, kill switch needed, customer migration. |

If the inputs do not unambiguously confirm an axis, treat it as
**not triggered** for the proposed structure but list the
ambiguity in `open-questions-json` so Stop A can resolve it.

## Section ordering

Recommended top-level ordering when included:

1. Document Information
2. Problem Statement
3. Goals & Success Metrics
4. Users & Personas
5. Stakeholders & Reviewers (gated)
6. Solution Summary
7. Functional Requirements
8. Acceptance Criteria
9. Non-Functional Requirements (gated)
10. Capacity & Performance Targets (gated)
11. Security & Compliance (gated)
12. Threat Model Summary (gated)
13. Regulatory & Privacy (gated)
14. Data Model (gated)
15. Telemetry & Analytics (gated)
16. API Contract (gated)
17. Versioning & Deprecation Policy (gated)
18. Dependencies & Assumptions (gated)
19. Rollout Plan (gated)
20. Rollback Strategy (gated)
21. Test Scenarios (gated)
22. Risks & Mitigations
23. Open Questions
24. Out of Scope
25. Appendices (Glossary, NFR↔FR Traceability, Aliases & Deprecations, Citations)

The drafter may reorder when the user's Stop A reply explicitly
requests it; otherwise stick to the canonical order.

## Anti-patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Including every gated section "to be safe" | Bloated specs nobody reads | Apply the heuristic; record `gated-omitted` reasons. |
| Omitting a gated section despite a triggering axis in the inputs | Underspecification; D2 penalty | Include it; cite the axis. |
| Renaming sections to vendor- or industry-specific labels without user opt-in | Domain leakage; this pack is generic | Use neutral names. User-approved overrides at Stop A are the only exception. |
| Renumbering existing requirement IDs in update mode | Breaks external references | Keep IDs stable; mark deprecations in place. |

## References

- [Section catalogue (machine-readable)](references/section-catalogue.md)
- [Neutral specification template](references/specification-template.md) — a
  full worked example showing every section. Reference material; the
  drafter does not literal-copy from it.
- [`state.json` schema](references/state-schema.md) — field table and
  JSON Schema for the per-session orchestrator state file.
