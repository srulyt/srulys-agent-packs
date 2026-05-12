# Beacontide engineering org context — FY25 ending state

## Headcount snapshot (end of FY25)

- Total engineering: 136 (124 IC + 12 EM/director).
- By group:
  - Platform: 28 IC, 3 EM
  - Pipeline pod: 12 IC, 1 EM
  - Forecasting pod: 11 IC, 1 EM
  - Activation pod: 14 IC, 1 EM
  - Cross-cutting (security, data-platform, infra-shared): 19 IC,
    2 EM
  - SREs: 4 (centralised under Platform)
- FY25 attrition: 11.4% (engineering-wide), concentrated in the
  Activation pod (4 of 14 IC).

## Capacity reality

- Platform group is currently absorbing the search-rewrite tail and
  the workspace-permissions cleanup. Both are committed FY26 work.
- Activation pod is below committed capacity due to attrition;
  backfill is urgent regardless of FY26 plan shape.
- Forecasting pod has a known shared dependency on data-platform
  for any FY26 enterprise feature work.

## Compensation envelope

- FY26 fully-loaded cost per engineer: $245K average (band-weighted).
- Staff-level fully-loaded cost: $340K average.
- SRE fully-loaded cost: $260K average.

## Recruiting constraints

- Time-to-hire (offer accepted): currently 78 days p50 for IC, 110
  days p50 for staff. Plan assumes no improvement, conservatively.
- Streaming Ingest pod hires are dependent on a successful Q2
  technical-risk gate; recruiting can warm pipelines but will not
  open conditional reqs until the gate clears.

## Cultural context (relevant to absorb-and-train)

- FY25 engineering retro flagged onboarding load as the second-most
  cited capacity drain after on-call (2024 retro cited it as fifth).
- Engineering managers escalated in Q3 that "more hires faster" had
  net-negative throughput in two pods last cycle. The
  absorb-and-train ratio in ``hiring-plan.md`` is the explicit
  response to that escalation.
