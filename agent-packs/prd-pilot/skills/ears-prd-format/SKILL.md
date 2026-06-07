---
name: ears-prd-format
description: "Step 4 of the EARS PRD workflow and the quality source-of-truth. Defines the 6 EARS shall-statement patterns, nested testable acceptance criteria, the lightweight mandatory PRD section catalogue, and a pre-present self-check. Triggers on: format the PRD, EARS shall statement, acceptance criteria, PRD sections, spec quality check, requirements syntax."
---

# EARS PRD Format & Quality Bar (step 4)

This skill is the EARS + PRD **quality source-of-truth**. It defines the
EARS shall-statement patterns, the lightweight mandatory section
catalogue, and a compact self-check the agent applies before presenting
the PRD. It is a distilled merge of `spec-author`'s
`spec-driven-prd-best-practices` (EARS), `prd-template` (mandatory
sections only), and a trimmed `prd-quality-rubric` (self-check, not a
separate critic pass).

## When to Use This Skill

Load this skill at **step 4**, after the outline is approved, to format
the final PRD — and any time you need to validate EARS shape.

## How to render the PRD (inline, verbatim sections)

Render the **complete PRD content inline in your response** — never
emit only an outline, a summary, or a pointer to an external file. Every
mandatory section below must be written out in full with real content.

Use the nine section names **exactly as written** in the catalogue
(verbatim, in order) as the document's headings. Do **not** rename,
merge, split, or substitute them (e.g. do not use "Overview" for
"Problem Statement", "Scope & Assumptions" for "Out of Scope", "Actors
& Definitions" for "Users & Personas", or "Non-Functional Requirements"
/ "Data & Token Model" / "Error & Edge Cases" in place of the canonical
set). Domain-specific detail belongs **inside** these sections (e.g. as
FRs, sub-bullets, or `[TBD]`+`OQ-NN`), not as renamed top-level
sections.

Under **Functional Requirements**, write each FR as a valid EARS
`shall`-statement (one of the six patterns) immediately followed by
**at least one** nested `Given / When / Then` acceptance criterion. Both
the shall-statement and its Given/When/Then ACs must be visible inline.

## EARS — Easy Approach to Requirements Syntax

Every Functional Requirement (FR) is written as **one** EARS
shall-statement using one of these six patterns:

| Pattern | Template |
|---------|----------|
| Ubiquitous       | `The <system> shall <response>.` |
| Event-driven     | `When <trigger>, the <system> shall <response>.` |
| State-driven     | `While <state>, the <system> shall <response>.` |
| Optional-feature | `Where <feature is included>, the <system> shall <response>.` |
| Unwanted         | `If <undesired condition>, then the <system> shall <response>.` |
| Complex          | A combination, e.g. `When X, while Y, the <system> shall <response>.` |

**Rules:**

- **Exactly one `shall` per FR.** Zero or multiple `shall`s is invalid.
- The `<system>` clause **names the product/component**, never "we" or
  "the user".
- Triggers and states are **observable conditions**, not intentions.
- Avoid passive voice in the response clause.
- EARS expresses **what**, never **how**. Implementation choices belong
  to engineering design, not the FR.

Worked examples for each pattern live in
[`references/ears-patterns.md`](references/ears-patterns.md).

## Acceptance criteria (nested, testable)

Each FR is paired with **one or more** Acceptance Criteria written as
**Given / When / Then** scenarios that verify the shall-statement. ACs
are nested under their FR with hierarchical IDs `AC-<FR>.<n>`. The
shall-statement is the contract; Given/When/Then is the verification.

> **FR-12** *(event-driven, P0)* — When a user opens an unread
> notification, the Notifications service shall mark it as read within
> 500ms p95.
>
> **AC-12.1** — Given a user has 1 unread notification, when the user
> taps it, then the unread badge decrements to 0 within 500ms in 95 of
> 100 sampled sessions.

Bad AC: "AC-03: The notification appears quickly." (not falsifiable)
Good AC: concrete inputs + observable, measurable result.

## Priority on requirements (P0/P1/P2)

Tag every FR: **P0** = blocker for first ship; **P1** = should-have;
**P2** = nice. This forces the team to declare minimum viable scope.

## Mandatory section catalogue (lightweight)

Include **all** of these sections, **using these exact names verbatim**,
in this order. (Heavyweight complexity-gated sections from `spec-author`
are intentionally dropped for speed.)

| Section | ID convention |
|---|---|
| Document Information | — |
| Problem Statement | — |
| Goals & Success Metrics | — |
| Users & Personas | — |
| Solution Summary | — |
| Functional Requirements | `FR-NN`; ACs nested as `AC-<FR>.<n>` |
| Risks & Mitigations | `R-NN` |
| Open Questions | `OQ-NN` |
| Out of Scope | — |

> "Acceptance Criteria" is **not** a separate top-level section. ACs
> live inside each FR with hierarchical IDs — this eliminates FR↔AC
> traceability mismatches.

## Unknowns: `[TBD]` + Open Questions discipline

Anything not yet decided becomes an `OQ-NN` entry in **Open Questions**.
The agent **never silently picks** an option the inputs do not
constrain. Where a section must reference an undecided value, write
`[TBD — <one-line reason>]` and add the matching `OQ-NN`. This addresses
the canonical failure mode: "the spec quietly assumes X, the team builds
X, the customer needed Y."

## Evidence discipline

Do not fabricate evidence or cite non-authoritative / session-local
sources. State honest uncertainty with a range and a reason rather than
inventing a precise figure.

## Pre-present self-check (run before showing the PRD)

This is a lightweight self-check, not a separate critic pass. It carries
the load-bearing dimensions of `spec-author`'s rubric (D1 coverage, D4
EARS/AC/evidence). Before presenting, verify:

- [ ] **Coverage (D1):** all 9 mandatory sections present, **named
      verbatim**, in order, and non-empty (or carrying an explicit
      `[TBD]`+`OQ-NN`).
- [ ] **Inline render:** the full PRD content is in the response itself,
      not replaced by an outline or an external-file pointer.
- [ ] **EARS validity (D4):** every FR matches one of the 6 patterns,
      has **exactly one** `shall`, names a system (not "we"/"the user"),
      and expresses **what, not how**.
- [ ] **Testable ACs (D4):** every FR has **≥1** Given/When/Then AC with
      concrete inputs and an observable result.
- [ ] **Open Questions:** every unknown has an `OQ-NN`; no silent guess.
- [ ] **Evidence:** no fabricated or non-authoritative citations.

If any FR fails the EARS check, **rewrite it** before presenting — do
not show a non-conforming FR.

## Must NOT

- MUST NOT emit an FR with zero or multiple `shall`s.
- MUST NOT use "we"/"the user" as the EARS `<system>`.
- MUST NOT put implementation ("how") inside an FR.
- MUST NOT leave an unknown silent — `[TBD — reason]` + `OQ-NN`.
- MUST NOT fabricate evidence or cite non-authoritative / session-local
  sources.
- MUST NOT rename, merge, or substitute any of the 9 mandatory section
  names — use them verbatim.
- MUST NOT emit only an outline, summary, or external-file pointer in
  place of the full inline PRD content.
