---
name: interaction-modeling
description: "How the ux-interaction-spec pack models behaviour before interface: the REQ-§2 separation of product requirement from interaction model from interface design, the 16 REQ-§1 core objectives, input triage for PRDs and rough concepts and supplied UI, actors and conceptual model and terminology, permission and state modeling, journeys versus system workflows, feedback and error and edge-case resilience, and the cross-cutting accessibility, localization and governance constraints. Load when extracting requirements from input or writing any EIS section. Keywords: interaction model, behaviour before interface, actors, conceptual model, permissions, state model, user journey, workflow, edge cases, governance."
---

# Interaction modeling

## Specify behavior before interface (REQ-§2)

Do not jump from requirements into screens. Three layers, kept explicitly
apart:

| Layer | What it is | Owned by |
|---|---|---|
| **Product requirement** | What the product needs to accomplish. | the input |
| **Interaction model** | How actors, objects, permissions, states, actions, workflows, and system responses behave. | **the EIS** |
| **Interface design** | How those behaviors are represented through pages, panels, dialogs, menus, buttons, forms, controls, visual hierarchy, layout, styling. | later design work |

The EIS focuses primarily on the **interaction model**.

Prefer:

> A user without access who is eligible for approval must be able to initiate
> an access request. Once submitted, exactly one active pending request exists
> and the user must be able to determine that the request is pending whenever
> they encounter the resource.

Not:

> Put a blue Request Access button in the upper-right corner. Clicking it
> opens a 480-pixel modal.

The first is an interaction requirement. The second is a design decision —
legitimate only when the existing product has a strong established pattern
that makes it an explicit, sourced recommendation.

You **may** identify likely UI surfaces, entry points, information
requirements, and the controls a later designer will need. You must avoid
unnecessary decisions about visual presentation. The critic's layer-separation
check (C-13) reads `{out}/eis.md` for exactly this.

## Discover gaps, don't reorganise the PRD

The pack must discover gaps rather than merely reorganize the source PRD. A
successful specification will often expose product questions that were not
apparent in the original requirements. If it exposes none, that is a finding
about the review, not a compliment to the input.

## References

| File | Use it for |
|---|---|
| [core-objective-coverage.md](references/core-objective-coverage.md) | The 16 REQ-§1 objectives, the pass-D sweep, and the three ways it fails. |
| [input-triage.md](references/input-triage.md) | REQ-§6 extraction, conflicts, the ask-only-if-necessary test, rough concepts (§37), supplied UX concepts as proposals (§38), supplied UI (§39). |
| [actors-concepts-terminology.md](references/actors-concepts-terminology.md) | EIS-§4, §5, §6 — actors, the user-facing vs implementation split, and the glossary. |
| [permissions-and-state.md](references/permissions-and-state.md) | EIS-§7 and §8 — the capability model, the six capabilities to keep apart, and full lifecycle modeling. |
| [journeys-and-workflows.md](references/journeys-and-workflows.md) | EIS-§9, §10, §11, §12 — entry points, journeys, system workflows, async, blueprints. |
| [resilience-and-edge-cases.md](references/resilience-and-edge-cases.md) | EIS-§14, §15, §16 — feedback channels, the 14 failure classes, the 25 edge-case classes. |
| [cross-cutting-constraints.md](references/cross-cutting-constraints.md) | EIS-§3 principles and invariants, EIS-§17 accessibility and localization, and the REQ-§28 governance placement map. |

Document shape — which headings exist, in what order — belongs to the
`eis-document-contracts` skill, not here.

## Path resolution

Reference files resolve through the ladder in each agent's
`## Skills to Load` section: already-in-context, then
`.github/skills/interaction-modeling/references/<file>`, then
`agent-packs/ux-interaction-spec/skills/interaction-modeling/references/<file>`,
then `skills/interaction-modeling/references/<file>` relative to the parent of
the agent directory.
