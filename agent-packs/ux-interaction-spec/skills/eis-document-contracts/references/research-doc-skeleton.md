# Research document skeleton — Document 2 (verbatim contract)

Source of truth: **REQ-§32**. The 10 canonical `## <n>. <Title>` level-2
headings below are a
**verbatim contract**. Do not rename, reorder, merge, or drop them — not even
when `research_mode` is `degraded` or `skipped`.

## The skeleton

```markdown
# [Feature] UX Pattern Research

## 1. Research Objective

## 2. Host Product Analysis
### Existing concepts
### Relevant workflows
### Permission conventions
### Interaction conventions
### Terminology
### Constraints

## 3. Competitive Products

### Product A
Observed behavior
Relevant pattern
Strengths
Weaknesses
Applicability

### Product B

## 4. Adjacent Patterns

## 5. Cross-Product Pattern Matrix

| Problem | Host product | Competitor A | Competitor B | Industry pattern |
|---|---|---|---|---|

## 6. Patterns We Recommend Adopting

## 7. Patterns We Recommend Adapting

## 8. Patterns We Recommend Rejecting

## 9. Implications for the EIS

## 10. Sources
```

`### Product A` / `### Product B` are `[repeatable]`: replace them with the
real product names and add one `###` block per product studied, each carrying
the five lines `Observed behavior`, `Relevant pattern`, `Strengths`,
`Weaknesses`, `Applicability`. The six `###` sub-headings under RES-§2 and the
RES-§5 matrix header row are part of the contract.

## The title line

`# [Feature] UX Pattern Research` — substitute the real feature name for
`[Feature]`. The literal `[Feature]` must not survive into the delivered file.

## All ten headings render in every research mode

`research_mode` changes what the **bodies** say, never which headings exist.
This section is the **single source of truth** for the per-mode body form. The
researcher's `## Degradation Protocol` and the orchestrator's research task
prompt both defer to it; if either appears to say something different, this
file wins.

| Mode | What the bodies say |
|---|---|
| `full` | Substantive findings under every heading. |
| `degraded` | Substantive findings where research reached; the skipped-form body (below) under every heading it did not reach, each carrying its own `EV-GAP-###` ids. |
| `skipped` | The skipped-form body under every heading. RES-§1 still states the objective; RES-§9 and RES-§10 still render their required content (below). |

### The `skipped` declaration

When `research_mode` is `skipped`, `{out}/ux-pattern-research.md` opens
immediately under the title with a **verbatim** block:

```markdown
> **research_mode: skipped** — no external or host-product research was
> performed for this run. Every pattern claim below is unresearched. The EIS
> must not present any interaction choice as precedent-backed.
```

The literal token `research_mode: skipped` must appear in the file.

### The skipped-form body — verbatim

Each unresearched heading's body is this line, followed by the `EV-GAP-###`
ids naming what would have been verified there:

```
Not performed — research_mode: skipped (<reason from state.json>).
EV-GAP-004, EV-GAP-005
```

Both parts are required. `<reason from state.json>` is the run's actual reason
— `user requested skipped`, `no web tool available`, and so on — never the
literal angle-bracket text. **The trailing `EV-GAP-###` ids are not optional:**
critic check C-7 fails **BLOCKING** when an unresearched heading carries prose
with no gap ids behind it, because a heading that merely says "not performed"
does not record *what* went unverified.

In `degraded` mode the same body form is used, with
`research_mode: degraded (<reason>)` substituted, on the headings that were not
reached. Headings that were reached are written normally.

### Sections 9 and 10 are never declared-empty

Two headings carry required content in **every** mode:

- **RES-§9** still renders the REQ-§25 matrix. In `skipped` mode it renders the
  column header row, plus one data row for each decision area the analyst's
  research brief named, with every precedent cell set to
  `Unverified — EV-GAP-0nn` and every Recommendation demoted to *Assumption for
  the author*. Each such row is backed by a `PAT-###` record with
  `verdict: context-only` (see `ledger-format.md`). If the brief named no
  decision areas, RES-§9 renders the **header row alone, with no data rows** —
  that is a legitimate outcome and not a vacuity finding.
- **`## 10. Sources`** (`RES-§10`) lists the supplied material the run did
  have — host product documents the user provided — or, when there was none,
  the literal `No sources — research skipped`.

A `skipped` run still writes a `Coverage — round N` record to
`{stm}/ledger/evidence.md` with the pinned values
`host_product: none; competitors: 0; adjacent: 0` (see `ledger-format.md`).
Those pinned values are what make the critic's Definition-of-Done denominator
`S = 14` true by construction rather than by assumption.

## Non-vacuity

Rendering the headings is not research. Every **data** row in RES-§9 and every
verdict in RES-§6/§7/§8 must have a matching `PAT-###` record in
`{stm}/ledger/evidence.md`. The critic's check C-10 fails **BLOCKING** with
rule `§5 — pattern verdicts not recorded` when the ledger holds zero `PAT-###`
records while RES-§9 renders at least one **data** row, or while
`research_mode` is `full`.

**The header row is not a data row.** A `skipped` run whose RES-§9 is the
column header alone, with no data rows and no `PAT-###` records, does not trip
the floor — there is nothing being claimed. A `skipped` run that *does* render
data rows must back each with a `context-only` `PAT-###` record, and the floor
applies normally.

## Sources

RES-§10 lists every source with enough information to verify it: product or
document name, the specific surface or page, how it was reached, and the date
observed. A source that cannot be re-checked from what is written is not a
source — record the underlying claim as an `EV-GAP-###` instead.

**Each entry reproduces the source's own stated identifier verbatim** — its
title, publication or system name, URL, and document, memo or version number,
exactly as the material writes them. Where the material arrived inside a
supplied bundle, the bundle filename and section are recorded *in addition*,
as the locator; they never stand in for the identifier. One entry per
constituent document, never one entry for the bundle. The identifiers here are
the same ones the body sections cite, so the two must agree — see
`ux-research-method/references/evidence-discipline.md § Reproduce the source's
own identifier`, which owns this rule.
