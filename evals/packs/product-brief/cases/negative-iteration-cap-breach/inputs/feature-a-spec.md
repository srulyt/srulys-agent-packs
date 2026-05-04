# Feature A — Pipeline canvas (spec excerpt)

**Product:** Polariq (mid-market CRM for technical-services firms)
**Owner:** N. Hoffmann, PM, Pipeline pod
**Status:** Greenlit for spec; awaiting prioritisation against
Feature B

## What it is

A visual pipeline-canvas surface that replaces the current list-only
deal view. Users drag deal cards across stage columns; stage
transitions trigger the existing automation rules unchanged.

## Why this, why now

- 41% of mid-market trial accounts in FY25 cited "no visual
  pipeline" as a reason for choosing a competitor at the bake-off
  stage (post-trial survey, n=148).
- The deal-card data model already supports the required attributes;
  no schema migration is required.
- Sales engineering says they currently demo a hand-drawn
  whiteboard during prospect calls because the product cannot show
  the canvas they describe.

## Build envelope

- 4 months, Pipeline pod (3 engineers, 1 designer, 1 PM).
- No new infra; reuses existing automations service.
- Risk: drag-and-drop performance on accounts with >2,000 open
  deals. Mitigation: virtualised rendering, tested in spike.

## Expected impact

- Trial-to-paid conversion: +3 to +5 percentage points on mid-market
  cohort (modeled from competitor-cited losses).
- No expected impact on enterprise cohort.
