---
name: story-telling-agent-smoke-visual-qa-loop
target: story-orchestrator
kind: agent
tags: [pack, slow]
timeout: 1500
---

# QA revise loop

## Description
QA revise-loop: deck-builder produces an intentionally problematic first draft; deck-critic flags >=2 issues with `verdict: revise`; deck-builder retries with the top-fixes; deck-critic re-runs and passes. Verifies `qa_iteration` increments and the bounded retry cap (cap=2).

Ported from legacy `cases/smoke-visual-qa-loop/`.

## Act
```prompt
@story-orchestrator

Build me a deck for a quarterly product review.

**Audience**: head of product, head of design, head of engineering.

**Decision needed**: align on Q2 priorities.

**Facts**:
- Q1 shipped 3 features (advanced search, dashboard v2, API rate
  limiting).
- One feature missed Q1 (mobile redesign, slipped to Q2).
- Q2 candidates: mobile redesign, internationalization, audit logs.
- Capacity = 2 features in Q2.

**Tone**: candid; this is a working session, not a victory lap.

When you propose, I will respond ``APPROVED`` immediately.

Important instruction for deck-builder: in your FIRST draft,
intentionally overload slides 3 and 4 with bullet text (>50 words per
slide) and put two metrics on slide 5 with no source citation. This
will exercise the deck-critic's revision loop. After deck-critic's
first revise verdict, fix the top issues it identifies and let it
re-run.

Return the final .pptx path once QA verdicts pass.
```

## Assert
```yaml
files:
  exists:
    - ".story-telling-stm/runs/*/agents/deck-builder/output.pptx"
    - ".story-telling-stm/runs/*/agents/deck-critic/qa-report.json"
    - ".story-telling-stm/runs/*/state.json"
matches:
  - { path: ".story-telling-stm/runs/*/state.json", pattern: '"qa_iterations?"\s*:\s*[12]' }
```
