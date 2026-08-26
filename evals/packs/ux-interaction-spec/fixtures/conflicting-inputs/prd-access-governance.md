# PRD — Access governance

**Status:** Approved · **Owner:** Governance PM

## Summary

Give data product owners a single place to decide access requests, and give
requesters a way to see where their request stands.

## Requirements

1. A requester may have **at most 3 pending requests** at any time. A fourth
   submission is rejected with an explanation.
2. A request is decided by the data product owner. Approve or deny.
3. A denial requires a reason, shown to the requester.
4. On approval, access is **granted immediately** and the requester sees the
   data product in their catalog on the next page load.
5. Access expires after the approved duration and the requester is warned 7
   days before expiry.
6. Every request and decision is written to the audit log.
7. A requester may cancel their own pending request.
8. Owners see pending requests oldest-first.

## Roles

| Role | Can do |
|---|---|
| Requester | Create a request, cancel their own pending request, view their own requests |
| Data product owner | Approve or deny requests for data products they own |
| Auditor | Read the audit log; cannot decide requests |

## Non-goals

- Bulk approval.
- Delegating ownership.
