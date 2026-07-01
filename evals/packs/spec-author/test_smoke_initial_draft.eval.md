---
name: spec-author-initial-draft
target: spec-author
kind: agent
tags: [smoke, slow, judge]
timeout: 900
---

# Initial draft lands at draft state
> A newly created spec lands at `Status: draft` with a real PRD body and
> **no** CHANGELOG.

## Description
Smoke evals for the `spec-author` agent pack.

Ported from `evals/packs/spec-author/cases/smoke-creation-initial-draft-state/` (legacy YAML harness). Read top-to-bottom to understand the eval.

## Act
```prompt
@spec-author write a PRD for **Quick Toggle** -- a UI affordance that
lets a user flip a single setting (notifications on/off) from the
top-bar without opening Settings.

This is a brand-new spec. There is no existing spec at this path.
Treat as a single-team UI addition: no datastore, no API surface, no
security-surface change.

## Pre-supplied answers (do not park; proceed straight through)

This is a non-interactive run. Treat the following as already
answered -- do not pause at any `awaiting-*` park:

- **Stop 0 (output location):** `output_path: docs/specs/quick-toggle.md, spec_kind: product`
- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end through detective -> drafter -> critic without
waiting for further user input.
```

## Assert
```yaml
files:
  exists:
    - docs/specs/quick-toggle.md
    - .spec-author/sessions/*/artifacts/spec-review.md
  absent:
    - "**/CHANGELOG.md"
judge:
  artifact: docs/specs/quick-toggle.md
  threshold: 0.7
  criteria: |
    The spec MUST:
    1. Have a header containing 'Status: draft' and 'Version: 0.0.1-draft'
       (or equivalent draft markers).
    2. Describe the Quick Toggle UI feature (top-bar single-setting toggle).
    3. Be a real PRD with named sections, not a stub.
    Score 1.0 only if all three are met. Score 0.5 if 2/3. Score 0 if 0-1.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better,
      baseline: rolling_mean, tolerance: 0.1 }
```
