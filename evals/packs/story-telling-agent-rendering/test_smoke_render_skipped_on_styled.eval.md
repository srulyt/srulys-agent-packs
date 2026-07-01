---
name: story-telling-agent-rendering-render-skipped-on-styled
target: story-orchestrator
kind: agent
tags: [pack, slow]
timeout: 900
---

# Styled deck with skipped render blocks QA

## Description
OQ5 regression: a styled-deck rendered with no soffice/libreoffice on PATH must NOT ship with `pass` or `pass_unverified`. The critic must emit `verdict: revise` with blocking finding `render_unverified`.

Ported from legacy `cases/smoke-render-skipped-on-styled/`.

## Setup
```yaml
files:
  - { copy: "fixtures/smoke_render_skipped_on_styled", dest: ".story-telling-stm/runs/smoke-render-skipped/agents/deck-builder" }
```

## Act
```prompt
@story-orchestrator

Run the deck-build / QA loop against the pre-staged session
``smoke-render-skipped``. The session's deck-spec contains a styled slide
(``style_recipe: hero_full_bleed``).

When the critic invokes ``render_pptx.py`` for QA, force the render
pipeline to skip by overriding PATH to a directory that contains none
of ``soffice``, ``libreoffice``, or ``unoconv`` (e.g. via
``env -i PATH=/tmp/empty python ...``). With ``render_engine=null``,
the critic MUST set ``verdict: revise`` and include
``render_unverified`` as a blocking finding -- it MUST NOT issue
``pass`` or ``pass_unverified`` for a styled deck.
```

## Assert
```yaml
files:
  exists:
    - ".story-telling-stm/runs/*/agents/deck-critic/qa-report.json"
contains:
  - { path: ".story-telling-stm/runs/*/agents/deck-critic/qa-report.json", text: "render_unverified" }
not_contains:
  - { path: ".story-telling-stm/runs/*/agents/deck-critic/qa-report.json", any: ['"status": "pass"', '"status":"pass"', '"status": "pass_unverified"', '"status":"pass_unverified"'], ignore_case: true }
```
