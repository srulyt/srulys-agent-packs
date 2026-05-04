# Feature B — Forecast-as-of (spec excerpt)

**Product:** Polariq
**Owner:** S. Vargas, PM, Forecasting pod
**Status:** Greenlit for spec; awaiting prioritisation against
Feature A

## What it is

A "forecast-as-of" capability that lets sales leaders ask "what did
the forecast look like on date X" and get a reproducible snapshot,
including the deal-level state that produced the rolled-up number.
Currently forecasts are non-reproducible after the fact.

## Why this, why now

- Two of our top-ten accounts (both publicly traded) have flagged
  forecast non-reproducibility as a compliance concern in their
  most recent QBR. One has explicitly tied renewal to it.
- Internal sales-ops research (n=23 customers) found that 19 of 23
  manually screenshot the forecast each week to work around this
  gap. That is a strong adoption signal but a fragile workaround.
- The audit-log refactor shipped in FY25-Q3 is the structural
  prerequisite. It is now in place.

## Build envelope

- 5 months, Forecasting pod (3 engineers, 1 designer, 1 PM) plus
  shared dependency on the data-platform team for the snapshot
  store (estimated 4 weeks of their time).
- Risk: storage cost growth if snapshot retention is unbounded.
  Mitigation: 13-month rolling retention, configurable per tenant.

## Expected impact

- Enterprise renewal risk reduction: removes a named blocker on at
  least one publicly-traded renewal.
- Net-new enterprise: cited in 6 of the last 11 enterprise RFPs as
  a "must-have" or "scored requirement". Today we score 0 on it.
- No expected impact on SMB or mid-market cohort.
