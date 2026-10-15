# Customer Research Summary — Onboarding Friction

**Compiled by:** Research Ops (Mara Holmgren)
**Window:** Last two quarters
**Methods:** 32 customer interviews, 4 unmoderated usability tests
(n=24), trial telemetry review, ticket-tag analysis on 1,840 tier-1
support tickets, two NPS waves.

## Population

- 32 interviews: 14 SMB (under 50 seats), 13 mid-market (50–500
  seats), 5 lower-enterprise (500–1,500 seats).
- Roles: 11 admins / IT, 13 finance leads, 8 analysts.
- Mix of trials that converted, trials that did not, and paying
  accounts that churned within 90 days.

## Top findings

### 1. Role mismatch in the first session

The current onboarding assumes the first user is an analyst. In 71%
of mid-market trials the first user is actually an admin or an IT
operator setting up SSO and data sources. They are blocked on tasks
the checklist does not surface (workspace permissions, data-source
auth, audit-log configuration), and the dashboard-creation task that
the checklist pushes them toward is not theirs to do.

Quote (mid-market admin): "I spent the first day setting up access
and the product kept telling me to build a dashboard. I'm not the
person who builds dashboards. By the time the analyst logged in,
they had no context for what was already configured."

### 2. "Empty workspace" is a confidence killer

Across usability tests, 17 of 24 participants described the empty
default workspace as the moment they lost confidence that the product
would be worth the migration. Participants who were given a sample
workspace pre-loaded with realistic finance data progressed roughly
twice as far in the same 30-minute session.

### 3. Time-to-first-value is too long

Median time from signup to first published dashboard, on trials that
eventually converted, is 6.2 days. On trials that did not convert,
median time-to-abandonment is 3.4 days. The activation event,
empirically, has to happen inside the first three days or it usually
does not happen at all.

### 4. Support tickets cluster on three causes

Ticket-tag analysis on 1,840 tier-1 tickets from net-new accounts:

- Data-source connection failures and auth confusion: 38%
- Permissions / "I cannot see what my colleague set up": 22%
- "How do I get started" / generic orientation: 17%
- All other categories combined: 23%

The first two categories are addressable by surfacing the right tasks
to the right role at the right time. The third is addressable by a
non-empty starting state.

### 5. Admin-led "first close" is the natural milestone

In interviews with finance leads, the moment they described as
"this product earns its keep" was consistently the first month-end
close run partially or fully through Lumetric. Eight of 13 finance
leads volunteered this unprompted. None of them named "first
dashboard published," which is what the current onboarding optimizes
for.

## What customers asked for, in their own words

- A setup track that knows whether you are an admin or an analyst.
- A populated example workspace they can poke at without fear of
  breaking anything real.
- Something that tells them they are on track during the first
  close, not just during the first dashboard.
- Fewer email nudges in week one, more in-product guidance.

## Caveats

The interview population skews slightly toward customers who agreed
to talk to us, which historically over-represents engaged users.
Unconverted-trial signal is therefore stronger from telemetry than
from interviews. The telemetry signal is consistent with the
interview signal in direction, if not in intensity.
