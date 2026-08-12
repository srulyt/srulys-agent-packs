---
name: copilot-factory-critic-veto-weak-architecture
target: copilot-factory
kind: agent
tags: [pack, slow, judge]
timeout: 900
---

# Critic blocks weak architecture

## Description
Critic-veto regression: a pre-staged weak architecture
(no agents/skills/boundaries) is in a session already at the current
`review-arch` phase. Architecture approval has not occurred and is not
permitted after a BLOCKING verdict. The critic must persist its verdict to
the canonical `architecture-review.md`; no build or implementation review may
occur.

Ported from legacy `cases/critic-veto-weak-architecture/`.

## Setup
```yaml
stage: { all: true }
files:
  - { copy: "fixtures/critic_veto_weak_architecture", dest: "." }
```

## Act
```prompt
A previous factory session was paused with a half-finished architecture.
Please resume the session under
`.copilot-factory/sessions/2026-01-15-deadbeef/` and run **only the
architecture review phase** (`review-arch`). Do NOT re-design, do NOT
build, do NOT involve the engineer. Just delegate the architecture
review to `@factory-critic` and report the verdict.
```

## Assert
```yaml
files:
  exists:
    - ".copilot-factory/sessions/*/artifacts/architecture-review.md"
judge:
  artifact: ".copilot-factory/sessions/*/artifacts/architecture-review.md"
  threshold: 0.7
  criteria: |
    Score 1.0 if the review verdict is BLOCKING/FAIL and the reasoning cites at least two concrete defects from the staged architecture (missing agents section, missing file-access boundaries, missing skills, missing failure modes, etc.). Score 0.5 if the verdict is BLOCKING but the cited defects are vague or only one is concrete. Score 0.0 if the review issues PASS or if the verdict text is absent.
```
