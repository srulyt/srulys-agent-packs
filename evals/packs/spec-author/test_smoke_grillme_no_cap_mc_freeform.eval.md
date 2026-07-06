---
name: spec-author-grillme-no-cap-mc-freeform
target: spec-author
kind: agent
tags: [smoke, slow, pack, judge]
timeout: 1200
---

# Grill-me interview: no artificial cap, MC with deferral + freeform

## Description
Requirement 2 (grill-me): when the detective finds P0 gaps, the
interviewer produces a gap-closure-sized question set (NOT truncated
at 12). Enumerable gaps are rendered as multiple-choice questions that
include a "Not sure / decide later" deferral option and NO literal
"Other" bucket; open-ended gaps are freeform.

## Setup
```yaml
files:
  - { copy: "fixtures/grillme_no_cap_mc_freeform", dest: "." }
```

## Act
```prompt
@spec-author write a PRD for **Assigned-to-me activity list** -- a
feature that shows each user what work was assigned or reassigned to
them across projects.

Treat this as an early-stage idea. I have deliberately provided NO
persona doc, NO metrics, NO solution notes, and NO reference links.
You will need to interview me (grill me) to close the gaps before
drafting. Ask as many gap-closing questions as you genuinely need --
do not stop early. Use multiple-choice where the answer is a bounded
set, freeform where it is open-ended.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop 0 (output location):** `output_path: docs/specs/assigned.md, spec_kind: mixed`
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
    - docs/specs/assigned.md
    - ".spec-author/sessions/*/artifacts/interview-questions.md"
contains:
  - { path: ".spec-author/sessions/*/artifacts/interview-questions.md", text: "Not sure / decide later" }
judge:
  artifact: ".spec-author/sessions/*/artifacts/interview-questions.md"
  threshold: 0.7
  criteria: |
    The interview question set is a grill-me interrogation. It MUST:
    1. Contain at least one multiple-choice question that offers a
       bounded set of options AND includes an explicit "Not sure /
       decide later" deferral option.
    2. NOT use a literal "Other" option/bucket in any multiple-choice
       question (the freeform affordance covers that instead).
    3. Contain at least one freeform (open-ended) question for a
       qualitative gap (e.g. the problem, the outcome metric, or the
       solution shape), AND show no sign of being artificially
       truncated to a fixed count like 12 -- the set is sized by the
       gaps present, one gap per question.
    Score 1.0 only if all three hold. Score 0.5 if 2/3. Score 0 if 0-1.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better,
      baseline: rolling_mean, tolerance: 0.1 }
```
