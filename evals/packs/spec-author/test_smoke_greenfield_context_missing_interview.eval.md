---
name: spec-author-greenfield-context-missing-interview
target: spec-author
kind: agent
tags: [smoke, slow, pack]
timeout: 1200
---

# Missing greenfield context produces interview artifacts and answered sections

## Description
Greenfield creation where the detective finds P0 gaps. Stop B fires (interviewer generates a gap-closure-sized question set — no tight cap); user provides answers; detective re-runs; Stop A; APPROVE; drafter; critic. Asserts the interview artifacts are produced and the drafter does not leave `[TBD]` placeholders for sections the user actually answered.

Ported from legacy `cases/smoke-greenfield-context-missing-interview/`.

## Setup
```yaml
files:
  - { copy: "fixtures/greenfield_context_missing_interview", dest: "." }
```

## Act
```prompt
@spec-author write a PRD for **Workspace activity digest** -- a daily
summary of changes in a product workspace.

Treat this as an early-stage idea. I have no persona doc, no spike
notes, no reference links. You will need to interview me to fill
the gaps before drafting.

When you ask me clarifying questions (Stop B), I will answer them
all. When you then propose the structure (Stop A), I will reply
`APPROVE`.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop 0 (output location):** `output_path: docs/specs/digest.md, spec_kind: mixed`
- **Stop B (interview answers) -- pre-supplied:** the interview
  answers covering all P0 questions are pre-staged at
  `interview-answers.md` in the workspace; treat them as the user's
  first reply to your interview, then proceed to drafting without
  parking.
- **Stop A (structure approval):** `APPROVE` (first ask)

The orchestrator should still invoke prd-interviewer once (so the
`interview-questions.md` artifact is produced and the rubric can
check it), then immediately apply the answers above and proceed.
```

## Assert
```yaml
files:
  exists:
    - docs/specs/digest.md
    - ".spec-author/sessions/*/artifacts/interview-questions.md"
    - ".spec-author/sessions/*/*/interview-answers.md"
not_contains:
  - { path: "docs/specs/digest.md", text: "[TBD - Problem Statement" }
  - { path: "docs/specs/digest.md", text: "[TBD - Goals" }
  - { path: "docs/specs/digest.md", text: "[TBD - Personas" }
  - { path: "docs/specs/digest.md", text: "[TBD - Solution Summary" }
```
