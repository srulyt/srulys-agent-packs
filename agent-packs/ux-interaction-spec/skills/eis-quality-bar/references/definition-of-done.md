# Definition of Done — the 16-point scoring rubric (REQ-§36)

The critic scores every point on every review round. Scores are `pass`,
`partial`, `fail`, or `n/a`.

## The 16 points

| # | Point | Read from |
|---|---|---|
| 1 | The important user goals are known. | EIS-§3, §10 |
| 2 | Relevant actors are known. | EIS-§4 |
| 3 | The conceptual model is coherent. | EIS-§5 |
| 4 | Terminology is substantially resolved. | EIS-§6 |
| 5 | Permissions are defined or open decisions are explicit. | EIS-§7 |
| 6 | Important lifecycle states are defined. | EIS-§8 |
| 7 | Primary and important alternate flows are documented. | EIS-§10, §13 |
| 8 | Cross-role and backstage workflows are understood. | EIS-§11, §12 |
| 9 | Significant async behavior is specified. | EIS-§11, §13, §14 |
| 10 | Failure and recovery behavior has been considered. | EIS-§15, §16 |
| 11 | Research establishes how the feature fits the host product. | RES-§2, §9 |
| 12 | Relevant competitor conventions have been evaluated. | RES-§3, §5 |
| 13 | Recommendations and requirements are clearly distinguished. | EIS-§19, §20, §22; `decision-log.md` |
| 14 | Blocking questions are resolved. | EIS-§21; `decision-log.md` |
| 15 | Requirements are traceable to the resulting specification. | EIS-§22 |
| 16 | The specification constrains UX behavior without unnecessarily constraining visual design. | EIS-§13, §18 |

## Scoring

- `pass` — the point is met and the evidence for it is on disk.
- `partial` — met in part, or met without the supporting detail a designer
  would need.
- `fail` — not met.
- `n/a` — the point does not apply to this run. Tightly restricted; see below.

## The `n/a` rule

`n/a` is legal **only** for points **11** and **12**, **only** when
`research_mode` is `degraded` or `skipped`, and **only** for the category the
researcher's `Coverage — round N` record in `{stm}/ledger/evidence.md` shows
was not researched:

| Record field | Makes eligible |
|---|---|
| `host_product: none` | point 11 |
| `competitors: 0` | point 12 |

`host_product` is one of `high`, `partial`, `none` (schema:
`eis-document-contracts/references/ledger-format.md`). Only `none` makes point
11 eligible — `partial` and `high` do not, however thin the findings read.

Rules that make this hard to abuse:

- The record is **cumulative for the run**. A top-up round restates the
  totals reached across all previous rounds, so a top-up that only touched
  host-product sources does not reset `competitors` to 0.
- Readers take the **highest** `— round N` record present, because the ledger
  is append-only and earlier rounds still exist.
- **No record at all ⇒ nothing is `n/a`-eligible.** A missing coverage record
  is scored on the documents as written, and separately raises a BLOCKING
  issue for the missing record.
- `research_mode: full` ⇒ nothing is `n/a`-eligible, regardless of the record.
- For `research_mode: skipped` the record's values are pinned to
  `host_product: none; competitors: 0; adjacent: 0`, which is what makes
  `S = 14` on a skipped run true by construction.

Point **14 is never `n/a`**, in any mode.

## The bar

Let `S` = the number of points **scored** (that is, 16 minus the number of
legal `n/a`s) and `P` = the number of points scoring `pass`.

| `research_mode` | `S` | Bar |
|---|---|---|
| `full` | 16 | `P ≥ 14` |
| `degraded` | 15 or 16 | `P ≥ S − 2` |
| `skipped` | 14 | `P ≥ 12` |

## Point 14 in non-interactive runs

Non-interactive runs cannot resolve a blocking question by asking. They are
not excused from point 14 — they are scored on **honesty**:

| What the documents do | Score |
|---|---|
| Names the blocking question, states the default used, labels it as an assumption in EIS-§20, lists it in EIS-§21 and under `## Blocking Questions` | `partial` |
| Presents the assumed answer as a decision, or omits the question | `fail` |
| Resolves it from an input or a prior answer | `pass` |

`n/a` remains illegal for point 14 even here. A non-interactive run that
silently defaults everything scores `fail`, not `n/a`.

## Verdict

| Verdict | Condition |
|---|---|
| `BLOCKING` | at least one BLOCKING issue, **or** any point scores `fail` |
| `CONCERNS` | no BLOCKING issue and no `fail`, but 3 or more `partial`s, or 3 or more CONCERN-level issues |
| `PASS` | no BLOCKING issue, no `fail`, at most 2 `partial`s |

Meeting the `P` bar does not by itself produce `PASS` — a BLOCKING issue
overrides the score every time.

## The `dod-json` block

```dod-json
{
  "research_mode": "full",
  "scored": 16,
  "passed": 14,
  "bar": 14,
  "points": [
    {"n": 1, "score": "pass", "why": "EIS-§3 names four outcomes, each traced to a journey"},
    {"n": 12, "score": "n/a", "why": "Coverage — round 2 records competitors: 0 in degraded mode"}
  ]
}
```

Every `n/a` must cite the coverage record and round that authorises it. An
`n/a` without that citation is itself a BLOCKING issue.
