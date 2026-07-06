# Scripted interview answers (grill-me: UI-forward context gaps)

Reply to the grill-me question set when the orchestrator parks at
`awaiting-interview-answers`. Because this spec is UI-forward, the
grill escalates persona / journey / role gaps to P0; the scripted user
answers them concretely so the loop closes.

## Users & Personas
- Which distinct user types / roles use this? — Members (submit and
  view their own items), Reviewers (review and decide), Admins
  (configure the board and manage members).

## Jobs To Be Done
- What job is each hiring this for? — A Member wants to get an item
  reviewed quickly so they can unblock their work; a Reviewer wants a
  single queue so they can clear decisions in one sitting.

## User Journey
- Primary end-to-end steps? — Member opens the board -> creates an
  item via a multi-step form -> submits -> Reviewer sees it in a queue
  -> opens detail -> approves/rejects/returns -> Member is notified.

## Roles & Permissions
- Who can do what? — Members: create/view own items, cannot decide.
  Reviewers: decide on items in their queue, cannot configure the
  board. Admins: configure board + manage members, cannot decide on
  behalf of a Reviewer. Deny by default; enforced server-side.

## Problem Statement / Goals
- Problem & metric? — Review requests get lost in chat; reduce median
  time-to-decision from 2 days to under 4 hours for 70% of items in 90
  days.

## Solution Summary
- Rough shape? — A dedicated review board with Member, Reviewer, and
  Admin surfaces and role-scoped actions.
