---
name: story-telling-agent-qa-retry
target: story-orchestrator
kind: agent
tags: [pack, slow, judge]
timeout: 1800
---

# Qa Retry

## Act
```prompt
Build a deck, treat the first staged render as having overlap and weak evidence-fit findings, and run the bounded correction workflow.
```

## Assert
```yaml
contains:
  - { text: "story-ready", ignore_case: true }
files:
  exists: [".story-telling-stm/runs/**/qa-report.json"]
judge:
  threshold: 0.75
  criteria: |
    Score 1.0 only when all requirements hold. The correction MUST address named findings, compare before/after, avoid regressions, rerun independent QA, respect the two-retry cap, and not weaken thresholds.
    Score 0.5 for partial compliance and 0.0 for missing artifacts, fabricated evidence, bypassed gates, or off-topic output.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better, baseline: rolling_mean, tolerance: 0.1 }
```
