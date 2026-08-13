---
name: story-telling-agent-technical-read-ahead
target: story-orchestrator
kind: agent
tags: [pack, slow, judge]
timeout: 1800
---

# Technical Read Ahead

## Act
```prompt
Build a technical read-ahead from `examples/technical-review/context.md` with robust notes and both formats.
```

## Assert
```yaml
contains:
  - { text: "story-ready", ignore_case: true }
files:
  exists: [".story-telling-stm/runs/**/deck-spec.json"]
judge:
  threshold: 0.75
  criteria: |
    Score 1.0 only when all requirements hold. The artifact MUST layer precise technical detail, use readable hierarchy and navigation, preserve evidence IDs, and include useful speaker/read-ahead notes.
    Score 0.5 for partial compliance and 0.0 for missing artifacts, fabricated evidence, bypassed gates, or off-topic output.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better, baseline: rolling_mean, tolerance: 0.1 }
```
