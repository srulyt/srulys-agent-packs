---
name: context-pack-builder-smoke-new-context-pack
target: cpb-orchestrator
kind: agent
tags: [pack, slow, judge]
timeout: 2100
---

# New checkout context pack includes expected artifacts and content

## Description
Happy-path smoke: a NEW context pack is produced from a small seed.

Seeds a tiny fixture feature into the workspace, runs the orchestrator, and asserts a uniform pack dir with plugin.json, context-pack.json, and a skills/<slug>-context/SKILL.md carrying the five content areas + confidence. A judge then checks the content actually maps the seeded feature.

## Act
```prompt
Build a context pack for the "checkout" feature in this repository.
BOUNDED MODE (fast pass): keep this run cost-capped and single-pass.

Scope — confine discovery/analysis to EXACTLY these seed paths; do NOT
scan the rest of the repository:
  - src/checkout/routes.py    (entry point: POST /checkout route)
  - src/checkout/service.py   (business: CheckoutService.place_order)
  - src/checkout/models.py    (data: the Order row)
  - tests/test_checkout.py    (tests)
  - docs/checkout.md          (docs)

The feature is the order checkout flow: a POST /checkout route calls
CheckoutService.place_order, which validates the cart and writes an Order
row. Produce the pack in context-packs/ and run the full pipeline to
completion (all five content areas with confidence scores).
```

## Assert
```yaml
files:
  exists:
    - "context-packs/*-context/plugin.json"
    - "context-packs/*-context/context-pack.json"
    - "context-packs/*-context/skills/*-context/SKILL.md"
judge:
  artifact: "context-packs/*-context/skills/*-context/SKILL.md"
  threshold: 0.7
  criteria: |
    Score 1.0 only if this is a context-pack SKILL.md for a 'checkout' feature that covers ALL FIVE content areas (entry points; file & folder locations per layer; glossary; patterns & practices; architecture & design), shows a per-area confidence score (1-5) for each, and accurately reflects the seeded feature (a POST /checkout route calling CheckoutService.place_order that writes an Order). Score 0.5 if some areas or confidence scores are missing. Score 0.0 if it is not a coherent checkout context pack. Be strict.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better,
      baseline: rolling_mean, tolerance: 0.1 }
```
