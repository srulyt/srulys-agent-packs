---
name: product-brief-smoke-late-stage-decision-ask
target: brief-orchestrator
kind: agent
tags: [pack, slow, judge]
timeout: 600
---

# Late-stage Decision Ask brief

## Description
Smoke: late-stage Decision Ask brief (FY26 onboarding funding).

Exercises the full happy-path evidence-analyst -> strategy-modeler -> brief-composer flow and verifies the closing section is rendered as a Decision Ask. Ported from legacy `cases/smoke-late-stage-decision-ask/`.

## Setup
```yaml
files:
  - { copy: "fixtures/smoke_late_stage_decision_ask", dest: "inputs" }
```

## Act
```prompt
@brief-orchestrator

We need to build a decision-grade brief asking leadership to approve
funding for a new in-product onboarding flow next planning cycle.

Source material is in ``inputs/``. It includes:

- A draft funding ask (``funding-ask.md``)
- Customer research summary (``customer-research.md``)
- Two competing implementation options with cost ranges (``options.md``)
- Success metrics proposal (``metrics.md``)

Audience: VP Product + CFO. The decision required is **approve / reject
funding for FY26 onboarding redesign**. Please produce a full
late-stage decision brief.
```

## Assert
```yaml
files:
  exists:
    - ".product-brief-agent-stm/runs/*/agents/brief-orchestrator/product-brief.md"
    - ".product-brief-agent-stm/runs/*/agents/brief-orchestrator/handoff-report.md"
    - ".product-brief-agent-stm/runs/*/agents/evidence-analyst/evidence-log.md"
    - ".product-brief-agent-stm/runs/*/agents/strategy-modeler/decision-model.md"
    - ".product-brief-agent-stm/runs/*/agents/brief-composer/product-brief.draft.md"
judge:
  artifact: ".product-brief-agent-stm/runs/*/agents/brief-orchestrator/product-brief.md"
  threshold: 0.7
  criteria: |
    Score 1.0 if the brief is structured as a late-stage Decision Ask: names the explicit decision (approve/reject FY26 onboarding funding), names the decision audience (VP Product + CFO), presents at least two implementation options with cost trade-offs sourced from the input materials, ends with a clear recommendation or decision-required call-out, AND is free of writer-scaffolding / meta-commentary (no content-labels or announcing captions like 'What the customer gets:', no design self-commentary like '...is deliberately simple' / 'and that is the point', no significance meta-commentary like 'this matters because...' / 'the value of this is...', and no emphasis-only 'X, not Y' contrast where the positive claim already stands). Judge the writer-scaffolding CLASS (author-serving narration), not these exact phrases -- penalize unseen variants that fit the class and do not reward a brief that merely avoided the listed phrases. Score 0.5 if the brief covers the evidence and options but omits an explicit Decision Ask closing or carries noticeable writer-scaffolding. Score 0.0 if it reads as an exploratory summary with no decision framing.
```
