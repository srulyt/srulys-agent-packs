---
name: story-telling-agent-smoke-executive-buy-in
target: story-orchestrator
kind: agent
tags: [pack, smoke, judge]
timeout: 900
---

# Smoke Executive Buy In

## Act
```prompt
Build an evidence-calibrated executive decision deck from `examples/buy-in/context.md`. Use both formats. Stop for proposal approval before composing.
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
    Score 1.0 only when all requirements hold. The response MUST frame a clear decision and stakes, preserve sourced/unsupported claim distinctions, anticipate objections, use assertion headlines, show executive restraint, and follow approval before composition.
    Score 0.5 for partial compliance and 0.0 for missing artifacts, fabricated evidence, bypassed gates, or off-topic output.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better, baseline: rolling_mean, tolerance: 0.1 }
```
