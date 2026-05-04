# Hiring-plan options considered

Three shapes were modeled. The plan in ``hiring-plan.md`` is
Option 2.

## Option 1 — Aggressive (revenue-aligned)

- 22 net-new engineers + 3 SREs. Matches the 22% growth implied by
  the FY26 revenue plan.
- Cost: $5.9M FY26.
- **Why rejected:** Violates the absorb-and-train ratio in 3 of 4
  pods. Engineering leads explicitly opposed; the FY24 precedent
  for over-hiring (net-negative throughput in two pods) is recent
  and well-remembered.

## Option 2 — Constrained (recommended)

- 17 net-new engineers + 2 SREs, tranched as described in
  ``hiring-plan.md``. Conditional Q3 tranche tied to Streaming
  Ingest technical-risk gate.
- Cost: $4.6M FY26.
- **Why recommended:** Honours the absorb-and-train ratio.
  Discharges Streaming Ingest risk before staffing it. Backfills
  Activation pod attrition urgently.

## Option 3 — Defensive (flat)

- 8 net-new engineers + 1 SRE. Backfill-only posture.
- Cost: $2.2M FY26.
- **Why rejected:** Cannot staff Streaming Ingest at all under any
  scenario. Forces deferral of either the search-rewrite tail or
  the FY26 enterprise feature commitments. Leaves SRE ratio at
  1:48, well below the platform team's stated need.

## Decision shape

The trade-off is **constrained-and-conditional (Option 2)** vs
either revenue-shape-matching (Option 1) or capability-deferral
(Option 3). The CFO office has signalled comfort with any of the
three envelopes; the real constraint is engineering's
absorb-and-train ceiling.
