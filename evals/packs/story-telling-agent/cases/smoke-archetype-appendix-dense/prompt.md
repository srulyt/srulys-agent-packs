# Smoke — Appendix Dense

## Audience & Decision

Board pre-read for Q3 review. Audience: board of directors. The body deck (5-7 slides) ends with one Appendix Dense slide carrying methodology, cohort definition, raw data table, and caveats — high density is the point.

## Tone

Professional, data-led, decision-forcing.

## Approval gate

When you reach the proposal, I will reply `APPROVED`. When the deck
is built and QA-passed, return the path to `output.pptx`.

## Renderer expectation

This case verifies that the **Appendix Dense** archetype renders
correctly via the `appendix_dense` styled recipe (function `_styled_appendix_dense`)
introduced in session `2026-05-04-c8d3b2a1`. The strategist's
proposal should call out the archetype in the `Visual Treatment`
field for the relevant slide. The deck-builder should set
`style: "styled"` and `style_recipe: "appendix_dense"` on that slide and
populate the spec key(s): `panels[]` (2-4); pair with `appendix: true`.
