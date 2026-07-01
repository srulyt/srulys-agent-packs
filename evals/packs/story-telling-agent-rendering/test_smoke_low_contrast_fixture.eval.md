---
name: story-telling-agent-rendering-low-contrast-fixture
target: story-orchestrator
kind: agent
tags: [pack, slow]
timeout: 900
---

# Low-contrast fixture blocks QA

## Description
F4 regression: a deck-spec with a low-contrast text/background pair (`#BBBBBB` text on `#F5F6FA` background, ratio < 2:1) must be flagged via `contrast_violations` by the runtime contrast pipeline, not silently downgraded to `contrast_unresolved`.

Ported from legacy `cases/smoke-low-contrast-fixture/`.

## Setup
```yaml
files:
  - { copy: "fixtures/smoke_low_contrast_fixture", dest: ".story-telling-stm/runs/smoke-low-contrast/agents/deck-builder" }
```

## Act
```prompt
@story-orchestrator

Run the deck-build / QA loop against the pre-staged session
``smoke-low-contrast``. The deck-spec on disk sets slide 2 text to ``#BBBBBB``
on a ``#F5F6FA`` background -- a contrast ratio well below the WCAG
4.5:1 normal-text threshold. The critic must emit ``verdict: revise``
with blocking finding ``contrast_violations``.
```

## Assert
```yaml
files:
  exists:
    - ".story-telling-stm/runs/*/agents/deck-critic/qa-report.json"
contains:
  - { path: ".story-telling-stm/runs/*/agents/deck-critic/qa-report.json", text: "contrast_violations" }
not_contains:
  - { path: ".story-telling-stm/runs/*/agents/deck-critic/qa-report.json", any: ['"status": "pass"', '"status":"pass"'], ignore_case: true }
```
