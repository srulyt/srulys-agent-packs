# Smoke — Waterfall / Value Bridge

## Audience & Decision

FY26 revenue-bridge for the CFO. Audience: CFO + FP&A. Decision needed: approve the FY26 plan. Decompose FY25 revenue ($10M) -> FY26 plan ($14M) into 3-4 contributing components: pricing increase (+$2M), Q2 churn (-$1M), new logos (+$3M). Show the running total.

## Tone

Professional, data-led, decision-forcing.

## Approval gate

When you reach the proposal, I will reply `APPROVED`. When the deck
is built and QA-passed, return the path to `output.pptx`.

## Renderer expectation

This case verifies that the **Waterfall / Value Bridge** archetype renders
correctly via the `waterfall` styled recipe (function `_styled_waterfall`)
introduced in session `2026-05-04-c8d3b2a1`. The strategist's
proposal should call out the archetype in the `Visual Treatment`
field for the relevant slide. The deck-builder should set
`style: "styled"` and `style_recipe: "waterfall"` on that slide and
populate the spec key(s): `waterfall.{start,steps[],end,units}`.
