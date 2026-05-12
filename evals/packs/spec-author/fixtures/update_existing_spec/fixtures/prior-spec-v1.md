# Workspace activity digest — Specification

## Document Information

- **Author(s)**: Notifications team
- **Created**: 2025-09-01
- **Last Updated**: 2025-09-01
- **Status**: Approved
- **Reviewers**: PM lead, EM lead
- **Version**: v1.0

---

## Problem Statement

Workspace members miss important changes across squads. Scrolling
individual channels to find what matters takes too long. PMs and
EMs surface this pain in NPS comments and qualitative interviews.

---

## Goals & Success Metrics

### User outcomes
- Reduce median time-to-first-action on a flagged change from
  45 minutes to under 10 minutes for >70% of digest recipients
  within 90 days post-launch.

### Business outcomes
- Lift weekly engagement among PM/EM cohorts by 8 points.

### Success metrics

| Metric | Baseline | Target | Window |
|--------|----------|--------|--------|
| Median time-to-first-action | 45 min | < 10 min for >70% | 90 days |
| PM/EM weekly engagement     | baseline | +8 pts            | 90 days |

---

## Users & Personas

| Persona | Primary needs | Expected outcome |
|---------|---------------|------------------|
| PM      | Daily summary across squads. | < 2 min to know what to follow up on. |
| EM      | Blockers and unclaimed work in their org. | Re-route quickly. |

---

## Solution Summary

A daily in-app notification at user-configurable time (default 9 AM
local) summarising changes in the workspace the user owns or
follows. Built on the existing `workspace-events` Kafka topic. No
new datastore.

---

## Functional Requirements

| ID    | Requirement | Priority |
|-------|-------------|----------|
| FR-01 | Deliver a daily digest notification at the user's configured time. | P0 |
| FR-02 | Allow users to opt in or out of the digest. | P0 |
| FR-03 | Allow users to configure the delivery time. | P0 |
| FR-04 | Allow users to filter the digest by workspace they own/follow. | P0 |
| FR-05 | Render up to 20 changes per digest, prioritised by recency and relevance. | P1 |
| FR-06 | Support a "snooze" action that suppresses the next digest only. | P1 |
| FR-07 | Mouse-only quick actions: clicking a change row opens it in the source surface. | P1 |

---

## Acceptance Criteria

| ID    | For   | Given / When / Then |
|-------|-------|---------------------|
| AC-01 | FR-01 | Given a user has the digest enabled, when their configured time is reached, then the digest is delivered within 5 minutes p95. |
| AC-02 | FR-02 | Given a user opts out, when the next configured delivery time is reached, then no digest is delivered. |
| AC-03 | FR-04 | Given a user follows N workspaces, when the digest is generated, then only changes from those workspaces appear. |

---

## Risks & Mitigations

| ID   | Risk | Mitigation |
|------|------|------------|
| R-01 | Notification fatigue. | Cap at one digest/day; allow snooze; clear opt-out. |

---

## Open Questions

| ID    | Question | Owner |
|-------|----------|-------|
| OQ-01 | What's the right cap on changes per digest? | PM |

---

## Out of Scope

- Email delivery (in-app only for v1).
- Per-channel granularity (workspace-level only for v1).
