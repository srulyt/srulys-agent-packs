---
name: story-telling-agent-smoke-template-mode
target: story-orchestrator
kind: agent
tags: [pack, slow]
timeout: 900
---

# Template path round trip

## Description
Template-aware deck generation: when the user supplies a `.pptx` template, the deck-builder must invoke `generate_deck.py` with `--template` so the output deck inherits master slides and theme. Verifies path round-trip (not theme correctness).

Ported from legacy `cases/smoke-template-mode/`. The original case expected the user to drop a real corporate template under `inputs/templates/`; the hermetic eval generates a minimal placeholder via `python-pptx`.

## Act
```prompt
@story-orchestrator

I have a corporate PowerPoint template at
``templates/corporate-2026.pptx`` in this workspace. I need you to use
it as the base -- output deck must inherit its master slides, theme
colors, and font choices.

**Audience**: customer advisory board (8 enterprise customers).

**Decision needed**: customers volunteer for a 6-week pilot of our
new analytics module.

**Facts**:
- 3 customers already on the waitlist (Acme, Globex, Initech).
- Pilot includes weekly check-ins + dedicated support engineer.
- We need 5 total commitments to greenlight the GA timeline.

**Tone**: warm, peer-to-peer. Customers are partners, not buyers.

When you reach the proposal, I will reply ``APPROVED``. When the deck
is built and QA-passed, return the path.

Important: deck-builder MUST pass
``--template templates/corporate-2026.pptx`` when invoking
``generate_deck.py``.
```

## Assert
```yaml
files:
  exists:
    - ".story-telling-stm/runs/*/agents/deck-builder/deck-spec.json"
    - ".story-telling-stm/runs/*/agents/deck-builder/output.pptx"
contains:
  - { path: ".story-telling-stm/runs/*/agents/deck-builder/deck-spec.json", any: ["corporate-2026.pptx", "templates"] }
```
