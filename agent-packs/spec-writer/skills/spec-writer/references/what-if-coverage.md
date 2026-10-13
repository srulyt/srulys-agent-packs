# What-if coverage

Reviewers ask "but what if…?" when a spec only captures the happy path in its input. A complete spec answers those questions up front. For every FR, and for every journey step when a UX section exists, work out what can plausibly go wrong. Write each consequential case as a normal FR, usually unwanted-behaviour (`If…, then…`) or state-driven (`While <degraded state>…`), with its own negative ACs. Do this even when the input never mentions the case. Do not tag these FRs or move them into a separate section.

## Lenses

Apply only the lenses relevant to the feature. Skip any that don't apply rather than producing boilerplate.

| Lens | Probe |
| --- | --- |
| Input | Empty, missing, malformed, wrong type, oversize; boundaries (0, 1, max, max+1); duplicates; special characters, encoding, locale, time zones |
| State and lifecycle | First use / empty state; partially completed flow; cancel, undo, retry, re-entry; stale data; referenced item deleted, renamed, or moved; expired items |
| Concurrency | Simultaneous edits; double submit; out-of-order events; idempotency of retries |
| Dependency failure | Downstream unavailable, slow, timing out, partial success, inconsistent or unexpected response |
| Permissions | Unauthenticated; insufficient role; role or access revoked mid-session; cross-tenant or cross-owner access; deny path |
| Limits and scale | Quotas, rate limits, size caps, capacity exhaustion, very large lists, long-running operations |
| Data integrity | Loss, corruption, partial writes, rollback, migration of existing data, backward compatibility |
| Environment | Network loss/offline; session expiry; old clients or version skew; unsupported browser/device |
| Misuse | Malicious input, enumeration, spam/flooding, privilege escalation attempts |
| Recovery and feedback | How the user learns of the failure; what state they are left in; how they recover; what is logged or alerted |

## Writing the result

- **Response:** state an observable, recoverable outcome: what the user sees, what state is preserved, and what is retried or rolled back. Avoid generic responses such as "shall handle errors gracefully".
- **Grouping:** group related failure cases into one FR when they share a response. Write separate FRs only when the responses differ.
- **Safe defaults first:** when an established safe practice or obvious least-surprise outcome exists, specify it as the response instead of a TBD. Examples: neutralise injection per OWASP guidance, make duplicate submits idempotent, keep existing state and user input on validation or dependency failure, show an empty state rather than an error for zero results. If the default is a real choice, list it under Assumptions so reviewers can overturn it.
- **Business decisions:** when the right response is a product, policy, or legal decision that can't be safely inferred (numeric limits, entitlement, retention, pricing), still write the FR. Use `[TBD — reason]` as the response and add an OQ that phrases the what-if: "What should happen when…?". A visible open question is the goal; a guessed policy is not. Too many TBDs is also a gap: reviewers will still ask "what if".
- **Interview:** ask about a what-if only when its answer changes scope or a P0 behaviour.
- **Risks:** a failure the spec can't prevent becomes a Risk with a mitigation. A failure the system must handle becomes an FR.
- **Proportionality:** include a case only when it is plausible and consequential for this feature. If the input argues against a case, leave it out.
