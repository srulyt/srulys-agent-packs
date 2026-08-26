# Interaction contract — the EIS-§13 scenario shape (REQ-§16)

Interaction contracts are where ambiguity stops being pushed onto the UX
designer. Write one for every interaction whose behaviour is not obvious from
the journey alone.

## The twelve fields

Each scenario is a `###` block under EIS-§13, headed by its id and name, and
carries all twelve fields in this order:

| # | Field | Content |
|---|---|---|
| 1 | Actor | Who performs it — a role from EIS-§4, named identically. |
| 2 | User goal | What they are trying to achieve, in their words. |
| 3 | Preconditions | What must already be true. One bullet per condition. |
| 4 | Trigger | What starts it. An intent, not a click on a named control. |
| 5 | System response | A **numbered** behavioural sequence. |
| 6 | Resulting state | Which objects moved to which EIS-§8 states. |
| 7 | Alternate paths | Meaningful non-error branches. |
| 8 | Error cases | What can fail and what the user sees and can do. |
| 9 | Permission rules | Which EIS-§7 rules apply and what a denial looks like. |
| 10 | Notifications or feedback | What is communicated, to whom, through which surface class. |
| 11 | UX requirements | Behavioural requirements design must satisfy. |
| 12 | Open questions | `Q-MD-###` ids that would change this scenario. |

A field with nothing to say reads `None.` — it is never omitted. The count of
`###` scenario blocks and the presence of all twelve fields in each is a
structural property the critic checks.

## Scenario ids

`UX-###` for generic scenarios, or `UX-<AREA>-##` where a feature has distinct
areas (`UX-ACCESS-03`). Ids are stable for the life of the document and are
referenced from EIS-§10 journeys, EIS-§22 traceability, and
`decision-log.md`'s `Implications:` lines.

## Worked example

**UX-ACCESS-03 — Request governed access**

Actor: Consumer

User goal: Obtain access to a product I can see but cannot use.

Preconditions:

* Product is published.
* Consumer can discover the product.
* Consumer lacks active access.
* Product requires approval.

Trigger:
Consumer indicates intent to obtain access.

System response:

1. Determine whether an existing pending request exists.
2. Determine the approval policy.
3. Gather required justification if applicable.
4. Create exactly one pending request.
5. Communicate that approval is pending.
6. Preserve the pending state anywhere the user later encounters the product.

Resulting state: `Request: Not requested → Pending`. Product entitlement
unchanged.

Alternate paths:

* Existing pending request → show the existing request rather than create another.
* Consumer gains access through another mechanism → resolve the pending request.
* Product becomes unavailable → request becomes invalid/cancelled.
* Request rejected → expose the outcome and permissible next actions.

Error cases: request creation fails → the consumer is told the request was not
created and the intent is still available; no phantom pending state is shown.

Permission rules: EIS-§7 `Request access` = Yes for Consumer when eligible but
not entitled; an ineligible consumer is told **why**, not merely that the
action is unavailable.

Notifications or feedback: the approver is notified through the product's
existing request-notification surface; the requester sees persistent pending
status wherever the product appears.

UX requirements: pending status must be discoverable from every surface that
shows the product; the outcome must be reachable without re-navigating to the
original entry point.

Open questions: `Q-MD-007` — may an administrator bypass approval?

## Behaviour, not interface

Step 5 says "Communicate that approval is pending", not "show a green toast in
the top-right". The contract fixes **what must be true**; the designer chooses
the surface. See the `interaction-modeling` skill's layer-separation rules.

Legal in a contract: intents, states, rules, timing classes, surface *classes*
(`inline`, `notification`, `email`, `digest`), and content requirements.

Not legal: control types, layout, position, colour, iconography, copy strings,
component names, spacing, and animation.
