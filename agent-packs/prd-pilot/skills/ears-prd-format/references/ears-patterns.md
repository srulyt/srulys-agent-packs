# EARS Pattern Catalogue — Worked Examples

Overflow reference for `ears-prd-format/SKILL.md`. One worked Functional
Requirement (with a nested acceptance criterion) per EARS pattern. Use
these as templates; replace `<system>` with the real product/component
name — never "we" or "the user".

## 1. Ubiquitous — `The <system> shall <response>.`

Always-active behaviour with no trigger or precondition.

> **FR-01** *(ubiquitous, P0)* — The Billing service shall record every
> charge in an immutable audit log.
>
> **AC-01.1** — Given a charge of any amount is processed, when the
> charge completes, then a corresponding append-only audit entry exists
> with the charge id, amount, and timestamp.

## 2. Event-driven — `When <trigger>, the <system> shall <response>.`

Behaviour triggered by a discrete event.

> **FR-02** *(event-driven, P0)* — When a user submits a password-reset
> request, the Auth service shall send a single-use reset link within
> 60 seconds.
>
> **AC-02.1** — Given a registered email address, when the user submits
> a reset request, then exactly one reset email is delivered and its
> link is invalidated after first use.

## 3. State-driven — `While <state>, the <system> shall <response>.`

Behaviour active for the duration of a state.

> **FR-03** *(state-driven, P1)* — While the system is in maintenance
> mode, the API gateway shall return HTTP 503 with a Retry-After header
> for all write endpoints.
>
> **AC-03.1** — Given maintenance mode is enabled, when a client issues
> a POST request, then the response is 503 and includes a Retry-After
> header.

## 4. Optional-feature — `Where <feature is included>, the <system> shall <response>.`

Behaviour that applies only when an optional feature is present.

> **FR-04** *(optional-feature, P2)* — Where two-factor authentication
> is enabled for an account, the Auth service shall require a valid
> second factor before granting a session.
>
> **AC-04.1** — Given an account with 2FA enabled, when the user
> supplies a correct password but no second factor, then no session is
> granted and a second-factor prompt is shown.

## 5. Unwanted — `If <undesired condition>, then the <system> shall <response>.`

Behaviour in response to an error or undesired condition.

> **FR-05** *(unwanted, P0)* — If a payment provider returns a timeout,
> then the Checkout service shall mark the order as pending and retry
> once after 30 seconds.
>
> **AC-05.1** — Given a provider timeout on first attempt, when 30
> seconds elapse, then exactly one retry is issued and the order status
> is "pending" in the interim.

## 6. Complex — combination, e.g. `When X, while Y, the <system> shall <response>.`

Combines a trigger and a state (or multiple conditions).

> **FR-06** *(complex, P1)* — When a file upload completes, while the
> account is over its storage quota, the Storage service shall reject
> the upload and notify the user of the quota breach.
>
> **AC-06.1** — Given an account at 100% of quota, when an upload
> finishes transferring, then the file is not persisted and a
> quota-exceeded notice is returned.

## Common rewrites (fixing invalid FRs)

| Invalid | Why | Fixed |
|---|---|---|
| "We shall send a confirmation email." | "We" is not a system | "The Notifications service shall send a confirmation email …" |
| "The system shall validate input and shall log errors." | Two `shall`s | Split into two FRs, one `shall` each. |
| "The system shall use Redis to cache sessions." | Describes *how* | "The Session service shall return a cached session within 50ms p95." (what, not how) |
| "The notification appears quickly." | Not falsifiable; no `shall`; no system | "When a notification is generated, the Notifications service shall display it within 2s p95." |
