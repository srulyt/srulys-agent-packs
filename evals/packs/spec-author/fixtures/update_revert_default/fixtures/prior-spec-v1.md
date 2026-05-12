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

Workspace memebers miss important changes accross squads, and the
scrolling of individual channels in order to be finding what matters
is taking too much of the time. PMs and EMs surface this pain in NPS
comments and qualitative interviews.

---

## Goals & Success Metrics

- Reduce median time-to-first-action on a flagged change from
  45 minutes to under 10 minutes for >70% of digest recipients
  within 90 days post-launch.

---

## Users & Personas

| Persona | Primary needs | Expected outcome |
|---------|---------------|------------------|
| PM      | Daily summary across squads. | < 2 min to know what to follow up on. |
| EM      | Blockers & unclaimed work in their org. | Re-route quickly. |

---

## Solution Summary

A daily in-app notification at user-configurable time (default 9 AM
local) summarising changes in the workspace the user owns or
follows. Built on the existing `workspace-events` Kafka topic. No new datastore.

---

## Functional Requirements

| ID    | Requirement | Priority |
|-------|-------------|----------|
| FR-01 | Deliver a daily digest notification at the user's configured time. | P0 |
| FR-02 | Allow users to opt in or out of the digest. | P0 |
| FR-03 | Allow users to configure the delivery time. | P0 |

---

## Acceptance Criteria

| ID    | For   | Given / When / Then |
|-------|-------|---------------------|
| AC-01 | FR-01 | Given a user has the digest enabled, when their configured time is reached, then the digest is delivered within 5 minutes p95. |
| AC-02 | FR-02 | Given a user opts out, when the next configured delivery time is reached, then no digest is delivered. |
