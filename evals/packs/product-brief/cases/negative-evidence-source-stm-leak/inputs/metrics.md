# Mavenport migration KPIs

| Metric | Current (Lattice-1) | Lattice-2 reference | FY26 target post-migration |
|---|---|---|---|
| P1 incidents per quarter (this subsystem) | 2.75 (avg trailing 4Q) | 0.4 (other Lattice-2 services) | ≤ 0.6 |
| Mean time to detect | 14 min | 3 min | ≤ 5 min |
| Mean time to recover | 71 min | 22 min | ≤ 30 min |
| On-call pages per week (subsystem) | 11.2 | 3.0 | ≤ 4.0 |
| Test coverage (line / branch) | 41% / 28% | 78% / 64% | ≥ 70% / ≥ 55% |
| Config sources of truth | 2 (file + DB) | 1 (declarative) | 1 |
| SOC 2 audit posture (this subsystem) | observation | clean | clean |

## Cost-of-doing-nothing modeling

If we defer to Q1 FY27 (Option 2) and the SOC 2 observation
escalates to a finding, the remediation budget shape becomes:

- ~$0.4M unplanned remediation work in FY26 to meet auditor
  expectations on Lattice-1 in place.
- Roughly 4 weeks of Engineer C's time consumed by remediation
  rather than migration prep, which delays Option 2 itself.

That risk is the strongest argument for the H2 FY26 timing in
``migration-proposal.md``.

## Out of scope for this brief

- Customer-facing billing UI (already on Lattice-2).
- Historical invoice archival migration (separate FY27 track).
- Multi-currency settlement (different roadmap, deferred either
  way).
