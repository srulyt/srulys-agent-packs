---
name: spec-author-upper-section-isolation
target: spec-author
kind: agent
tags: [smoke, slow, pack]
timeout: 900
---

# Upper sections avoid cross-section leakage

## Description
F1 per-section isolation contract for upper sections: the prompt deliberately mixes problem-narrative, solution direction, ownership, and rollout in one paragraph. The drafter must split them into the correct upper sections; cross-section leakage MUST NOT occur: Solution Summary must not contain problem-narrative phrases or owner names; Problem Statement must not preempt the solution or name owners; Goals must not name owners or describe rollout.

Ported from legacy `cases/smoke-upper-section-isolation/`.

## Act
```prompt
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
```

## Assert
```yaml
files:
  exists:
    - docs/specs/sla-dashboard.md
section_not_contains:
  - { path: "docs/specs/sla-dashboard.md", section: "Solution Summary",
      any: ["drowning", "12 hours/week", "no single view"] }
  - { path: "docs/specs/sla-dashboard.md", section: "Solution Summary",
      any: ["Maya", "Devon", "platform PM", "platform EM"] }
  - { path: "docs/specs/sla-dashboard.md", section: "Problem Statement",
      any: ["dashboard", "drill-down"], ignore_case: true }
  - { path: "docs/specs/sla-dashboard.md", section: "Problem Statement",
      any: ["Maya", "Devon"] }
  - { path: "docs/specs/sla-dashboard.md", section: "Goals & Success Metrics",
      any: ["Maya", "Devon", "platform PM", "platform EM"] }
  - { path: "docs/specs/sla-dashboard.md", section: "Goals & Success Metrics",
      any: ["behind a flag", "two weeks later"], ignore_case: true }
```
