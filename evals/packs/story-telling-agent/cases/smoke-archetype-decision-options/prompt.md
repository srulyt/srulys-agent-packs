# Smoke — Decision Options Table

## Audience & Decision

Vendor selection for production data warehouse. Audience: CTO + data platform team. Decision needed: pick a vendor. Compare 4 vendors (Acme, Globex, Initech, Umbra) across criteria (Cost, Latency, Support, SOC2 compliance). Recommend Acme.

## Tone

Professional, data-led, decision-forcing.

## Approval gate

When you reach the proposal, I will reply `APPROVED`. When the deck
is built and QA-passed, return the path to `output.pptx`.

## Renderer expectation

This case verifies that the **Decision Options Table** archetype renders
correctly via the `decision_options` styled recipe (function `_styled_decision_options`)
introduced in session `2026-05-04-c8d3b2a1`. The strategist's
proposal should call out the archetype in the `Visual Treatment`
field for the relevant slide. The deck-builder should set
`style: "styled"` and `style_recipe: "decision_options"` on that slide and
populate the spec key(s): `options[]`, `criteria[]`, `recommendation`.
