# Channel Notifications — Specification

## Document Information

- **Author(s)**: Dana Levi
- **Created**: 2026-06-02
- **Last Updated**: 2026-07-14
- **Status: published**
- **Reviewers**: Omer Katz, Priya Natarajan
- **Version: 1.0.0**

---

## Problem Statement

Team members miss time-sensitive messages in busy channels. In the June 2026 survey (n=412), 58% of respondents said they learned about an urgent channel message more than an hour after it was posted. Notifications today are all-or-nothing per workspace, so users either mute everything or get interrupted by every message.

---

## Goals & Success Metrics

| Metric | Baseline | Target | Measurement window | Type |
|--------|----------|--------|--------------------|------|
| Users who see an @mention within 15 minutes | 42% | 70% | 60 days after GA | user |
| Workspace-wide mute adoption | 31% | 15% | 60 days after GA | user |

---

## Users & Personas

| Persona | Role / context | Primary job (JTBD) | Top pains | Expected outcome |
|---------|----------------|--------------------|-----------|------------------|
| Channel member | Belongs to 10–40 channels | When an urgent message mentions me, I want to know quickly, so I can respond before it blocks others | Noise from low-value channels | Sees urgent messages fast without constant interruption |

---

## Solution Summary

Add per-channel notification levels (All, Mentions, None) and deliver push notifications according to each channel's level. A daily email digest summarises unread mentions.

---

## Functional Requirements

### FR-01 — Per-channel notification level  *(P0, optional-feature)*

Where a user is a member of a channel, the notification service shall let the user set that channel's notification level to All, Mentions, or None.

#### Acceptance Criteria

- **AC-01.1** — Given a user in channel #ops, when they set the level to Mentions, then only messages that @mention them trigger a push notification from #ops.

---

### FR-02 — Daily email digest  *(P1, event-driven)*

When 08:00 in the user's time zone is reached, the notification service shall email the user a digest of unread @mentions from the previous 24 hours.

#### Acceptance Criteria

- **AC-02.1** — Given a user with 3 unread mentions, when 08:00 local time is reached, then one email listing the 3 mentions is sent.

---

### FR-03 — Push delivery  *(P0, event-driven)*

When a message matches a channel's notification level for a user, the notification service shall send that user a push notification within 10 seconds.

#### Acceptance Criteria

- **AC-03.1** — Given level All on #ops, when a message is posted in #ops, then the user's device receives a push within 10 s p95.

---

### FR-04 — Push provider failure  *(P0, unwanted-behaviour)*

If the push provider rejects or times out on a delivery, then the notification service shall retry with exponential backoff for up to 5 minutes and record the final outcome.

#### Acceptance Criteria

- **AC-04.1** — Given the push provider returns HTTP 503, when a notification is sent, then it is retried and the final status is logged as delivered or failed.

---

## Risks & Mitigations

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|------------|--------|------------|
| R-01 | Users set everything to None and miss urgent messages | Medium | High | Default new channels to Mentions |

---

## Open Questions

- **OQ-01** — Should workspace admins be able to enforce a minimum level on announcement channels? *Owner:* Dana Levi. *Due:* 2026-09-01.

---

## Out of Scope

- Desktop notification sounds per channel.
