# Anti-requirements — what must never appear (REQ-§29, §42, §43)

Three lints. All three read the delivered documents, not an agent's
intentions.

---

## 1. Premature visual design (REQ-§29)

Unless the user specifically requested it, the EIS must **not** define:

- colors
- typography
- spacing
- pixel dimensions
- visual styling
- iconography
- exact component placement
- detailed page layouts
- decorative treatment

It **may** define structural interaction requirements:

- a persistent way to see status is required
- users need access to both current state and history
- the action must be available from the resource context
- administrators need a batch-management experience
- a potentially destructive operation requires explicit confirmation

The dividing line: **what must be true** is in scope; **how it looks** is not.

### The rewrite move

An input that supplies a visual hint carries behavioural content underneath
it. Lift the behaviour and drop the presentation.

The hint itself is never discarded: `@eis-context-analyst` records it at intake
as a `VIS-###` record in `{stm}/ledger/context-ledger.md`, carrying the hint,
its `behavioural_content`, and a verdict. That instruction lives in
`interaction-modeling/references/input-triage.md`, which is the analyst's
file. **Readers of *this* file — the author, the researcher and the critic —
do not write `context-ledger.md`**; they read the `VIS-###` records the analyst
already wrote and verify the substitution was recorded rather than silent.

| Input says | EIS says |
|---|---|
| "a modal with two tabs for duration and ticket" | "the requester chooses between a duration-based and a ticket-based justification; the two are mutually exclusive and both are available at the point of request" |
| "a red banner at the top of the page" | "a failed provisioning attempt is communicated persistently wherever the user encounters the resource, and is distinguishable from a pending attempt without relying on colour" |
| "a green check icon in the table row" | "the entitlement's active state is visible in any list that shows the resource" |
| "put Approve and Reject side by side" | "the approver can act on a request without leaving the request context; approval and rejection are equally available and rejection requires a reason" |

Never silently delete a visual hint — record it and explain the substitution.
The user asked for something; they are owed an answer about what happened
to it.

### Exception

If the invocation explicitly asks for visual guidance, it is in scope, and
the EIS says so in EIS-§2 `In Scope` so a later reader knows the omission
policy was deliberately overridden.

---

## 2. Implementation leakage (REQ-§42)

The EIS specifies **product semantics**, not software architecture.

Good:

> Approval creates an entitlement associated with the user and product. If the
> product's access policy later changes, existing entitlements remain valid
> unless the policy change explicitly triggers reevaluation.

Avoid unless dictated by a stated constraint:

> Insert a row into the ProductEntitlements PostgreSQL table and publish an
> event to Kafka.

Leak markers: named datastores, table or column names, queue and topic names,
API route shapes, class or service names, framework names, SDK calls, protocol
details, and internal identifiers with no user-visible meaning.

A technical constraint **is** in scope when it changes behaviour — "the
provisioning call is asynchronous and may take up to ten minutes" belongs in
EIS-§11 and drives EIS-§8. State the *consequence*, not the mechanism.

---

## 3. Generic UX filler (REQ-§43)

The documents must be precise, structured, concise where possible, explicit
where ambiguity matters, in product/UX language, and consumable by PMs,
designers, engineers, and AI systems.

Banned filler:

- "make it intuitive"
- "ensure a seamless experience"
- "provide a user-friendly interface"

and their relatives: "delightful", "frictionless", "best-in-class",
"easy to use", "clean and modern", "world-class".

Replace with a testable behavioural requirement.

Instead of:

> Make access requests intuitive.

Write:

> When a user encounters a resource they may request but cannot currently use,
> the experience must distinguish "requestable" from "unavailable" and provide
> a direct path to initiate the request.

The test: could a reviewer disagree with it on the evidence? If not, it is
filler.

---

## How the critic applies these

Check C-3 lints all three across `{out}/eis.md` and `{out}/decision-log.md`.

| Finding | Severity |
|---|---|
| A visual prescription in an interaction contract, capability matrix, or state model | BLOCKING |
| A visual prescription elsewhere in the EIS | CONCERN |
| Implementation leakage that changes what a reader thinks the product does | BLOCKING |
| Implementation leakage that is merely noise | CONCERN |
| Filler in EIS-§3 `Design Principles`, EIS-§13, or EIS-§18 | BLOCKING |
| Filler elsewhere | CONCERN |

Severity is higher inside the sections a designer builds directly from,
because that is where an unfalsifiable sentence does the most damage.
