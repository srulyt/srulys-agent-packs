# Synthesis and precedent (REQ-§5, §40)

The objective is not a competitive-analysis report. Research must **influence
the interaction specification**, or it should not have been done.

## The six synthesis questions

For each meaningful external pattern, answer all six:

1. Should we adopt this convention?
2. Adapt it?
3. Reject it?
4. Is it only relevant context?
5. Would customers likely recognize it?
6. Does it conflict with conventions in the host product?

Questions 1–3 resolve to the `PAT-###` `verdict` field — `adopt`, `adapt` or
`reject` — which renders under RES-§6, RES-§7 or RES-§8. Question 4 is a
filter, not a fourth verdict: a pattern that is only relevant context stays out
of the RES-§5 matrix. It is **not** the same as the fourth verdict value,
`context-only`, which is the *degradation* verdict — a pattern that would have
earned one of the first three but could not be evidenced well enough, rendered
as an unverified RES-§9 row. The closed set is therefore `adopt`, `adapt`,
`reject`, `context-only`; in `degraded` and `skipped` modes — the modes this
pack most often runs in — `context-only` is the only verdict available for an
unevidenced pattern, so a three-value reading of this section strands the run.
Question 5 feeds the `familiarity` axis; question 6 feeds `host-consistency`.

## Precedence rule

Prefer the host product's established mental model over a competitor's unless
there is a strong reason to change. When host-product and industry conventions
conflict, **explicitly surface the tradeoff** — do not resolve it silently.

The surfacing goes in three places:

- RES-§9, as an implication with both options named;
- a `Q-RS-###` in `open-questions`, with the default that will be used;
- `## Recommendations Awaiting Decision` in `decision-log.md` if it survives
  to delivery undecided.

## 9. Implications for the EIS (`RES-§9`)

This is the load-bearing section. It is where research stops being a document
and starts being a specification input. Each implication names:

| Field | Content |
|---|---|
| The decision area | Phrased as the problem, not the feature. |
| The evidence | `EV-RS-###` and `PAT-###` ids. |
| The implication | Which `EIS-§n` sections must now say what. |
| The confidence | `evidenced`, `inferred`, or `assumed`. |

Render it as the REQ-§25 five-column matrix, whose columns are pinned verbatim
in `eis-document-contracts/references/matrices.md § 3`:

`Decision area | Host product precedent | External precedent | Recommendation | Rationale`

so the author and the critic read the same shape.

An implication with no `EIS-§n` target is not an implication. Delete it or
give it one.

## Preserve the user's product intent (REQ-§40)

Research is an input to judgment, not authority.

The goal is **not**:

> Make our product behave exactly like competitors.

The goal is:

> Understand the mental models users bring with them, then consciously decide
> where to align and where to differ.

Where the proposed product intentionally differs from existing products, the
job is to make that distinction **coherent** — to say what the difference
buys, what mental model it breaks, and what the product must therefore do to
teach the new model. Deliberate divergence recorded with its cost is good
design. Deliberate divergence recorded as a deviation to be corrected is
research overreaching its authority.

When an input states a product strategy that conflicts with every precedent
found, the correct output is:

> Every product studied does X. This product's stated objective (`REQ-007`)
> requires Y. Y is therefore a deliberate divergence, and EIS-§9 must carry
> the discovery burden that X would otherwise have carried for free.
> `PAT-011`, verdict `reject`.

Not:

> Recommend adopting X, consistent with the market.

## Deferred answers

The author may send `research-requests` mid-run. Answer them in the
`deferred-answers-json` block, each carrying the requesting id, the answer,
and the `EV-RS-###` or `EV-GAP-###` that backs it. An unanswerable request
gets an explicit `EV-GAP-###` — never an empty answer and never silence.

## Top-ups

A research top-up is a **narrow** round: it answers specific requests and adds
the evidence they need. Its `Coverage — round N` record still restates the
cumulative totals for the whole run, so a top-up that touched only host-product
sources does not appear to have researched zero competitors. The record's
`mode` field stays the run's underlying `research_mode` (`full`, `degraded` or
`skipped`) — `top-up` is how you were invoked, never a coverage mode. Top-ups
have a ceiling of 2 per run; the ceiling is a stop, not a quota to spend.
