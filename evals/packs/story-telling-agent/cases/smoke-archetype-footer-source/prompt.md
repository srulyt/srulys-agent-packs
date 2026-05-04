# Smoke — Footer Source

## Audience & Decision

Confidential Series-B pitch with cited research. Audience: VC partners. Every chart slide cites its source; every slide carries a 'Confidential' marker; every slide has a 'page N / total' footer. Use a regular content / data-callout slide and overlay the footer.

## Tone

Professional, data-led, decision-forcing.

## Approval gate

When you reach the proposal, I will reply `APPROVED`. When the deck
is built and QA-passed, return the path to `output.pptx`.

## Renderer expectation

This case verifies that the **Footer Source** archetype renders
correctly via the `footer_source` styled recipe (function `_apply_footer_source (partial)`)
introduced in session `2026-05-04-c8d3b2a1`. The strategist's
proposal should call out the archetype in the `Visual Treatment`
field for the relevant slide. The deck-builder should set
`style: "styled"` and `style_recipe: "footer_source"` on that slide and
populate the spec key(s): `slide.footer.{source,page,page_total,confidentiality}`.
