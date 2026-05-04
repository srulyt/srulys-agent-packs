# Smoke — Risk Heatmap

## Audience & Decision

Quarterly enterprise-risk register for the COO. Audience: COO + risk committee. Decision needed: which 3 risks get owners + mitigation funding this quarter. Risks to plot (5 total): vendor SLA failure (high/high), spec drift (high/med), hiring slip (low/low), data-loss event (low/high), tooling outage (med/med).

## Tone

Professional, data-led, decision-forcing.

## Approval gate

When you reach the proposal, I will reply `APPROVED`. When the deck
is built and QA-passed, return the path to `output.pptx`.

## Renderer expectation

This case verifies that the **Risk Heatmap** archetype renders
correctly via the `risk_heatmap` styled recipe (function `_styled_risk_heatmap`)
introduced in session `2026-05-04-c8d3b2a1`. The strategist's
proposal should call out the archetype in the `Visual Treatment`
field for the relevant slide. The deck-builder should set
`style: "styled"` and `style_recipe: "risk_heatmap"` on that slide and
populate the spec key(s): `risks[]`, `axes`.
