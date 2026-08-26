# PRD — Governed Data Product Access

**Status:** Draft · **Owner:** Data Platform PM · **Target:** H2

## Problem

Analysts across the company cannot get to the data products they need without
filing a ticket that takes three to five business days. Data owners, meanwhile,
have no visibility into who is asking for what or why, and approve requests
from a spreadsheet a platform engineer maintains by hand.

## Goal

Let an analyst discover a governed data product, request access to it with a
stated purpose, and receive a decision from the data owner without a ticket.

## In scope

- A catalog of governed data products, browsable and searchable.
- An access request carrying a stated business purpose and a requested
  duration.
- An approval decision by the data product's owner.
- Notification of the outcome to the requester.

## Out of scope

- Provisioning the underlying warehouse grants (handled by the existing
  entitlement service).
- Data quality scoring.
- Cost attribution.

## Requirements

1. An analyst must be able to search the catalog by data product name, domain,
   and owning team.
2. A data product marked `restricted` must not appear in search results for
   users who do not already hold access, but must be discoverable by name if
   the user knows it exists.
3. An access request must capture: requester, data product, business purpose
   (free text, required), requested duration, and requested access level
   (`read` or `read-write`).
4. The data product owner must be able to approve or deny a request.
5. A denial must carry a reason that is visible to the requester.
6. Approved access must expire at the end of the requested duration.
7. The requester must be notified when a decision is made.
8. The system must retain an audit record of every request and decision for
   seven years.
9. A data product may have more than one owner. Any single owner may decide.
10. Requests older than 14 days without a decision are escalated to the owning
    team's manager.

## Success criteria

- Median time-to-decision under 8 business hours.
- 80% of access grants flow through this path rather than tickets within two
  quarters.

## Open items

- Whether an analyst can request access on behalf of a team.
- Whether an owner can grant access at a level lower than the one requested.
