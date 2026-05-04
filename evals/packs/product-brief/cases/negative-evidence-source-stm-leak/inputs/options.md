# Migration options considered

## Option 1 — H2 FY26, full migration with bought tooling (recommended)

- Timing: kick off Q3 FY26, GA on Lattice-2 by end Q4 FY26.
- Tooling: buy the third-party schema-diff tool ($0.15M). Saves an
  estimated 6 weeks of internal build.
- Cost envelope: $2.1M fully loaded.
- Pros: closes the FY26 SOC 2 risk before the audit window.
  Discharges the knowledge-concentration risk while Engineer C is
  still on the team. Smallest cumulative on-call cost over the next
  18 months.
- Cons: takes 9 months of a 4-engineer team plus partial SRE.
  Forces deferral of one Lattice-2 feature initiative (the leading
  candidate is the multi-currency settlement track; see scope-out
  in ``migration-proposal.md``).

## Option 2 — Q1 FY27, full migration with internal tooling

- Timing: kick off Q1 FY27, GA by end Q3 FY27.
- Tooling: build internal schema-diff (≈ 6 weeks). No external
  spend.
- Cost envelope: $2.0M fully loaded (saves $0.15M tooling, costs
  $0.10M internal build, plus the on-call cost of running another
  4 quarters on Lattice-1).
- Pros: protects FY26 feature roadmap. Spreads cost into FY27.
- Cons: SOC 2 observation likely becomes a finding in FY26.
  Engineer C departure risk extends another year. Cumulative
  on-call cost is meaningfully higher.

## Option 3 — Strangler pattern, 18-month rolling migration

- Timing: kick off Q3 FY26, GA in tranches through end FY27.
- Cost envelope: $2.6M fully loaded (longer duration, more
  context-switching overhead).
- Pros: each subsystem ships independently; lower per-cutover risk.
- Cons: the billing-eventbus cannot be cleanly stranglered (it is
  the substrate the others share). Compliance window is missed.
  Highest total cost.

## Decision shape

The trade-off is **time-to-relief (Option 1)** vs. **roadmap
preservation (Option 2)** vs. **per-cutover risk reduction
(Option 3)**. The recommendation is Option 1.
