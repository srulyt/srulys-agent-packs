@spec-author create a new spec at `docs/specs/sla-dashboard.md` for
an internal SLA-tracking dashboard.

Background and what we want:

The on-call rotation is drowning. Engineers spend ~12 hours/week
chasing SLO breaches across five services, and we have no single
view of which SLOs are red right now. The platform team owns this;
Maya Chen (platform PM) and Devon Park (platform EM) will review.
We want to build a dashboard that shows current SLO state per
service, with drill-down to recent breach events. Success means
on-call gets to root cause in under 10 minutes p75 within one
quarter of launch. Roll out behind a flag to platform first, then
the rest of engineering two weeks later.

Please draft the spec.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop 0 (output location):** `output_path: docs/specs/sla-dashboard.md, spec_kind: technical`
- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
