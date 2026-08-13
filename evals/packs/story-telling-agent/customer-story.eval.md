---
name: story-telling-agent-customer-story
target: story-orchestrator
kind: agent
tags: [pack, judge]
timeout: 1800
---

# Customer Story

## Act
```prompt
Build a customer narrative from `examples/customer-story/context.md` without inventing facts.
```

## Assert
```yaml
contains:
  - { text: "story-ready", ignore_case: true }
files:
  exists: [".story-telling-stm/runs/**/story-plan.json"]
judge:
  threshold: 0.75
  criteria: |
    Score 1.0 only when all requirements hold. The story MUST have a credible human change arc and outcome while every factual claim is traceable or explicitly uncertain; no invented customer facts.
    Score 0.5 for partial compliance and 0.0 for missing artifacts, fabricated evidence, bypassed gates, or off-topic output.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better, baseline: rolling_mean, tolerance: 0.1 }
```
