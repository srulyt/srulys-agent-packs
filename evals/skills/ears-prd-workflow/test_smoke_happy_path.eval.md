---
name: ears-prd-workflow-smoke-happy-path
target: ears-prd-workflow
kind: skill
tags: [skill, slow, judge]
timeout: 300
---

# Happy path produces an EARS PRD

## Description
Skill-in-isolation eval: ears-prd-workflow happy path (full 4-step flow).

Stages only the `ears-prd-workflow` skill and asks the default agent to produce an EARS PRD for a small, well-specified feature so it can run all four steps with minimal interrogation and write the document.

## Act
```prompt
Write an EARS-style PRD for a small, well-specified feature: a
"password reset via email" capability for an existing web app's Auth
service. Assume registered users have a verified email on file; the
reset link should be single-use and expire after 15 minutes.

Run the full workflow. Keep interrogation minimal since the feature is
well specified, propose a short outline, and (treating this approval as
granted) format the final PRD. Write it to `password-reset-prd.md` and
emit the `prd-outline` and `prd-summary` blocks in your final response.
```

## Assert
```yaml
stdout_contains:
  - { text: "prd-summary" }
  - { text: "Functional Requirements" }
judge:
  threshold: 0.7
  criteria: |
    The response completes a 4-step EARS PRD workflow. It MUST:
    1. Contain a PRD with the mandatory sections (Document Information, Problem Statement, Goals & Success Metrics, Users & Personas, Solution Summary, Functional Requirements, Risks & Mitigations, Open Questions, Out of Scope).
    2. Have at least 3 Functional Requirements, each a SINGLE valid EARS `shall` statement that names a system (not 'we'/'the user') and expresses what-not-how.
    3. Give each FR at least one nested Given/When/Then acceptance criterion.
    4. Include an Open Questions section.
    5. Emit a `prd-summary` fenced block.
    6. Contain NO fabricated citations or invented data.
    Score 1.0 only if all six are met. Score 0.5 if 4-5 met. Score 0.0 otherwise.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better,
      baseline: rolling_mean, tolerance: 0.1 }
```
