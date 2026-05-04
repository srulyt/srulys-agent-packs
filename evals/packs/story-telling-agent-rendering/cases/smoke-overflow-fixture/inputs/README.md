# Inputs

This case stages a pre-built `deck-spec.json` + `generate_deck.py`
fixture under `.story-telling-stm/runs/smoke-overflow/agents/deck-builder/`
(via the `fixtures/` copy step in `case.yaml`).

The fixture contains slide 3 with a 50-word body in a 4-inch wide
textbox at body_size=22pt — guaranteed to overflow under the
rebuilt `check_pptx.py` real-metric pipeline.
