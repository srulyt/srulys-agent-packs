# Golden — smoke-update-upper-section-stability (C2, F2 regression guard)

The prior spec is the workspace-events digest fixture (also used by
`smoke-update-minimal-edit-discipline`). The user asks for ONE
change: add a keyboard-shortcuts FR. Everything above the Functional
Requirements section MUST stay byte-identical.

## What is asserted

- The prior bait spans from upper sections survive verbatim:
  - Problem Statement first sentence (`Workspace members miss
    important changes across squads. Scrolling individual channels
    to find what matters takes too long.`).
  - Solution Summary closer (`Built on the existing
    \`workspace-events\` Kafka topic. No new datastore.`).
  - Goals first metric clause (`Reduce median time-to-first-action
    on a flagged change from`).
  - Personas table PM row.
- `edit-audit-json.preserved_unchanged_sections` includes
  `Problem Statement`, `Goals & Success Metrics`, `Users & Personas`,
  `Solution Summary`.
- `edit-audit-json.counts.add >= 1`, `counts.modify <= 1`,
  `counts.reorder == 0`, `counts.rename == 0`.
- No non-mechanics edit has a locator inside any upper section.
- Critic `findings-json` contains no entry whose `issue` or `rubric`
  field includes the substring `upper-section`.
- CHANGELOG.md gains an `### Added` entry.

## What is NOT asserted

- Exact wording of the new FR or its acceptance criterion.
- Specific version bump value (the case does not pin minor vs patch
  semantics; `version-bump-json` is required by the drafter contract
  but not constrained here).
- Any text below `## Functional Requirements`.

## Failure interpretation

- A bait span missing → F2 ratchet bypassed; drafter "improved"
  upper-section wording.
- `preserved_unchanged_sections` missing an upper-section name →
  drafter touched the section even if the bytes happen to match.
- An `upper-section` finding from the critic → critic-side regression
  on D10's upper-section-ratchet sub-rubric.
