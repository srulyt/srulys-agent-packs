---
name: eis-document-contracts
description: "The verbatim document contracts for the ux-interaction-spec pack: the 22-section EIS skeleton, the 10-section UX pattern research skeleton, the 6-section decision log skeleton, the five fixed matrices, the twelve-field interaction contract, Mermaid diagram conventions, the question format, the output-location protocol, and the short-term-memory ledger schemas. Load when materialising, filling, or auditing any of the three deliverables. Keywords: EIS skeleton, section contract, research document, decision log, traceability matrix, capability matrix, assumptions table, interaction contract, ledger, output location."
---

# EIS document contracts

This skill owns **shape**. What goes *in* the shape is owned by
`interaction-modeling` (behaviour), `ux-research-method` (evidence), and
`eis-quality-bar` (whether it is good enough).

## Notation — read this first

A bare `§17` is ambiguous and is a defect in any artifact this pack produces.
Always qualify:

| Notation | Namespace | Example |
|---|---|---|
| `REQ-§n` | A section of the user's requirements document (46 sections). | `REQ-§31` defines the EIS skeleton. |
| `EIS-§n` | A level-2 heading of Document 1, the EIS (22 of them, from REQ-§31). | `EIS-§7` is `## 7. Permissions and Capabilities`. |
| `RES-§n` | A level-2 heading of Document 2, the research doc (10 of them, from REQ-§32). | `RES-§9` is `## 9. Implications for the EIS`. |
| `DL-<heading>` | A level-2 heading of Document 3, the decision log (6 of them, from REQ-§33). | `DL-Confirmed Decisions`. |
| `Q-IN-###` / `Q-RS-###` / `Q-MD-###` | Questions raised during intake / research / modeling. | `Q-MD-007` |

## The three deliverables

| Doc | File | Headings | Contract |
|---|---|---|---|
| 1 | `{out}/eis.md` | 22 `EIS-§n` | [eis-skeleton.md](references/eis-skeleton.md) |
| 2 | `{out}/ux-pattern-research.md` | 10 `RES-§n` | [research-doc-skeleton.md](references/research-doc-skeleton.md) |
| 3 | `{out}/decision-log.md` | 6 `DL-<heading>` | [decision-log-skeleton.md](references/decision-log-skeleton.md) |

All three render **every** heading on **every** run. Research mode, feature
size, and degraded inputs change what the bodies say, never which headings
exist.

## Two file disciplines

- **`{out}/eis.md` is skeleton-first, fill-in-place.** Pass A materialises all
  22 headings with sentinel bodies before writing any content; later passes
  edit those bodies in place. `eis.md` is **never** appended to. Appending is
  how sections end up out of contract order.
- **Every `{stm}/ledger/*.md` is append-only.** Never rewrite, re-sort, or
  delete a ledger line. Corrections append a superseding record. Because
  ledgers keep old rounds, every reader of a `— round N` record takes the
  **highest** `N` present.

## Sentinels

An unfilled EIS body carries both:

```markdown
<!-- EIS-PENDING: pass C -->
_Pending — pass C._
```

Pass D must leave zero sentinels. `EIS-§12` and `EIS-§17` are *conditionally
substantive*: when they do not apply, the body reads
`Not applicable — <reason>` — a filled body, never a sentinel.

## References

| File | Use it for |
|---|---|
| [eis-skeleton.md](references/eis-skeleton.md) | The 22 verbatim EIS headings, pass ownership, stub form, conditional sections. |
| [research-doc-skeleton.md](references/research-doc-skeleton.md) | The 10 verbatim RES headings, the `research_mode: skipped` declaration, non-vacuity. |
| [decision-log-skeleton.md](references/decision-log-skeleton.md) | The 6 verbatim DL headings and the five entry fields. |
| [matrices.md](references/matrices.md) | Capability (EIS-§7), cross-product (RES-§5), evidence-to-recommendation (REQ-§25), traceability (EIS-§22), assumptions (EIS-§20). |
| [interaction-contract.md](references/interaction-contract.md) | The twelve-field EIS-§13 scenario shape and the `UX-ACCESS-03` worked example. |
| [diagrams.md](references/diagrams.md) | Which Mermaid diagram belongs to which section, and syntax hygiene. |
| [question-format.md](references/question-format.md) | The `open-questions` block, gates, and the importance value test. |
| [output-location.md](references/output-location.md) | Where deliverables go, the `location-proposal` block, write-once. |
| [ledger-format.md](references/ledger-format.md) | Every `{stm}/ledger/*.md` record schema, the highest-round rule, and what is persisted versus in-block only. |

## Path resolution

Reference files resolve through the ladder in each agent's
`## Skills to Load` section: already-in-context, then
`.github/skills/eis-document-contracts/references/<file>`, then
`agent-packs/ux-interaction-spec/skills/eis-document-contracts/references/<file>`,
then `skills/eis-document-contracts/references/<file>` relative to the parent
of the agent directory.
