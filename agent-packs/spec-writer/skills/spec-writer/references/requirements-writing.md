# Writing requirements

## EARS functional requirements

Each FR is exactly **one** `shall` statement. If an FR has zero or several `shall`s, split it. For example, "authenticate, email, and log" becomes three FRs.

| Pattern | Form | Use for | Example |
| --- | --- | --- | --- |
| Ubiquitous | The `<system>` shall `<response>`. | Always-active behaviour | The billing service shall record every charge in an immutable audit log. |
| Event-driven | When `<trigger>`, the `<system>` shall `<response>`. | Discrete events, journey steps | When a user requests a password reset, the system shall send one single-use reset link within 60 seconds. |
| State-driven | While `<state>`, the `<system>` shall `<response>`. | Behaviour during a mode/state | While in maintenance mode, the API shall return HTTP 503 with a `Retry-After` header. |
| Optional feature | Where `<feature/role is included>`, the `<system>` shall `<response>`. | Configurable features, role-conditioned behaviour | Where two-factor authentication is enabled, the system shall require a second factor at sign-in. |
| Unwanted behaviour | If `<undesired condition>`, then the `<system>` shall `<response>`. | Errors, failures, misuse, limits | If the payment provider times out, then the system shall mark the order pending and retry once. |
| Complex | While `<state>`, when `<trigger>`, the `<system>` shall `<response>`. | Combined state and trigger | While the account exceeds its quota, when an upload completes, the system shall reject the file and report the quota. |

- **System clause:** name the product or component, never "we" or "the user".
- **Triggers and states:** must be observable.
- **Response:** say *what* the system does, not *how*. Use active voice, make it concrete, and make it falsifiable. "Appears quickly" fails; "renders within 500 ms at p95" passes.
- **Thresholds:** include quantitative thresholds wherever relevant. Mark inferred assumptions, and keep conflicting inputs visible as OQs instead of choosing silently.
- **Rationale:** a one-line *Rationale* is optional. It ties the FR to a goal or user need.

## Priority

Every FR gets a priority:

- **P0:** a first-ship blocker.
- **P1:** should have.
- **P2:** nice to have.

Security, data-integrity, legal, and blocking-dependency requirements default to P0. A P0 must never depend on a P1 or P2.

## Acceptance criteria

- **Shape:** nested under the FR as `AC-<FR>.<n>`, written Given/When/Then with concrete inputs and an observable result.
- **Count:** varies with complexity. A simple FR may need 1–2; a complex one, 5 or more.
- **Coverage:** the happy path, plus the negative, boundary, and state-transition cases that are plausible for the FR. Pin deny paths for permissions, e.g. "Given a Viewer, when they attempt delete, then the system refuses and changes nothing".
- **Format:** Given/When/Then is the default. Use a table or specification-by-example inside an AC when parameter variations or calculation rules read more clearly that way.
- **Quality:** each AC must be independently testable, unambiguous, and traceable to its FR.

## Goals and metrics

- **SMART:** each metric is specific, measurable, achievable, relevant, and time-bound. Give a baseline, a target, and a measurement window, and state the type (business, user, or technical).
- **Balance:** pair leading indicators (adoption, usage, performance) with lagging ones (retention, satisfaction, revenue). Avoid single vanity metrics.
- **Instrumentation:** a metric must be instrumentable. When it depends on new telemetry, name the event or data source (Telemetry & Analytics).
- **Size:** keep a small set specific to the feature; don't copy generic metric catalogues.

## Non-functional requirements

- **Deltas only:** write NFRs only for what the feature needs **beyond or differently from** the platform or organizational baseline, e.g. unusual latency, scale, availability, privacy, accessibility, DR, or interoperability needs. Never restate inherited baseline controls as feature NFRs. If the baseline matters, note it once as an assumption.
- **Shape:** each NFR has a measurable target and a verification method.
- **Size:** a focused set, typically 5–10, beats dozens of boilerplate items.

## Test scenarios (when gated in)

Each `TS-NN` names the FR and AC IDs it covers and its type: unit, integration, e2e, performance, security, accessibility, migration, or DR. Every P0 FR and every NFR needs validation coverage.
