---
name: product-brief-negative-evidence-source-stm-leak
target: brief-orchestrator
kind: agent
tags: [pack, slow]
timeout: 600
---

# No STM paths cited as evidence

## Description
Negative: no evidence-log entry, contradictions entry, or final-brief source citation may reference a path under `.product-brief-agent-stm/` (working memory). STM files are NEVER valid evidence sources.

Ported from legacy `cases/negative-evidence-source-stm-leak/`. Where the legacy rubric inspected only the rubric-targets, the new test greps the evidence-log and the final brief directly for the forbidden prefix.

## Setup
```yaml
files:
  - { copy: "fixtures/negative_evidence_source_stm_leak", dest: "inputs" }
```

## Act
```prompt
@brief-orchestrator

Build a decision-grade brief from the materials in ``inputs/``. All
evidence citations must reference user-provided source files (under
``inputs/``). Working-memory paths beginning with
``.product-brief-agent-stm/`` are NOT valid citations.

Decision context: prioritisation for the FY26 product roadmap.
Audience: VP Product.
```

## Assert
```yaml
files:
  exists:
    - ".product-brief-agent-stm/runs/*/agents/evidence-analyst/evidence-log.md"
    - ".product-brief-agent-stm/runs/*/agents/brief-orchestrator/product-brief.md"
not_contains:
  - { path: ".product-brief-agent-stm/runs/*/agents/evidence-analyst/evidence-log.md", text: "(.product-brief-agent-stm/" }
  - { path: ".product-brief-agent-stm/runs/*/agents/evidence-analyst/evidence-log.md", text: "](.product-brief-agent-stm/" }
  - { path: ".product-brief-agent-stm/runs/*/agents/evidence-analyst/evidence-log.md", text: "`.product-brief-agent-stm/" }
  - { path: ".product-brief-agent-stm/runs/*/agents/brief-orchestrator/product-brief.md", text: "(.product-brief-agent-stm/" }
  - { path: ".product-brief-agent-stm/runs/*/agents/brief-orchestrator/product-brief.md", text: "](.product-brief-agent-stm/" }
  - { path: ".product-brief-agent-stm/runs/*/agents/brief-orchestrator/product-brief.md", text: "`.product-brief-agent-stm/" }
```
