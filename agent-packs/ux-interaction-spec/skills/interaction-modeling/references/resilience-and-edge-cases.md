# Resilience — feedback, errors, edge cases (REQ-§18, §20, §21)

## System feedback and communication — EIS-§14 (REQ-§18)

Document how the system must communicate important changes. Channels to
consider: immediate confirmation · inline status · persistent status ·
notification · activity history · audit log · email · task/inbox entry.

For every important transition, ask:

> Does the user need to know this **only now**, or must they be able to
> **discover this state later**?

Prefer persistent state for long-lived or asynchronous processes. Avoid
interaction models where critical information exists only in a transient
toast — a notification can be missed, dismissed, or delivered to a session
that no longer exists.

Specify the **class** of surface (`inline`, `persistent status`,
`notification`, `email`, `digest`, `audit entry`), what it must convey, and
who receives it. Do not specify the control, the position, or the copy.

| Transition | Persistent? | Channel class | Audience |
|---|---|---|---|
| Request created | yes — pending status on the resource | inline + notification | requester, approver |
| Request approved | yes — entitlement state | notification + email | requester |
| Provisioning failed | yes — failure state on the request | persistent status + notification | requester, admin |

## Errors and recovery — EIS-§15 (REQ-§20)

Treat recovery as part of the product behavior, not as an error-message
appendix.

For significant operations consider all fourteen failure classes:

validation failure · authorization failure · policy failure · network/service
failure · dependency failure · stale data · race condition · duplicate
submission · partial completion · expired object · deleted object · lost
permission · changed ownership · conflicting edits

For each, specify five things:

1. what happened;
2. what remains true;
3. what the user can do next;
4. whether retry is safe;
5. whether human intervention is required.

Point 2 is the one most often missing and the one users most need. "Your
request failed" without "your existing access is unaffected and no request was
created" leaves the user unable to decide what to do.

Point 4 is a **specification** obligation, not an implementation detail: if
retrying a partially-completed provisioning is unsafe, the specification must
say so and say what the user does instead.

### Prevention versus recovery

They are different requirements. Prevention stops the state arising ("a second
request cannot be created while one is pending"); recovery gets the user out
of it ("a stuck provisioning attempt can be abandoned, returning the request
to `Approved`"). Specify both where both apply.

## Edge cases — EIS-§16 (REQ-§21)

**Actively search** for edge cases instead of waiting for them to appear in
the source material. Twenty-five classes to consider:

first-time use · empty state · no results · very large result sets · no
permissions · partial permissions · inherited permissions · multiple roles ·
user changes organization · deleted user · deleted resource · owner leaves ·
no valid approver · concurrent requests · duplicate action · cancellation ·
expiration · policy change · state change while screen is open · direct/deep
link · outdated bookmark · external collaborator · accessibility constraints ·
localization constraints · mobile/responsive limitations where relevant

**Include only the relevant cases, but demonstrate that the categories were
considered.** The demonstration is a short line per considered-and-excluded
class, grouped at the end of EIS-§16:

> Considered and not applicable: *multiple roles* (this product has a single
> role per user per workspace); *external collaborator* (the feature is
> unavailable to guests, EIS-§7); *mobile/responsive limitations* (no
> interaction here depends on pointer precision or viewport size).

A section that lists only the cases the input already named has not searched;
that is one of the reformatted-PRD markers the critic looks for.

### The high-yield six

If time is short, these six produce the most missing requirements:

`no valid approver` · `concurrent requests` · `policy change` ·
`state change while screen is open` · `owner leaves` · `partial permissions`

Each usually forces a new EIS-§8 transition or a new EIS-§7 rule, which is
exactly the "meaningful additional layer" the specification exists to add.
