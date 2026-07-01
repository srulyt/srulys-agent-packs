---
name: story-telling-agent-archetype-recipes
target: story-orchestrator
kind: agent
tags: [pack, slow]
timeout: 1800
---

# Archetype recipes

## Description
Smoke coverage for the 8 styled archetype recipes added in session `2026-05-04-c8d3b2a1`. Each parametrised case asks `@story-orchestrator` to build a deck featuring one specific archetype, then asserts that the resulting `deck-spec.json` actually selects that `style_recipe` and that the deck/QA artefacts exist.

Ported from legacy `cases/smoke-archetype-*/`. The 8 archetypes: `funnel`, `waterfall`, `risk_heatmap`, `flywheel`, `priority_matrix`, `decision_options`, `footer_source`, `appendix_dense`.

## Act
```prompt
@story-orchestrator

Build a single smoke-test deck that exercises all 8 styled archetype
recipes from the legacy parametrised cases. The deck must include slides
that use these exact style recipes in `deck-spec.json`:

- `funnel`: Q3 sales-pipeline review for CRO + sales ops, with stages
  Leads (1000) -> MQL (400) -> SQL (120) -> Closed Won (30) and the
  Leads->MQL leak called out.
- `waterfall`: FY26 revenue bridge for the CFO, decomposing FY25
  revenue ($10M) -> FY26 plan ($14M) with pricing increase (+$2M),
  Q2 churn (-$1M), and new logos (+$3M).
- `risk_heatmap`: quarterly enterprise-risk register for the COO with
  risks including vendor SLA failure, spec drift, hiring slip,
  data-loss event, and tooling outage.
- `flywheel`: growth-loop pitch for Series-B prospects with stages
  more users -> more data -> better recommendations -> more users
  return and centre label 'Compounding network effect'.
- `priority_matrix`: engineering backlog triage for VP Eng + product,
  plotting initiatives including SSO migration, tooltip polish,
  reporting v2, and error-page redesign.
- `decision_options`: production data warehouse vendor selection
  comparing Acme, Globex, Initech, and Umbra across Cost, Latency,
  Support, and SOC2 compliance; recommend Acme.
- `footer_source`: confidential Series-B pitch treatment where at
  least one regular content or data-callout slide has a non-null
  footer block with source/page/confidentiality.
- `appendix_dense`: board pre-read for Q3 review ending with one dense
  appendix slide carrying methodology, cohort definition, raw data
  table, and caveats.

Use `style: "styled"` where applicable and set each `style_recipe`
exactly as listed above. This is a non-interactive run: when you reach
the Stop-B proposal gate, treat it as approved and continue building
end-to-end (proposal -> approval -> build -> QA) without pausing for
additional input. When the deck is built and QA-passed, return the path
to `output.pptx`.
```

## Assert
```yaml
files:
  exists:
    - ".story-telling-stm/runs/*/agents/deck-builder/deck-spec.json"
    - ".story-telling-stm/runs/*/agents/deck-builder/output.pptx"
    - ".story-telling-stm/runs/*/agents/deck-critic/qa-report.json"
contains:
  - path: ".story-telling-stm/runs/*/agents/deck-builder/deck-spec.json"
    all:
      - "funnel"
      - "waterfall"
      - "risk_heatmap"
      - "flywheel"
      - "priority_matrix"
      - "decision_options"
      - "footer_source"
      - "appendix_dense"
```
