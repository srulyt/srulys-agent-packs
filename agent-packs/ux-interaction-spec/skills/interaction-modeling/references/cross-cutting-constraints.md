# Cross-cutting constraints (REQ-§22, §26, §27, §28)

## Design principles and invariants — EIS-§3 (REQ-§22)

Derive a **small number** of principles that should govern later UX design.
Examples of the right shape:

- Users request access to the product, not its implementation components.
- A single user intent should not require multiple redundant access requests.
- Administrative complexity should remain invisible to normal consumers.
- Every asynchronous request must have a persistent discoverable status.
- Users must understand why an unavailable action is unavailable.
- The same concept should use the same terminology throughout the product.
- Administrative authority and resource usage are separate capabilities.

Each is falsifiable — a design can be checked against it. Distinguish
principles from proposed implementation.

`### Design Invariants` carries the harder subset: **behavioral rules later
designs must not violate**. An invariant is written so a reviewer can point at
a mockup and say it breaks. "Every state reachable by the user is reachable
from at least one persistent surface" is an invariant; "the experience should
feel coherent" is filler.

Three to seven principles is the useful range. Twenty principles govern
nothing.

## Accessibility and inclusive interaction — EIS-§17 (REQ-§26)

At the specification stage, identify **behavioral** accessibility requirements
even though visual design has not begun:

- workflows must not require drag-and-drop as the only interaction;
- status changes must be available independently of color;
- error states must identify affected fields/actions;
- important interactions must support keyboard operation;
- timeout behavior must not unexpectedly destroy user work;
- focus or reading-order implications should be noted where interaction
  architecture makes them relevant.

**Do not turn the EIS into a visual accessibility audit.** Capture the
behavioural requirements later design must preserve — contrast ratios, focus
ring styling, and ARIA attribute choices are design-stage concerns.

## Localization and internationalization — EIS-§17 (REQ-§27)

When relevant, identify interaction assumptions affected by localization: RTL
support · text expansion · locale-specific formats · names · time zones ·
currencies · translated system vocabulary · pluralization · sorting/filtering
behavior.

Only include what **materially affects the feature**. Time zones matter to an
approval-expiry feature; pluralization matters to a bulk-selection count;
neither matters to a read-only detail view. Say which apply and why.

EIS-§17 covers both accessibility and localization and is *conditionally
substantive*: when neither raises a behavioural requirement, its body reads
`Not applicable — <reason>` rather than a sentinel. The reason must be
specific — "this feature adds no new interaction affordance and no
locale-dependent value" — not "not applicable".

## Security, privacy, governance, compliance — REQ-§28

Where applicable, translate these constraints into **UX behavior**. The ten
items and where each lands in the EIS:

| # | Governance item | Placed in |
|---|---|---|
| 1 | whether sensitive resources can be discovered | EIS-§7, §9 |
| 2 | whether request reasons are visible to other actors | EIS-§7, §13 |
| 3 | auditability | EIS-§14 |
| 4 | consent | EIS-§13 |
| 5 | data retention | EIS-§8 |
| 6 | access expiration | EIS-§7, §8 |
| 7 | admin override | EIS-§7 |
| 8 | irreversible actions | EIS-§15, §16 |
| 9 | confirmation requirements | EIS-§13, §18 |
| 10 | delegated approval | EIS-§7, §11 |

The author's pass-C governance sweep walks every `REQ-###` with
`kind: governance` in `{stm}/ledger/requirements.md`, places it against this
map, and records the result in `{stm}/ledger/coverage.md` under
`## Pass C — governance_map`. The critic's check C-11 reads both and fails
BLOCKING when a governance requirement has no placement, or when the placement
cites a section that does not carry it.

### Two rules

- **Do not invent legal or security requirements.** A requirement that no
  input states and no regulation obviously imposes is a *recommendation*, and
  belongs under `## Recommendations Awaiting Decision`.
- **Distinguish known requirements from recommendations requiring
  validation.** "GDPR requires this" without a source is exactly the
  fabrication the `confidence` field exists to prevent — record it as
  `inferred` and flag it for validation.
