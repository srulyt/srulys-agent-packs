# Lattice-1 current-state assessment

## What runs on Lattice-1 today

| Service | Function | Traffic share | Last refactor |
|---|---|---|---|
| invoicing-svc | Invoice generation, line-item assembly | 18% | FY21 |
| revrec-svc | Revenue recognition, ASC 606 schedules | 6% | FY22 |
| billing-eventbus | Internal pub/sub for billing events | 4% | FY20 |
| webhook-gw-legacy | Outbound webhooks to customer endpoints | 2% | FY21 |

Total: ~30% of platform traffic by request volume; ~55% of
platform traffic by revenue-impacting request volume (because
billing requests are heavily weighted).

## Operational profile

- **Incident contribution:** 11 of the last 18 P1 incidents
  (FY25 trailing 12 months) trace to a Lattice-1 component.
- **Mean time to detect (Lattice-1 services):** 14 minutes.
  Lattice-2 services average 3 minutes (better instrumentation).
- **Mean time to recover (Lattice-1 services):** 71 minutes.
  Lattice-2 services average 22 minutes.
- **On-call load:** Lattice-1 generates roughly 3.4x the page
  volume per traffic unit compared with Lattice-2.

## Technical debt summary

- Configuration is partially file-based and partially database-
  shaped, with no single source of truth. This is the audit
  observation.
- Test coverage on revrec-svc is 41% line, 28% branch. Lattice-2
  services average 78% line, 64% branch.
- The billing-eventbus has no replay capability; recovery from
  bad-publish events requires manual database surgery.
- The webhook-gw-legacy uses a deprecated outbound-retry library
  with two CVEs in the last year (both patched, but the upstream
  is unmaintained).

## Knowledge map

Three engineers historically held deep Lattice-1 expertise:

- Engineer A: departed FY24-Q4.
- Engineer B: departed FY25-Q2.
- Engineer C: still on team. Proposed migration tech lead.

There is no fourth engineer with comparable depth. Pair-up plans
during the migration include training two Lattice-2-strong
engineers into Lattice-1 read-fluency for the duration.
