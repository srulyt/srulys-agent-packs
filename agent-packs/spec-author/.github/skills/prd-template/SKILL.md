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
| Document Information | Status, version, owners, reviewers, last-updated. Note: `Status:` and `Version:` semantics are governed by [`versioning-discipline`](../versioning-discipline/SKILL.md) (V1, V2, V15) — not by this skill. | — |
| Problem Statement | What problem, who feels it, evidence | — |
| Goals & Success Metrics | Business / user / technical outcomes; measurable | — |
| Users & Personas | Primary users, their needs, expected outcome | — |
| Solution Summary | Proposed approach at a high level | — |
| Functional Requirements | What the system does, written as **EARS shall-statements** (one `shall` per FR) — see [`spec-driven-prd-best-practices` §4a](../spec-driven-prd-best-practices/SKILL.md#4a-ears--easy-approach-to-requirements-syntax) for the pattern catalogue. ACs are nested under each FR as Given/When/Then scenarios. | `FR-NN`; ACs `AC-<FR>.<n>` |
| Risks & Mitigations | Identified risks + mitigation per risk | `R-NN` |
| Open Questions | Unresolved decisions; nothing silent | `OQ-NN` |
| Out of Scope | Explicit non-goals that pass the adjacency-by-language test in [`spec-driven-prd-best-practices` §7](../spec-driven-prd-best-practices/SKILL.md#7-out-of-scope-is-a-section-but-not-a-fishing-expedition). The section header is mandatory; the bullet list MAY be empty when no non-goal is load-bearing. Empty is preferred to fabricated negations. | — |

A `mandatory` section is present in every spec. If content is
genuinely unknown, the drafter writes `[TBD — <reason>]` and adds
a corresponding `OQ-NN` entry to "Open Questions". An empty
Out-of-Scope list is NOT "genuinely unknown" — it is a deliberate
signal that no negation passes the adjacency test. Do not write
`[TBD]` there.

**Acceptance Criteria are NOT a separate top-level section.** Each
FR carries its own `#### Acceptance Criteria` sub-section with one
or more `AC-<FR>.<n>` Given/When/Then scenarios. This eliminates
the FR↔AC traceability mismatch that arises from a flat AC table.

### Per-section isolation contract (upper sections)

The mandatory upper sections form a **shoulder** of the spec.
Each carries a single, focused job. Cross-pollination — restating
the problem inside the solution, smuggling ownership into goals,
discussing implementation inside the problem — is the leading
defect on revision turn 2+ and dilutes every section's signal.

| Section | MUST contain | MUST NOT contain |
|---|---|---|
| Document Information | Status, version, owners, reviewers, last-updated, `Updates:` / `Obsoletes:` header (update mode), `## Changes since vN` preamble (re-draft only). | Problem narrative, goals, solution mechanics, ownership rationale, rollout plan. |
| Problem Statement | What is broken today, who feels it, evidence (numbers / quotes / telemetry). | Solution direction ("we will…"), goals ("the goal is to…"), ownership ("the X team owns…"), rollout, FR-level detail. |
| Goals & Success Metrics | Outcomes (baseline + target + window) the work is judged against. | Problem restatement, solution mechanics, FRs in disguise, ownership, rollout. |
| Users & Personas | Primary users, their context, their expected outcome. | Solution mechanics ("they will use feature X"), ownership, success metrics. |
| Stakeholders & Reviewers (gated) | Named accountable parties and their decision rights. | Problem restatement, goals, FRs, rollout plan. |
| Solution Summary | The chosen approach at the highest level — what we are building, in one short paragraph. | Problem restatement, goals restatement, ownership, FR enumeration, AC detail, trade-off / alternatives reasoning (→ Risks & Mitigations / Alternatives), per-FR rationale (→ FR `*Rationale*` line), rollout / migration detail (→ Rollout Plan). |
| Out of Scope | Explicit, load-bearing non-goals that pass the §7 adjacency test. | Boilerplate negations; restatements of "we will" claims from Solution Summary. |

**The isolation test the drafter and critic both apply.** For each
candidate sentence in an upper section:

1. Read the sentence in isolation.
2. Ask: *"Which of the seven upper-section jobs does this sentence
   primarily do?"* If the answer is not the heading of the section
   the sentence currently sits under, the sentence is misplaced.
3. Move it to its correct home, or drop it if no home exists and
   §10's lower-section displacement test does not place it.

This rule operates **alongside** §10's lower-section displacement
heuristic. §10 catches "this belongs in an FR rationale / risk /
OQ"; this rule catches "this belongs in a different upper section".
Both apply on every authoring and review pass.

### Complexity-gated sections (include only when an axis triggers)

| Section | Triggering axis | Requires `spec_kind` | ID convention |
|---------|-----------------|----------------------|---------------|
| Stakeholders & Reviewers        | cross-team-scope            | any                | — |
| Dependencies & Assumptions      | cross-team-scope            | any                | — |
| Non-Functional Requirements     | infra-platform-change       | any (NFRs are product-visible) | `NFR-NN` |
| Capacity & Performance Targets  | infra-platform-change       | technical OR mixed | — |
| Security & Compliance           | security-surface            | any                | — |
| Threat Model Summary            | security-surface            | technical OR mixed | — |
| Regulatory & Privacy            | regulatory-load             | any                | — |
| Data Model                      | persistence-data            | technical OR mixed | — |
| Telemetry & Analytics           | persistence-data            | any                | — |
| API Contract                    | public-api-surface          | technical OR mixed | — |
| Versioning & Deprecation Policy | public-api-surface          | technical OR mixed | — |
| Rollout Plan                    | rollout-risk                | any                | — |
| Rollback Strategy               | rollout-risk                | any                | — |
| Test Scenarios                  | cross-team-scope OR infra-platform-change | any  | `TS-NN` |
| Technical Considerations        | any technical signal in `mixed` mode | mixed only | — |
| Appendix: Glossary              | optional polish             | any                | — |
| Appendix: NFR↔FR Traceability   | infra-platform-change       | technical OR mixed | — |
| Appendix: Aliases & Deprecations| update-mode rename history  | any                | — |

A `complexity-gated` section is included only when at least one
triggering axis fires **AND** the user-chosen `spec_kind` permits
it. Each include / omit decision is justified in
`section-decisions-json`. A section whose axis fires but whose
`Requires spec_kind` is not satisfied is recorded as
`gated-omitted-by-spec-kind`.

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
7. Functional Requirements (each FR carries its nested
   `#### Acceptance Criteria` block — there is no separate
   top-level Acceptance Criteria section)
8. Non-Functional Requirements (gated)
9. Capacity & Performance Targets (gated, technical/mixed only)
10. Security & Compliance (gated)
11. Threat Model Summary (gated, technical/mixed only)
12. Regulatory & Privacy (gated)
13. Data Model (gated, technical/mixed only)
14. Telemetry & Analytics (gated)
15. API Contract (gated, technical/mixed only)
16. Versioning & Deprecation Policy (gated, technical/mixed only)
17. Dependencies & Assumptions (gated)
18. Rollout Plan (gated)
19. Rollback Strategy (gated)
20. Test Scenarios (gated)
21. Risks & Mitigations
22. Open Questions
23. Out of Scope
24. Technical Considerations (gated, **mixed mode only**; carries
    any implementation-shaped detail isolated from FRs)
25. Appendices (Glossary, NFR↔FR Traceability, Aliases &
    Deprecations, References — optional)

The drafter may reorder when the user's Stop A reply explicitly
requests it; otherwise stick to the canonical order.

## Anti-patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Including every gated section "to be safe" | Bloated specs nobody reads | Apply the heuristic; record `gated-omitted` reasons. |
| Omitting a gated section despite a triggering axis in the inputs | Underspecification; D2 penalty | Include it; cite the axis. |
| Renaming sections to vendor- or industry-specific labels without user opt-in | Domain leakage; this pack is generic | Use neutral names. User-approved overrides at Stop A are the only exception. |
| Renumbering existing requirement IDs in update mode | Breaks external references | Keep IDs stable; mark deprecations in place. |
| Including a "Data Model" or "API Contract" section in a `product`-mode spec because inputs mention a datastore | Implementation leakage; the PRD becomes a design doc | Restrict implementation-shaped sections to `spec_kind: technical` or `mixed`; in `mixed`, place them under the Technical Considerations appendix, not inside FRs. |
| Auto-listing "Implementation details are out of scope" in Out of Scope | Redundant with product-mode posture; reads as defensive | Omit. List only domain-meaningful non-goals. |
| FRs that name an internal component, library, or storage technology | Locks engineering choice from the PRD | Re-cast the FR as a behaviour the system must exhibit; move technology references to Technical Considerations in `mixed` mode, or drop entirely in `product` mode. |

## References

- [Section catalogue (machine-readable)](references/section-catalogue.md)
- [Neutral specification template](references/specification-template.md) — a
  full worked example showing every section. Reference material; the
  drafter does not literal-copy from it.
- [`state.json` schema](references/state-schema.md) — field table and
  JSON Schema for the per-session orchestrator state file.
