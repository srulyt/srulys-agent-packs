# EIS skeleton — Document 1 (verbatim contract)

Source of truth: **REQ-§31, Document 1**. The 22 level-2 headings below are a
**verbatim contract**. Do not rename, reorder, merge, split, or "improve" them.
Do not add level-2 headings. Sub-headings marked `[repeatable]` may be repeated
or renamed to the real object/journey/scenario; all other `###` sub-headings
are part of the contract.

## Two notations — never interchangeable

This pack uses two different notations for the same section, and confusing them
corrupts the document:

| Notation | Example | Where it is legal |
|---|---|---|
| **Heading literal** | `## 8. State Models` | The `##` line in `eis.md`. **Always** copied verbatim from the skeleton block below. |
| **Reference shorthand** | `EIS-§8` | Prose, cross-references, ledgers, pass-ownership tables, `sections_filled`, `lands_in`, and envelope JSON. **Never** written into `eis.md` as a heading. |

**The string `EIS-§` must never appear on a `##` line.** A heading such as
`## EIS-§8 State Models` is a contract violation even though the title is
correct — the canonical form is `## 8. State Models`.

Where this file and the pass guide name a section as `EIS-§8` *State Models*,
the sigil is the reference id and the words are the human title. They are two
separate things printed next to each other for readability; they are **not** a
heading you can paste. The only text you may paste as a heading is the text
inside the fenced skeleton block under "The skeleton" below.

## How the author uses this file

1. **Pass A materialises the whole skeleton first.** **Copy the fenced skeleton
   block below verbatim** into `{out}/eis.md` before writing any content —
   copy the heading lines, never retype or reconstruct them from the pass
   tables. This file is **skeleton-first, fill-in-place** — after pass A the
   file is never appended to, only edited in place.
2. Every unfilled body carries **both** sentinels:
   `<!-- EIS-PENDING: pass X -->` and `_Pending — pass X._`
   The HTML comment is the machine-readable marker; the italic line is what a
   human sees. Both are removed when the section is filled.
3. **Pass D must leave zero sentinels.** `pass-summary.placeholders_remaining`
   must be `[]`.
4. **Pass A self-check before returning.** Re-read the `^## ` lines of
   `{out}/eis.md` and confirm each one begins with a bare number and a period
   (`## 1.` … `## 22.`) and that **none** contains `EIS-§`. If any heading
   carries the sigil, rewrite that heading from the skeleton block before you
   return. Every later pass edits bodies only and must leave headings untouched.

## Pass ownership

Reference shorthand only — these are ids, not headings.

| Pass | Fills |
|---|---|
| A | EIS-§2, §3, §4, §5, §6, §7 |
| B | EIS-§8, §9, §10, §11, §12, §13 |
| C | EIS-§14, §15, §16, §17, §18 |
| D | EIS-§1, §19, §20, §21, §22 |

## Conditional sections

`EIS-§12` (*Service Blueprint*) and `EIS-§17` (*Accessibility / Localization
Considerations*) are **conditionally substantive**, never conditionally
present. Their headings remain exactly `## 12. Service Blueprint` and
`## 17. Accessibility / Localization Considerations`. If the feature genuinely
does not warrant one, the heading still appears and the body reads:

```
Not applicable — <one-sentence reason grounded in this feature>.
```

A `Not applicable — …` body is a *filled* body. It is **never** left as a
sentinel, and `Not applicable` on its own with no reason is a defect.

## The skeleton

```markdown
# [Feature] Experience Interaction Specification

## 1. Executive Summary

## 2. Scope
### In Scope
### Out of Scope
### Dependencies

## 3. Experience Goals
### User Outcomes
### Business Outcomes
### Design Principles
### Design Invariants

## 4. Actors and Roles

## 5. Conceptual Model
### Objects
### Relationships
### User-facing vs implementation concepts

## 6. Terminology

## 7. Permissions and Capabilities
### Capability Matrix
### Permission Rules
### Inheritance / Overrides / Expiration

## 8. State Models
### [Object A]
### [Object B]

## 9. Entry Points and Discovery

## 10. User Journeys
### Journey 1
### Journey 2

## 11. Business / System Workflows

## 12. Service Blueprint

## 13. Interaction Scenarios
### UX-001
### UX-002

## 14. System Feedback and Notifications

## 15. Error and Recovery Behavior

## 16. Edge Cases

## 17. Accessibility / Localization Considerations

## 18. UX Requirements for Design Handoff

## 19. Confirmed Decisions

## 20. Assumptions

## 21. Open Questions

## 22. Requirements Traceability
```

`### [Object A]` / `### [Object B]` (under `EIS-§8`), `### Journey 1` /
`### Journey 2` (under `EIS-§10`) and `### UX-001` / `### UX-002` (under
`EIS-§13`) are `[repeatable]`: replace them with the real object names, real
journey names, and the real `UX-###` scenario ids, and add as many as the
feature needs. Never delete the parent level-2 heading.

## Worked stub form (what pass A writes)

```markdown
## 14. System Feedback and Notifications

<!-- EIS-PENDING: pass C -->
_Pending — pass C._
```

## The title line

`# [Feature] Experience Interaction Specification` — substitute the real
feature name for `[Feature]`, keeping the trailing words verbatim. The literal
placeholder `[Feature]` must not survive into the delivered document.

## Ordering rule

A structural check reads `{out}/eis.md`, extracts every `^## ` line, and
compares the resulting list to the 22 headings above **as an ordered
sequence**. A heading that is present but out of order is a failure, the same
as a missing heading.

The comparison is **exact string equality** against the skeleton block. It is
not a fuzzy or title-only match: `## 8. State Models` passes, and
`## EIS-§8 State Models`, `## Section 8 — State Models` and `## 8 State Models`
all fail, because the heading is the contract, not merely the title it carries.
