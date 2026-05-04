# Smoke — 2x2 / Priority Matrix

## Audience & Decision

Engineering backlog triage. Audience: VP Eng + product. Decision needed: which initiatives to staff in H1. Plot 4-6 candidate initiatives on effort (low/high) x value (low/high). Items: SSO migration (high effort/high value), tooltip polish (low/low), reporting v2 (high/high), error-page redesign (low/high). Mark the chosen 'quick wins' quadrant.

## Tone

Professional, data-led, decision-forcing.

## Approval gate

When you reach the proposal, I will reply `APPROVED`. When the deck
is built and QA-passed, return the path to `output.pptx`.

## Renderer expectation

This case verifies that the **2x2 / Priority Matrix** archetype renders
correctly via the `priority_matrix` styled recipe (function `_styled_priority_matrix`)
introduced in session `2026-05-04-c8d3b2a1`. The strategist's
proposal should call out the archetype in the `Visual Treatment`
field for the relevant slide. The deck-builder should set
`style: "styled"` and `style_recipe: "priority_matrix"` on that slide and
populate the spec key(s): `matrix_items[]`, `axes`, `quadrant_labels[4]`.
