---
name: spec-author-grillme-ui-context-gaps
target: spec-author
kind: agent
tags: [smoke, slow, pack, judge]
timeout: 1200
---

# Grill-me interview raises persona/journey/RBAC gaps on a UI-forward spec

## Description
Bridge between Requirement 1 and Requirement 2: a UI-forward feature
with missing persona / journey / role context fires the
`experience-surface` axis, so the detective flags those user-context
gaps as P0 and the grill-me interview raises persona / JTBD / journey
/ roles-and-permissions questions before drafting.

## Setup
```yaml
files:
  - { copy: "fixtures/grillme_ui_context_gaps", dest: "." }
```

## Act
```prompt
@spec-author write a PRD for **Review Board** -- a NEW multi-screen
product surface where team members submit items for review and
reviewers decide on them. There are new screens (a submission form, a
reviewer queue, an admin settings screen), navigation between them,
and behaviour that differs by user role.

I have deliberately provided NO persona doc, NO journey description,
and NO role/permission definitions. Because this is UI-forward, please
grill me to close the persona, user-journey, and roles/permissions
gaps before drafting.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop 0 (output location):** `output_path: docs/specs/review-board.md, spec_kind: product`
- **Stop B (interview answers) -- pre-supplied:** the interview
  answers are pre-staged at `interview-answers.md` in the workspace;
  treat them as the user's reply to your grill-me questions, then
  proceed to drafting without parking.
- **Stop A (structure approval):** `APPROVE` (first ask)

The orchestrator MUST invoke prd-interviewer once (so the
`interview-questions.md` artifact is produced), then apply the answers
above and proceed.
```

## Assert
```yaml
files:
  exists:
    - docs/specs/review-board.md
    - ".spec-author/sessions/*/artifacts/interview-questions.md"
judge:
  artifact: ".spec-author/sessions/*/artifacts/interview-questions.md"
  threshold: 0.7
  criteria: |
    This is a UI-forward spec with missing user-context, so the
    grill-me interview MUST escalate user-context gaps. The question
    set MUST raise questions that close at least THREE of these four
    user-context areas, and at least one of them MUST be tagged P0:
    1. Personas / distinct user types.
    2. Jobs-to-be-done or the user's goal/need.
    3. The user journey / end-to-end steps or flow.
    4. Roles & permissions (who is allowed to do what; access control).
    Score 1.0 if >=3 areas are covered with at least one P0 among the
    user-context questions. Score 0.5 if exactly 2 areas covered.
    Score 0 if <=1 area covered.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better,
      baseline: rolling_mean, tolerance: 0.1 }
```
