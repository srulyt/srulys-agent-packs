---
name: product-brief-smoke-early-stage-summary
target: brief-orchestrator
kind: agent
tags: [pack, slow, judge]
timeout: 600
---

# Early-stage summary from thin material

## Description
Smoke evals for the `product-brief` agent pack.

Ported from `evals/packs/product-brief/cases/smoke-early-stage-summary/`.

## Act
```prompt
@brief-orchestrator

I have a rough idea I want to put on paper for my own thinking. The
note is in `inputs/concept-note.md` -- it's just a few paragraphs
describing a hypothesis about a feature I might propose later.

Audience: just me, for now. No decision being asked. Please produce a
short brief that synthesizes what I have. If material is thin, that's
fine -- keep the brief short.
```

## Assert
```yaml
glob_count:
  - { pattern: ".product-brief-agent-stm/runs/*/agents/brief-orchestrator/product-brief.md", equals: 1 }
files:
  exists:
    - ".product-brief-agent-stm/runs/*/agents/brief-orchestrator/maturity-assessment.md"
judge:
  artifact: ".product-brief-agent-stm/runs/*/agents/brief-orchestrator/product-brief.md"
  threshold: 0.7
  criteria: |
    The brief MUST:
    1. Be focused with no padding or filler -- length should match the thin source material, but do not penalize thoroughness where clarity requires it (no fixed word cap).
    2. Reference the 'Pinned Insights' / starred-items concept from the user's note.
    3. End with a Summary-style closing section (NOT a 'Decision' or 'Recommendation' ask), because the user said 'no decision being asked'.
    4. Be free of writer-scaffolding / meta-commentary: no content-labels or announcing captions (e.g. 'What the customer gets:'), no design self-commentary ('...is deliberately simple', 'and that is the point'), no significance meta-commentary ('this matters because...', 'the value of this is...'), and no emphasis-only 'X, not Y' contrast where the positive claim already stands. Judge the CLASS (writer-narration that serves the author, not the reader), not these exact phrases -- penalize unseen variants that fit the class; do not reward a brief that merely avoided the listed phrases while keeping the pattern.
    Score 1.0 if all four. 0.5 if 2-3. 0 otherwise.
```
