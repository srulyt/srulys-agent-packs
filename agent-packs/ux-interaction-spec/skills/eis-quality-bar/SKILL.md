---
name: eis-quality-bar
description: "The completion standard for an Experience Interaction Specification: the REQ-§35 quality bar by category, the 16-point REQ-§36 Definition of Done with its strict n/a rule and verdict model, the REQ-§45 fourteen discovery probes that separate a real EIS from a reformatted PRD, the REQ-§29/§42/§43 anti-requirement lints, and the REQ-§44 conceptual distinctions. Load when reviewing, scoring, or self-checking a specification. Keywords: definition of done, quality bar, review, critic, anti-requirements, premature visual design, discovery probes, conceptual distinctions."
---

# EIS quality bar

Do not consider the EIS complete merely because all headings contain text.

## Quality bar by category (REQ-§35)

**Requirements** — every material input requirement is accounted for;
contradictions are identified; derived behavior is labeled correctly.

**Actors** — every meaningful actor is represented; cross-role interactions
are clear.

**Permissions** — relevant capabilities are enumerated; discoverability is
distinguished from access; access is distinguished from administration;
inheritance/override behavior is addressed where relevant.

**State** — important objects have explicit lifecycle models; pending and
failure states are represented; cancellation, expiration, and revocation are
addressed where relevant.

**Flows** — all major user goals have flows; alternate paths are represented;
multi-user handoffs are represented; async operations are correctly modeled.

**System behavior** — the system response to important actions is explicit;
persistent versus transient feedback is clear; error recovery is defined.

**Research** — host-product conventions were investigated; relevant
competitors were investigated; research affected recommendations rather than
merely being summarized; important claims have evidence.

**Design readiness** — a designer should not have to invent the permission
system, the state machine, basic business rules, approval semantics, ownership
semantics, failure semantics, or lifecycle behavior. Each is either resolved
in the EIS or explicitly listed as an unresolved product decision.

## Emptiness detection

A heading with text is not a scored point. Treat as empty:

- a body that restates its own heading;
- a body that lists categories without applying them to this feature;
- a table with header rows and no data rows — **except RES-§9 in `skipped`
  mode**, where the column header row alone, with no data rows and no `PAT-###`
  records, is the contracted form and is not a vacuity finding; see
  `eis-document-contracts/references/research-doc-skeleton.md`, which owns this
  rule;
- a Mermaid block whose states appear nowhere in prose;
- `TBD`, `TODO`, `N/A` with no reason, or a surviving `EIS-PENDING` sentinel;
- `Not applicable` with no reason attached.

Empty bodies score `fail`, not `partial` — with that one carve-out: a
header-row-only RES-§9 on a `skipped` run is not an empty body, it is the form
the document contract requires, and scoring it `fail` is the defect.

## Opinionated, but honest (REQ-§30)

Do not merely document ambiguity. Where research and product principles
provide enough evidence, make a recommendation using the explicit labels
**Recommendation**, **Rationale**, **Alternatives considered**, **Tradeoffs**.
Avoid false neutrality.

But never present a recommendation as a confirmed requirement unless it has
actually been decided. That is the single most damaging failure this pack can
produce, and it is scored BLOCKING.

## Preserve the user's product intent (REQ-§40)

Research is an input to judgment, not authority. Competitor precedent does not
override the user's product strategy. Where the product intentionally differs,
make the difference coherent and say why — do not quietly file it as a
deviation to be corrected.

## References

| File | Use it for |
|---|---|
| [definition-of-done.md](references/definition-of-done.md) | The 16 points, scoring, the `n/a` rule, the `S`/`P` bar, the verdict model, `dod-json`. |
| [discovery-probes.md](references/discovery-probes.md) | The 14 REQ-§45 probes, the pass-C sweep, and the reformatted-PRD test. |
| [anti-requirements.md](references/anti-requirements.md) | Premature visual design, implementation leakage, generic filler, and the severity table. |
| [conceptual-distinctions.md](references/conceptual-distinctions.md) | The 14 REQ-§44 pairs and how each gets collapsed. |

## Path resolution

Reference files resolve through the ladder in each agent's
`## Skills to Load` section: already-in-context, then
`.github/skills/eis-quality-bar/references/<file>`, then
`agent-packs/ux-interaction-spec/skills/eis-quality-bar/references/<file>`,
then `skills/eis-quality-bar/references/<file>` relative to the parent of the
agent directory.
