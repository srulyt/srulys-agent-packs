---
name: story-telling-agent-visual-comparison
target: story-orchestrator
kind: agent
tags: [pack, slow, judge]
timeout: 1800
---

# Visual Comparison

## Act
```prompt
Produce a v3 deck from the buy-in example and compare its first and corrected 150-DPI renders against the legacy baseline.
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
    Score 1.0 only when all requirements hold. V3 MUST materially improve hierarchy, evidence-fit, typography, composition, imagery, accessibility, and decision clarity; correction MUST improve named defects without regressions.
    Score 0.5 for partial compliance and 0.0 for missing artifacts, fabricated evidence, bypassed gates, or off-topic output.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better, baseline: rolling_mean, tolerance: 0.1 }
```
