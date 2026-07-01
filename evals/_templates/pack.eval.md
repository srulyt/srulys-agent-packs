---
name: PACK-NAME-short-slug
target: your-agent-id
kind: agent
tags: [pack, smoke]
timeout: 900
---

# One-line title of what this eval proves

## Description
What this eval checks and why. Keep it to a few sentences.

## Setup
Optional. Copy fixtures into the isolated workspace before the agent runs:

```yaml
files:
  - fixtures/seed.md
```

## Act
```prompt
The instruction given to the agent under test. Be explicit and bounded so
the run is deterministic and cost-capped.
```

## Assert
```yaml
files:
  exists:
    - "output/expected.md"
  absent:
    - "should-not-exist.txt"
  contains:
    - path: "output/expected.md"
      text: "a required phrase"
judge:
  artifact: "output/expected.md"
  threshold: 0.7
  criteria: |
    Score 1.0 only if <precise pass condition>. Score 0.0 otherwise. Be strict.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better,
      baseline: rolling_mean, tolerance: 0.1 }
```
