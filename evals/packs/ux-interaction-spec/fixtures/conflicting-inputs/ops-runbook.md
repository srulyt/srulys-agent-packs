# Ops runbook — access governance (internal, maintained by Platform Ops)

Operational notes for the on-call engineer. This is the current production
behaviour, whatever the PRD says.

## Pending request limits

The pending-request cap is **5 per requester**, not 3. It was raised in
March after the analytics org complained. The config key is
`access.request.pending_max` and it is set per-tenant; 5 is the default
everywhere today.

## Org admin override

Org admins can approve a request **on behalf of** a data product owner when
the owner has been unresponsive for more than 5 business days. This happens
roughly twice a week. The audit log records both the org admin as the actor
and the owner as the delegated party.

Org admins can also deny on behalf of an owner, but Ops policy is that they
only ever approve — a denial should come from the owner.

## Escalation

Requests older than 14 days page the owning team's manager. This is separate
from the org-admin override above and does not itself grant access.

## Things that go wrong

- If the requester leaves the company between request and decision, the
  request stays pending and eventually escalates to a manager who cannot
  action it. We close these manually.
- If a data product is deleted while a request is pending, the request is
  orphaned. There is a weekly cleanup job.
- Duplicate requests for the same data product from the same requester are
  possible and common. Owners see both.
