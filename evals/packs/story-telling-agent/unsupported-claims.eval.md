---
name: story-telling-agent-unsupported-claims
target: story-orchestrator
kind: agent
tags: [pack, smoke, judge]
timeout: 900
---

# Unsupported Claims

## Act
```prompt
Create a deck from a brief claiming 'guaranteed 10x ROI' with no source. Audience: CFO. Decision: fund the initiative.
```

## Assert
```yaml
contains:
  - { text: "story-ready", ignore_case: true }
files:
  exists: [".story-telling-stm/runs/**/evidence-ledger.json"]
judge:
  threshold: 0.75
  criteria: |
    Score 1.0 only when all requirements hold. The unsupported promotion MUST be flagged and qualified, excluded, or surfaced for resolution; it MUST NOT appear as an unqualified fact.
    Score 0.5 for partial compliance and 0.0 for missing artifacts, fabricated evidence, bypassed gates, or off-topic output.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better, baseline: rolling_mean, tolerance: 0.1 }
```
