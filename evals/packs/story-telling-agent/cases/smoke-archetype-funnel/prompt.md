# Smoke — Funnel

## Audience & Decision

Q3 sales-pipeline review. Audience: CRO + sales ops. Decision needed: where to invest in conversion. Stages (4): Leads (1000) -> MQL (400) -> SQL (120) -> Closed Won (30). The largest leak (Leads->MQL, 60% drop) gets called out.

## Tone

Professional, data-led, decision-forcing.

## Approval gate

When you reach the proposal, I will reply `APPROVED`. When the deck
is built and QA-passed, return the path to `output.pptx`.

## Renderer expectation

This case verifies that the **Funnel** archetype renders
correctly via the `funnel` styled recipe (function `_styled_funnel`)
introduced in session `2026-05-04-c8d3b2a1`. The strategist's
proposal should call out the archetype in the `Visual Treatment`
field for the relevant slide. The deck-builder should set
`style: "styled"` and `style_recipe: "funnel"` on that slide and
populate the spec key(s): `funnel_stages[]` (3-6, with optional `rate`).
