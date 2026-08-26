# Acme Data Cloud — supplied host-product material

Bundle assembled for the "bulk approvals" specification. Everything below is
first-party material about the host product itself. No external or competitor
material is included, and this environment has no network access, so nothing
here can be supplemented by browsing.

---

## 1. Product help centre — "Approving an access request"

Source: Acme Data Cloud Help Centre, article `help.acme.example/access/approving`
Published 2025-11-04. Retrieved 2026-08-19. Applies to release 2025.11.

> An approver opens **Requests → Awaiting me**, selects a request, and reviews
> the requester, the data product, the requested permission level and the stated
> business justification. Approving grants the permission and notifies the
> requester by email and in-product. Declining requires a reason of at least 20
> characters, which is shown to the requester verbatim.
>
> Requests are actioned one at a time. There is currently no way to approve or
> decline more than one request in a single action.
>
> An approver may **delegate** an individual request to another approver in the
> same group. Delegation is recorded in the request's history and the original
> approver remains visible as the delegator.

---

## 2. Internal design-system documentation — selection and bulk action

Source: Acme Design System (internal), `ds.acme.internal/patterns/table-selection`
Version 4.2, last updated 2026-02-17. Retrieved 2026-08-19.

> **Selection.** Tables that support multi-select render a checkbox column. The
> header checkbox selects the rows *currently loaded*, never the full result set;
> a "Select all N matching" affordance appears alongside it when the result set
> exceeds the loaded page, and choosing it switches the selection to a
> *query-based* selection that survives pagination and filter-stable refetches.
> The two selection kinds are visually distinguished because their semantics
> differ under filter change: a row-based selection is preserved, a query-based
> selection is invalidated and must be re-confirmed.
>
> **Bulk actions.** A bulk action bar is pinned to the bottom of the viewport
> while a selection exists. It states the count and the action, never the row
> identities. Destructive or irreversible bulk actions require a confirmation
> step that re-states the count. Bulk actions are **not** optimistic: the bar
> enters a progress state and the table does not mutate until the server responds.
>
> **Partial failure.** Where the underlying operation is per-row, the result is
> reported per row. The pattern is: a summary line ("42 of 50 succeeded"), an
> inline error state on each failed row, and a "Retry failed" action scoped to
> the failures only. Silently reporting overall success when some rows failed is
> a defect, not a simplification.

---

## 3. Platform engineering note — entitlement write throughput

Source: Acme Platform Engineering, internal memo `PLAT-2026-114`.
Dated 2026-05-30. Retrieved 2026-08-19.

> The entitlement service accepts a maximum of **25 grant operations per
> request** and rate-limits an approver principal to 4 such requests per minute.
> Grants are applied individually and are **not transactional**: a batch may
> partially succeed and there is no rollback. Each grant returns its own status.
> Callers must be prepared to surface partial success and to retry the failed
> subset; retrying the whole batch will produce duplicate-grant errors
> (`already_granted`) for the rows that already succeeded, which are safe to
> ignore but must not be reported to the user as failures.

---

## 4. Support ticket analysis — approver complaints

Source: Acme Support, saved report "Access approvals — top themes Q1 2026".
Report generated 2026-04-08. Retrieved 2026-08-19. n = 312 tickets.

> Top three themes among approver-raised tickets:
>
> 1. **Volume (41%).** Approvers in large tenants receive 30–200 requests per
>    onboarding wave and must action each individually. Median time to clear a
>    wave: 3.2 days.
> 2. **No context at the list level (26%).** Approvers report opening each
>    request only to discover it is a duplicate of one they just approved, or
>    from a requester whose access they just revoked.
> 3. **Accidental approval (11%).** Approvers report approving the wrong request
>    after mis-clicking in a fast sequence of individual approvals. There is no
>    undo; the only remedy is to revoke, which sends the requester a separate
>    revocation notice and is reported as confusing.

---

## 5. Notes on what is NOT available

The following could not be supplied and cannot be researched in this
environment:

- No competitor product documentation was obtained. Comparable access-governance
  products are commercial and their approval flows are behind sales-gated demo
  environments.
- No adjacent-domain material was obtained (e.g. how email clients, ticketing
  systems or code-review tools handle bulk triage). This was time-boxed out of
  the bundle.
- No usability testing, session recordings or analytics on the existing approval
  screen beyond the support-ticket themes above.
