# Mavenport billing platform — H2 FY26 migration proposal

**Owner:** F. Achterberg, Staff Eng, Billing Platform
**Audience for the brief:** VP Engineering
**Decision shape:** approve / reject funding for the H2 FY26
migration project

## Summary

We propose funding a **9-month migration** of Mavenport's invoicing
and revenue-recognition subsystem off the legacy "Lattice-1" stack
onto our current "Lattice-2" platform. The headline cost envelope
is **$2.1M fully loaded** (engineering, partial SRE, partial
data-platform). The headline benefit is the retirement of the
single largest source of P1 incidents in the last four quarters.

The Lattice-1 stack predates the FY22 platform consolidation. It is
the only subsystem still on Lattice-1. Every other subsystem was
migrated by FY24-Q2.

## Why now

Three pressures converged:

1. **Incident concentration.** Lattice-1 has produced 11 of the
   last 18 P1 incidents (FY25 trailing 12 months), despite serving
   roughly 30% of platform traffic by request volume.
2. **Compliance gating.** Our SOC 2 Type II auditor flagged
   Lattice-1's configuration-drift posture in the FY25 audit. It is
   an observation, not a finding, this cycle. The auditor has
   indicated it will become a finding in FY26 if unchanged.
3. **Knowledge concentration.** Two of the three engineers with
   deep Lattice-1 expertise have departed in the last 18 months.
   The remaining one is the migration's proposed tech lead and is
   already over-indexed.

## Cost shape

- Engineering: 4 engineers × 9 months fully loaded ≈ $1.45M
- SRE partial allocation: ≈ $0.30M
- Data-platform dependency: ≈ $0.20M
- Migration-tooling buy: ≈ $0.15M (third-party schema-diff tool;
  alternative is a 6-week internal build, see ``options.md``)

## Scope

In: invoicing service, revenue-recognition service, the shared
billing event-bus, the legacy webhook gateway.

Out: the customer-facing billing UI (already on Lattice-2),
historical invoice archival storage (separate FY27 track),
multi-currency settlement (depends on a different roadmap).

## What approval unlocks

- Recruiting backfill for the departed Lattice-1 engineers as
  Lattice-2 hires (broader hiring pool).
- Sequenced retirement of Lattice-1 by end FY26.
- Removes the FY26 SOC 2 finding risk before the audit window.

## What we need from this review

A clear approve / reject on the $2.1M envelope and an explicit
endorsement of the H2 FY26 timing (vs. the Q1 FY27 alternative
described in ``options.md``).
