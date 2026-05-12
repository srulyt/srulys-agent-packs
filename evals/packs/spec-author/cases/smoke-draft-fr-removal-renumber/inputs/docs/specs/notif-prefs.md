# Notification Preferences

## Document Information

- **Author(s)**: Spec Author Pack
- **Created**: 2026-04-15
- **Last Updated**: 2026-05-10
- **Status**: draft
- **Reviewers**: Pending assignment
- **Version**: 0.0.3-draft

---

## Problem Statement

Users cannot configure notification behaviour beyond a single
on/off toggle. Power users repeatedly request per-channel and
per-quiet-hour controls (38 forum threads in Q1 2026).

---

## Goals & Success Metrics

- Cut "notifications too noisy" support tickets by 60% within one
  quarter of launch.

---

## Users & Personas

- **Power user** — wants fine-grained control over which channels
  ping them and when.

---

## Solution Summary

A Notifications tab in Settings with per-channel toggles, a global
quiet-hours window, and a "test notification" button.

---

## Functional Requirements

### FR-01 — Per-channel toggle list (P0, ubiquitous)

The system shall display a list of all notification channels with
an on/off toggle per channel.

#### Acceptance Criteria

- **AC-01.1**: Given the user opens Settings → Notifications, When
  the page renders, Then every channel the user is subscribed to
  appears with its current toggle state.

### FR-02 — Persist toggle state (P0, event-driven)

When the user flips a per-channel toggle (per FR-01), the system
shall persist the new value within 200 ms p95.

#### Acceptance Criteria

- **AC-02.1**: Given a user flips a toggle (see FR-01), When the
  flip lands, Then the new state is reflected on next page load.

### FR-03 — Inline preview of muted channels (P2, ubiquitous)

The system shall show a small "muted" badge next to each channel
in the main app whenever its FR-01 toggle is off.

#### Acceptance Criteria

- **AC-03.1**: Given a channel toggle is off (see FR-01), When the
  user views the channel list in the main app, Then the muted
  badge is visible.

### FR-04 — Quiet-hours window (P1, state-driven)

While the current time is within the user's configured quiet-hours
window, the system shall suppress all notifications regardless of
per-channel toggle state.

#### Acceptance Criteria

- **AC-04.1**: Given quiet hours are 22:00–07:00, When a notification
  fires at 23:00, Then it is suppressed.
- **AC-04.2**: Given quiet hours end at 07:00, When a notification
  fires at 07:01, Then it is delivered.

### FR-05 — Test-notification button (P2, event-driven)

When the user clicks the "Send test notification" button, the system
shall deliver a test notification through the per-channel and
quiet-hours pipeline (see FR-01, FR-04).

#### Acceptance Criteria

- **AC-05.1**: Given the user clicks the test button, When the test
  fires, Then the user receives a notification respecting current
  FR-01 and FR-04 settings.

---

## Risks & Mitigations

| ID   | Risk | Mitigation |
|------|------|------------|
| R-01 | Quiet-hours window misconfigured across timezones (FR-04). | Show resolved local-time window in UI. |
| R-02 | Test button abused (FR-05). | Rate-limit to 3/min. |

---

## Open Questions

- **OQ-01**: Should the muted badge in FR-03 also surface in the
  mobile app, or web only for v1?
