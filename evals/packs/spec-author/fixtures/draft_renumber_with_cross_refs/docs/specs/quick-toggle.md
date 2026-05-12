# Quick Toggle

## Document Information

- **Author(s)**: Spec Author Pack
- **Created**: 2026-05-01
- **Last Updated**: 2026-05-04
- **Status**: draft
- **Reviewers**: Pending assignment
- **Version**: 0.0.1-draft

---

## Problem Statement

Users repeatedly open Settings just to flip notifications on or off
during meetings or focused work. The setting is buried two levels
deep, and 38% of weekly visits to Settings are this single toggle
(internal usage telemetry, Q1 2026).

---

## Goals & Success Metrics

- Reduce time-to-toggle from ~14 s to under 2 s.
- Cut Settings page load volume attributable to notification toggling
  by 80% within one quarter.

---

## Users & Personas

- **Focused worker** — wants to silence notifications for a
  one-hour stretch with one click.
- **Meeting host** — wants to silence them at meeting start without
  context-switching.

---

## Solution Summary

Add a top-bar toggle pill that mirrors the current notifications
setting. Clicking flips the setting and shows a 1-second toast.

---

## Functional Requirements

### FR-1 — Top-bar visibility (P0, ubiquitous)

The system shall display a notification-toggle pill in the top bar
on every authenticated page.

#### Acceptance Criteria

- **AC-1.1**: Given an authenticated user, When any application
  page renders, Then the pill is visible in the top bar.
- **AC-1.2**: Given the user toggles notifications via Settings,
  When the user returns to any page, Then the pill state matches
  the new Settings value (see FR-2).

### FR-2 — Click-to-toggle (P0, event-driven)

When the user clicks the pill, the system shall flip the
notifications-enabled flag and persist the new value to the
user's profile.

#### Acceptance Criteria

- **AC-2.1**: Given the pill shows "On", When the user clicks the
  pill, Then notifications are disabled (see FR-3 for the visual
  feedback that confirms the flip).
- **AC-2.2**: Given the user clicks twice within 500 ms, When the
  second click fires, Then the second flip is debounced (single
  net change).

### FR-3 — Visual feedback (P1, event-driven)

When the toggle flips, the system shall display a 1-second toast
confirming the new state.

#### Acceptance Criteria

- **AC-3.1**: Given a pill click landed (see FR-2), When the
  toggle persists, Then a toast reading "Notifications on" or
  "Notifications off" appears for 1 s.

---

## Risks & Mitigations

| ID | Risk | Mitigation |
|----|------|------------|
| R-1 | Users mis-click during scroll | Debounce per FR-2 / AC-2.2 |
| R-2 | Toast obscures content | Position toast in the corner |

---

## Open Questions

- **OQ-1**: Should the toast appear on every flip, or only when the
  flip changes the state? (See FR-3 / AC-3.1.)

---

## Out of Scope

- Per-channel notification preferences (email vs. in-app).
- Mobile app top-bar parity.
