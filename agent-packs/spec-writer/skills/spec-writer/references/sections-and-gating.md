# Sections and gating

## Mandatory sections (all specs, this order)

Document Information · Problem Statement · Goals & Success Metrics · Users & Personas · Solution Summary · Functional Requirements · Risks & Mitigations · Open Questions · Out of Scope.

- Use these names verbatim. Each section is non-empty, or carries `[TBD — reason]` with a matching `OQ-NN`. An empty Out of Scope list is a valid result, not a TBD.
- Acceptance criteria are never a top-level section; they nest under each FR.
- `Assumptions` (`A-NN`) is optional in any spec. List conditions that, if false, would change requirements, so reviewers can challenge them.

## IDs

`FR-NN`, `AC-<FR>.<n>` (e.g. `AC-03.2`), `NFR-NN`, `R-NN`, `OQ-NN`, `TS-NN`, `A-NN`, `ACR-NN`. Cross-reference with anchored links (`[FR-03](#fr-03--title)`), not bare section names.

## spec_kind

Settle this before drafting; ask if it's unclear.

- `product`: behaviour-shaped. FRs never name internal components, libraries, datastores, frameworks, languages, or specific APIs. Omit sections marked `technical|mixed`.
- `technical`: implementation detail lives inline in the dedicated sections (Data Model, API Contract, Capacity, Threat Model).
- `mixed`: FRs stay behaviour-shaped. User-supplied implementation detail is isolated in `Technical Considerations`.

## Gated sections

Include a gated section only when its axis fires **and** the `spec_kind` permits it. If an axis is ambiguous, omit the section and raise an OQ. Never add sections just for completeness.

| Axis | Fires when | Sections (kind restriction) |
| --- | --- | --- |
| experience-surface | New or materially changed screens/views/panels/dashboards; navigation or IA change; new interactive affordances; multi-step flows (wizard, onboarding, checkout, approval); role-varying UI behaviour. A single isolated affordance tweak with one actor and no role variation does **not** fire it. | User Experience: Journeys & Roles |
| cross-team-scope | More than one team owns delivery; named partner orgs; cross-org dependencies | Stakeholders & Reviewers; Dependencies; Test Scenarios |
| infra-platform-change | New service, region, or datastore; breaking API; capacity-shaping change | NFRs; Test Scenarios; Capacity & Performance (technical\|mixed); NFR↔FR Traceability (technical\|mixed) |
| security-surface | Auth-flow change; new data egress; PII handling; supply-chain change; new trust boundary | Security & Compliance; Threat Model Summary (technical\|mixed) |
| regulatory-load | A regulatory or compliance review is in scope, or the user names a regime | Regulatory & Privacy (defer regime specifics to user-supplied guidance) |
| persistence-data | New schema; retention change; new analytics events | Telemetry & Analytics; Data Model (technical\|mixed) |
| public-api-surface | External consumers; SDK changes; webhooks; customer-visible API | API Contract; Versioning & Deprecation Policy (both technical\|mixed) |
| rollout-risk | Phased release; feature flags; kill switch; customer migration | Rollout Plan; Rollback Strategy |
| update-rename | A published spec renames items | Appendix: Aliases & Deprecations |

Glossary is optional for any spec. Add it when domain terms or acronyms would otherwise be ambiguous.

## Woven versus dedicated user context

Every spec weaves personas, jobs, and role context into Problem Statement, Users & Personas, and the FRs. The dedicated UX section appears only when experience-surface fires. Even then it never repeats the persona table: it references personas by name and adds journeys, roles and permissions, and optional job-opportunity scoring.
