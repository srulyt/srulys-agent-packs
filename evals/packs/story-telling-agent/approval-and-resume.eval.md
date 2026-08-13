---
name: story-telling-agent-approval-and-resume
target: story-orchestrator
kind: agent
tags: [pack, smoke]
timeout: 900
---

# Approval And Resume

## Act
```prompt
Start a deck, stop before proposal approval, then describe the persisted resume behavior for a later explicit revision and approval.
```

## Assert
```yaml
contains:
  - { text: "story-ready", ignore_case: true }
files:
  exists: [".story-telling-stm/runs/**/state.json"]
judge:
  threshold: 0.75
  criteria: |
    Score 1.0 only when all requirements hold. The response MUST use event-backed approval, preserve completed valid phases, invalidate affected downstream lineage on revision, and never infer approval from prose.
    Score 0.5 for partial compliance and 0.0 for missing artifacts, fabricated evidence, bypassed gates, or off-topic output.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better, baseline: rolling_mean, tolerance: 0.1 }
```
