---
name: story-telling-agent-smoke-buy-in-deck
target: story-orchestrator
kind: agent
tags: [pack, slow, judge]
timeout: 1200
---

# Buy-in deck happy path

## Description
Smoke evals for the `story-telling-agent` pack.

Ported from `evals/packs/story-telling-agent/cases/smoke-buy-in-deck/`.

## Act
```prompt
@story-orchestrator

We need a buy-in deck to take to **VP Engineering and Director of
Product** on Friday. The ask: **approve $200K Phase-1 budget** for the
platform team's reliability initiative.

Existing context: we ran a 6-week pilot, p95 latency dropped 38%, two
key on-call rotations stabilized. Phase-1 funds dedicated SRE headcount
and one quarter of capacity to extend the pattern across services.

Build the deck end-to-end (intake -> research -> proposal -> approval
gate -> build -> qa). Approve at the Stop-B gate when prompted -- this
is a non-interactive run, so do not pause for additional input.
```

## Assert
```yaml
files:
  exists:
    - ".story-telling-stm/runs/*"
glob_count:
  - { pattern: ".story-telling-stm/runs/*/**/*.md", min: 3 }
judge:
  artifact: ".story-telling-stm/runs/*/**/*.md"
  threshold: 0.7
  criteria: |
    The deck MUST:
    1. Address VP Engineering and Director of Product as the audience.
    2. Make a clear ask for $200K Phase-1 budget.
    3. Include evidence from the pilot (latency drop, on-call stabilisation).
    4. Be structured (sections / slide-like progression), not a single prose blob.
    Score 1.0 if all four. 0.6 if 3/4. 0 otherwise.
```
