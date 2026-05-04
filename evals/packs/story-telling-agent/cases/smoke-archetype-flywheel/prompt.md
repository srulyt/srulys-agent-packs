# Smoke — Flywheel

## Audience & Decision

Growth-loop pitch for new investors. Audience: Series-B prospects. Decision needed: investor confidence in the compounding mechanism. Stages (4): more users -> more data -> better recommendations -> more users return. Centre label: 'Compounding network effect'.

## Tone

Professional, data-led, decision-forcing.

## Approval gate

When you reach the proposal, I will reply `APPROVED`. When the deck
is built and QA-passed, return the path to `output.pptx`.

## Renderer expectation

This case verifies that the **Flywheel** archetype renders
correctly via the `flywheel` styled recipe (function `_styled_flywheel`)
introduced in session `2026-05-04-c8d3b2a1`. The strategist's
proposal should call out the archetype in the `Visual Treatment`
field for the relevant slide. The deck-builder should set
`style: "styled"` and `style_recipe: "flywheel"` on that slide and
populate the spec key(s): `flywheel_stages[]` (3-6), `center_label`.
