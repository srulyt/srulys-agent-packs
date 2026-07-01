---
name: product-brief-negative-orchestrator-paraphrase
target: brief-orchestrator
kind: agent
tags: [pack, slow, judge]
timeout: 600
---

# Orchestrator persists draft verbatim

## Description
Negative: orchestrator must persist the composer's draft fence VERBATIM to `product-brief.draft.md` before any editing pass.

Best-effort port of legacy `cases/negative-orchestrator-paraphrase/`: the legacy harness diff-checked the persisted draft against the captured fence body. Without trace capture, we instead assert (a) the draft exists and is substantial, and (b) a judge inspects the draft for paraphrase-style markers (rewording of headings, summary-collapses, omitted bullets relative to the composer's mandated structure).

## Setup
```yaml
files:
  - { copy: "fixtures/negative_orchestrator_paraphrase", dest: "inputs" }
```

## Act
```prompt
@brief-orchestrator

Build a brief from ``inputs/``. After the composer returns its
``product-brief-draft`` fence, the orchestrator MUST persist the
fence body byte-for-byte to ``product-brief.draft.md`` before any
editing pass. Paraphrasing or "improving" the body during persistence
is a violation.

Decision context: hiring plan for FY26. Audience: head of engineering.
```

## Assert
```yaml
files:
  exists:
    - ".product-brief-agent-stm/runs/*/agents/brief-composer/product-brief.draft.md"
    - ".product-brief-agent-stm/runs/*/agents/brief-orchestrator/product-brief.md"
matches:
  - { path: ".product-brief-agent-stm/runs/*/agents/brief-composer/product-brief.draft.md", pattern: '^.{401,}$', flags: "s" }
judge:
  artifact: ".product-brief-agent-stm/runs/*/agents/brief-composer/product-brief.draft.md"
  threshold: 0.7
  criteria: |
    Score 1.0 if the persisted draft contains the full composer-style structure (multiple labelled sections such as Context, Evidence / Findings, Options or Recommendation, plus inline source citations) and shows no signs of orchestrator paraphrasing (no first-person orchestrator commentary, no 'summary:' compressions of bulleted lists, no removed evidence tables). Score 0.5 if the draft is structurally complete but obviously condensed. Score 0.0 if the draft reads as an orchestrator-written summary rather than a composer-authored decision brief.
```
