# Decision log skeleton — Document 3 (verbatim contract)

Source of truth: **REQ-§33**. The six `DL-<heading>` level-2 headings below
are a **verbatim contract**. All six render in every run, including runs where
a heading has no entries.

## The skeleton

```markdown
# [Feature] UX Decision Log

## Confirmed Decisions

### DEC-001 — [Decision]
Status:
Decision:
Rationale:
Evidence:
Implications:

## Recommendations Awaiting Decision

### DEC-002 — [Decision]
Question:
Recommended option:
Alternatives:
Tradeoffs:
Why this matters:

## Blocking Questions

## Non-Blocking Questions

## Assumptions

## Contradictions / Risks
```

The six contract headings, in order:

1. `## Confirmed Decisions`
2. `## Recommendations Awaiting Decision`
3. `## Blocking Questions`
4. `## Non-Blocking Questions`
5. `## Assumptions`
6. `## Contradictions / Risks`

## The five entry fields

Every entry under `## Confirmed Decisions` carries all five fields, in order,
each on its own line:

| Field | Content |
|---|---|
| `Status:` | `Confirmed by user` / `Confirmed in source <REQ-###>` / `Assumed — non-interactive` |
| `Decision:` | The decision itself, stated as behaviour, in one or two sentences. |
| `Rationale:` | Why this over the alternatives. |
| `Evidence:` | `EV-RS-###` / `PAT-###` / `REQ-###` ids, or the literal `None — decided without evidence`. |
| `Implications:` | Which `EIS-§n` sections and which `UX-###` scenarios change because of it. |

Entries under `## Recommendations Awaiting Decision` carry the five fields
`Question:`, `Recommended option:`, `Alternatives:`, `Tradeoffs:`,
`Why this matters:` instead. A recommendation is **never** written with a
`Status:` line — that is what makes it visibly not-yet-decided.

## Empty headings

A heading with no entries renders its body as:

```
None recorded for this run.
```

Never delete the heading, and never write a bare blank body.

## Status honesty

`Status:` is the anti-fabrication field. Rules:

- `Confirmed by user` — only when an answered gate question or an explicit
  statement in an input decided it. Cite the question id (`Q-IN-###`,
  `Q-RS-###`, `Q-MD-###`) or the requirement id.
- `Confirmed in source <REQ-###>` — the input said so directly. Quote or
  paraphrase closely enough that a reader can find it.
- `Assumed — non-interactive` — the run could not ask. This is the **only**
  legal status for an unasked decision, and it is a real status, not a
  synonym for confirmed. In interactive runs it must not appear at all.

Promoting a recommendation to a confirmed decision without a decision event is
a fabrication. The critic's check C-12 fails **BLOCKING** on it.

## Cross-references

- Each `DEC-###` here mirrors a `DEC-MD-###` or `DEC-RS-###` record in
  `{stm}/ledger/decisions.md`. The ledger is append-only and holds the audit
  trail; this document is the reader-facing rendering.
- EIS-§19 (`Confirmed Decisions`) and EIS-§20 (`Assumptions`) in `eis.md` must
  agree with this file. Where they disagree, this file is the one the critic
  reads for check C-12 and `eis.md` is the defect.
- `## Contradictions / Risks` carries every unresolved `CON-###` from
  `{stm}/ledger/context-ledger.md` that survived to delivery, each with the
  two sources it sits between and what it blocks.

## Small features

REQ-§33 allows the decision log to remain a section of the EIS for small
features. This pack **always writes the separate file** so the three
deliverables are uniform across runs and the critic has a stable path to read.
EIS-§19/§20/§21 remain the in-document summary.
