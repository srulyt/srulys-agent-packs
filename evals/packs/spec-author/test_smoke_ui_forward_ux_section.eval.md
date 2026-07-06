---
name: spec-author-ui-forward-ux-section
target: spec-author
kind: agent
tags: [smoke, slow, pack, judge]
timeout: 1200
---

# UI-forward spec fires experience-surface and gets the dedicated UX section

## Description
Requirement 1: a clearly UI-forward feature (a new multi-screen
approval-workflow UI with distinct roles) must fire the
`experience-surface` complexity axis, so the detective proposes and
the drafter authors the gated "User Experience: Personas, Journeys &
Roles" section with concrete persona / journey / role content.
Context is supplied inline so no interview is needed.

## Act
```prompt
@spec-author write a PRD for **Expense Approval Workspace** -- a
NEW multi-screen product surface with these screens/flows:

- A **Requester** dashboard to submit an expense (multi-step wizard:
  details -> attach receipts -> review -> submit).
- An **Approver** review queue screen to approve/reject/return
  submissions, with a decision detail view.
- An **Admin** settings screen to configure approval thresholds and
  manage members.

This is UI-forward: new screens, navigation between them, a
multi-step submission flow, and behaviour that differs by user role.

Roles & context (already known -- no interview needed):
- **Requester**: any employee; can create and view their own
  submissions; cannot approve.
- **Approver**: team lead; can approve/reject/return submissions in
  their queue; cannot change thresholds.
- **Admin**: finance ops; can configure thresholds and manage
  members; cannot approve on behalf of an Approver.
Primary journey: Requester submits -> Approver reviews in queue ->
decision -> Requester notified.
Personas: Requester (busy employee, mobile+desktop), Approver (team
lead, desktop, reviews in batches), Admin (finance ops, rare logins).

## Pre-supplied answers (do not park; proceed straight through)

- **Stop 0 (output location):** `output_path: docs/specs/expense-approval.md, spec_kind: product`
- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end through detective -> drafter -> critic without
waiting for further user input.
```

## Assert
```yaml
files:
  exists:
    - docs/specs/expense-approval.md
    - .spec-author/sessions/*/artifacts/spec-review.md
contains:
  - { path: "docs/specs/expense-approval.md", text: "## User Experience: Personas, Journeys & Roles" }
judge:
  artifact: docs/specs/expense-approval.md
  threshold: 0.7
  criteria: |
    This is a UI-forward spec, so the experience-surface axis MUST
    have fired and the dedicated UX section MUST be present and
    concrete. The spec MUST:
    1. Contain a '## User Experience: Personas, Journeys & Roles'
       section.
    2. In (or under) that section, describe the three distinct roles
       (Requester, Approver, Admin) with what each can and cannot do
       -- a role/permission mapping, not just a mention.
    3. Include at least one user journey for the submit->review->
       decision flow (an ordered set of steps/phases), AND express
       role-conditioned behaviour in the Functional Requirements
       (e.g. only an Approver can approve; a Requester attempting to
       approve is denied).
    Score 1.0 only if all three hold. Score 0.5 if 2/3. Score 0 if 0-1.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better,
      baseline: rolling_mean, tolerance: 0.1 }
```
