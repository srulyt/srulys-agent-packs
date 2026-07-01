---
name: story-telling-agent-rendering-overflow-fixture
target: story-orchestrator
kind: agent
tags: [pack, slow]
timeout: 900
---

# Overflow fixture blocks QA

## Description
F1 regression: a deck-spec with a slide that intentionally overflows its body textbox is fed through the build/QA loop. The critic must detect the overflow via `check_pptx.py` (Pillow real-metric pipeline) and emit `verdict: revise` with blocking finding `overflow_violations`.

Ported from legacy `cases/smoke-overflow-fixture/`.

## Setup
```yaml
files:
  - { copy: "fixtures/smoke_overflow_fixture", dest: ".story-telling-stm/runs/smoke-overflow/agents/deck-builder" }
```

## Act
```prompt
@story-orchestrator

Run the deck-build / QA loop against the pre-staged session
``smoke-overflow``. The deck-spec on disk contains an intentional text
overflow on slide 3 (body text exceeds the textbox bounds when
rendered with real Pillow metrics). The critic must catch this and
emit ``verdict: revise`` with blocking finding ``overflow_violations``.
```

## Assert
```yaml
files:
  exists:
    - ".story-telling-stm/runs/*/agents/deck-critic/qa-report.json"
contains:
  - { path: ".story-telling-stm/runs/*/agents/deck-critic/qa-report.json", text: "overflow_violations" }
not_contains:
  - { path: ".story-telling-stm/runs/*/agents/deck-critic/qa-report.json", any: ['"status": "pass"', '"status":"pass"'], ignore_case: true }
```
