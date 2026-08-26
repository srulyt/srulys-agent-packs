# Core objective coverage — the 16 things every run must determine (REQ-§1)

Given arbitrary product context, determine and document:

| # | Objective | Answered in |
|---|---|---|
| 1 | Who the actors are. | EIS-§4 |
| 2 | What concepts and objects users interact with. | EIS-§5 |
| 3 | What users are trying to accomplish. | EIS-§3, §10 |
| 4 | What actions are available. | EIS-§7, §13 |
| 5 | Under what conditions actions are available. | EIS-§7, §8 |
| 6 | Who has permission to perform each action. | EIS-§7 |
| 7 | What states the relevant objects can occupy. | EIS-§8 |
| 8 | How those states transition. | EIS-§8 |
| 9 | How users move through important journeys. | EIS-§10 |
| 10 | What happens behind the scenes during those journeys. | EIS-§11, §12 |
| 11 | What the system communicates to users. | EIS-§14 |
| 12 | What happens during failure, partial completion, cancellation, retry, expiration, or conflicting actions. | EIS-§15, §16 |
| 13 | How the feature should fit the UX conventions of the product it is built in. | RES-§2, EIS-§18 |
| 14 | What conventions users will already know from competing or adjacent products. | RES-§3, §4, §5 |
| 15 | Which interaction decisions are requirements versus recommendations versus assumptions. | EIS-§19, §20, §22 |
| 16 | Which important questions remain unresolved. | EIS-§21 |

## The pass-D sweep

At pass D, walk all sixteen in order and mark each:

- `answered` — with the `EIS-§n` (or `RES-§n`) section that answers it;
- `not-applicable` — with a one-sentence reason grounded in this feature;
- `unanswered` — it applies, and the documents do not answer it.

Write the sweep to `{stm}/ledger/coverage.md` under
`## Pass D — core_objective_unanswered` as a 16-row table
(`# | Objective | Status | Where`), and mirror it into
`coverage-json.core_objective_unanswered`.

**Record every objective, including the answered ones.** The field name says
"unanswered" because that is what the critic looks for, but a table containing
only the unanswered rows is indistinguishable from a table nobody filled in.

## Why it is written to disk

The critic cannot read the author's fenced output block. Check C-14 reads
`{stm}/ledger/coverage.md § Pass D — core_objective_unanswered` (highest
round) and can fail three distinct ways, all BLOCKING:

| Rule | When |
|---|---|
| `§1 — coverage sweep not recorded` | the section is missing, or has fewer than 16 rows |
| `§1 — silent drop` | an objective is marked `answered` but the cited section does not answer it |
| `§1 — false completeness` | every objective is marked `answered` while EIS-§21 lists blocking open questions that bear on one of them |

A missing sweep is never scored `pass`.

## `unanswered` is a legitimate outcome

An objective that genuinely cannot be answered on the available context is
marked `unanswered`, gets a `Q-MD-###`, appears in EIS-§21, and — if it
blocks — appears under `## Blocking Questions` in `decision-log.md`. That is
an honest result. Marking it `answered` to make the table look complete is the
`silent drop` failure.

## `not-applicable` needs a reason

> 12. failure, partial completion, cancellation, retry — **not-applicable**?

Almost never. Objective 12 applies to any feature with a state model. Reasons
that pass: "this feature is a read-only view with no user-initiated
operations". Reasons that do not: "not relevant", "out of scope", "the input
does not mention it". The input not mentioning it is precisely why the sweep
exists.
