---
name: story-telling-agent-smoke-critical-gaps
target: story-orchestrator
kind: agent
tags: [pack, slow]
timeout: 600
---

# Thin brief surfaces gaps and blocks build

## Description
Gaps-detection path: a thin brief with no audience, no decision, no facts must produce `status: needs-clarification` and a populated `gaps.md` -- NOT a fabricated proposal and certainly NOT a built deck.

Ported from legacy `cases/smoke-critical-gaps/`.

## Act
```prompt
@story-orchestrator

Make me a presentation about our product.

That's all I have for you. Go.
```

## Assert
```yaml
files:
  exists:
    - ".story-telling-stm/runs/*/state.json"
    - ".story-telling-stm/runs/*/agents/story-strategist/gaps.md"
  absent:
    - ".story-telling-stm/runs/*/agents/deck-builder/output.pptx"
matches:
  - { path: ".story-telling-stm/runs/*/agents/story-strategist/gaps.md", pattern: '\S' }
not_contains:
  - { path: ".story-telling-stm/runs/*/state.json", text: '"user_approved": true' }
  - { path: ".story-telling-stm/runs/*/state.json", text: '"phase": "build"' }
  - { path: ".story-telling-stm/runs/*/state.json", text: '"current_phase": "build"' }
```
