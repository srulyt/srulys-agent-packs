---
name: story-telling-agent-rendering-styled-recipe-render
target: story-orchestrator
kind: agent
tags: [pack, slow]
timeout: 900
---

# Styled recipe render records metric_xxl usage

## Description
F5 happy-path: a pre-staged deck-spec with one `style: styled` slide (`style_recipe: metric_xxl`) is built. The deck-builder must dispatch to `_styled_metric_xxl` and the build-log must reflect `styled-count: 1` with `metric_xxl` listed in `styled-recipes-used`.

Ported from legacy `cases/smoke-styled-recipe-render/`.

## Setup
```yaml
files:
  - { copy: "fixtures/smoke_styled_recipe_render", dest: ".story-telling-stm/runs/smoke-styled/agents/deck-builder" }
```

## Act
```prompt
@story-orchestrator

Run the deck-build / QA loop against the pre-staged session
``smoke-styled``. The session's deck-spec contains one slide with
``style: "styled"`` and ``style_recipe: "metric_xxl"``. Build the deck,
have the critic verify it, and stop when the critic returns a verdict.
```

## Assert
```yaml
files:
  exists:
    - ".story-telling-stm/runs/*/agents/deck-builder/output.pptx"
    - ".story-telling-stm/runs/*/agents/deck-builder/deck-spec.json"
    - ".story-telling-stm/runs/*/agents/deck-builder/build-log.txt"
matches:
  - { path: ".story-telling-stm/runs/*/agents/deck-builder/output.pptx", pattern: "." }
contains:
  - { path: ".story-telling-stm/runs/*/agents/deck-builder/build-log.txt", all: ["styled-count: 1", "metric_xxl"] }
```
