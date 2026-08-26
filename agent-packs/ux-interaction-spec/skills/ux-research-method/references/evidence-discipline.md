# Evidence discipline (REQ-§4)

Research supports product reasoning. It is not decoration.

## The three categories — never blurred

| Category | Definition | How it is written |
|---|---|---|
| **Observed fact** | Directly supported by a reliable source. | `EV-RS-###` with source and date. |
| **Inference** | A conclusion drawn from observed behavior or documentation. | Prefixed `Inference:` with the reasoning chain and the `EV-RS-###` it rests on. |
| **Recommendation** | A proposed behavior for the product being specified. | Labelled **Recommendation** with **Rationale**, **Alternatives considered**, **Tradeoffs**. |

Writing an inference as an observation is the most common research failure and
the hardest to detect downstream, because by the time the author reads it,
the hedge is gone.

## Source tiers

Prefer primary sources, in this order:

1. official product interfaces
2. official product documentation
3. official help centers
4. official API or permission documentation
5. official product videos or demos
6. credible secondary sources
7. community discussions, where they help explain actual customer expectations

Record the tier on each `EV-RS-###`. A tier-7 source is legitimate evidence
**about what customers expect**; it is weak evidence about what a product
does. Do not use a forum post to establish product behaviour when tiers 1–4
were not attempted.

## Recording a source

Every source carries enough to verify it: product or document name, the
specific surface or page, how it was reached, and the date observed —
"observed 2026-08-25". Include URLs when available. Behaviour changes; a
citation without a date cannot be audited later.

The `source` field records the material's **own stated identifier**, verbatim,
not your description of it — see `## Reproduce the source's own identifier`
below. A ledger record that says "the product's approval documentation" cannot
be re-checked any more than a body claim that says it.

If a source cannot be re-checked from what is written, it is not a source.
Record the underlying claim as an `EV-GAP-###` instead.

## Citing in the document body

An `EV-RS-###` is a **pointer into your own ledger, not a citation**. A reader
of `{out}/ux-pattern-research.md` has not read your ledger. A body sentence
that ends in `` (`EV-RS-001`) `` and nothing else tells that reader only that
*some* evidence exists; it does not tell them *what* was consulted, and it
forces them to cross-reference `RES-§10` to find out — which cannot work when
`RES-§10` cites a whole bundle in one line.

**Every claim in the body names its source in human-readable form alongside the
ledger id.** The identity is whatever a reader would use to find the material
again: the document or article title, the page/section or memo identifier, a
URL when there is one, and the date.

```markdown
Sharing is limited to members of the owning workspace (Help Centre article
"Sharing a dashboard", `help.example.com/dashboards/sharing`, published
2025-06-12 — `EV-RS-004`).

The export API caps a job at 10,000 rows and does not paginate beyond the
first page (Engineering memo `ENG-2025-081`, 2025-09-03 — `EV-RS-011`).
```

Not this:

```markdown
The decision-critical object vocabulary is requester, data product, requested
permission level, and business justification (`EV-RS-004`, `EV-RS-011`).
```

The first reference to a source **within a section** carries the full identity.
Later references in that same section may use the bare id. A section that
mentions a source only by id is not correctly attributed, even when the id
resolves cleanly in the ledger.

This applies to **every** narrative section — `RES-§2` Host Product Analysis
most of all, because that is where supplied first-party material lands and
where an unattributed claim is indistinguishable from an assertion.

## Reproduce the source's own identifier — do not paraphrase it

This rule is separate from the one above and is the one most often missed.

Material almost always states **who it is and where it lives**: a `Source:`
line, a masthead, a publication or system name, an article or page title, a
URL, a document, memo or version number. When it does, **reproduce those
tokens exactly as the material writes them.** Your own description of the
material is not its identifier.

| The material says | Write | Never write |
|---|---|---|
| `Source: Vendor Support Centre, article help.example.com/sharing` | Vendor Support Centre article `help.example.com/sharing` | "the product's current sharing documentation" |
| `Source: Engineering, internal memo ENG-2025-081` | Engineering memo `ENG-2025-081` | "an internal engineering note" |
| `Source: Northwind Interface Guidelines (internal), v4.2` | Northwind Interface Guidelines v4.2 | "the internal interface guidance" |

A paraphrase reads like a citation and does none of its work. "The product's
current approval-flow documentation" cannot be looked up, cannot be
distinguished from a second document about the same topic, and cannot be
checked by anyone who does not already have the bundle open. The identifier
can.

**Mode-independent.** This is not a degraded-mode rule. It applies in `full`,
`degraded` and `skipped` alike, and to host-product, competitor and adjacent
material equally. The only thing that changes by mode is how many sources
there are to identify.

### Supplied bundles: the filename is a locator, not an identifier

When the source is a supplied input bundle, the bundle's filename and section
number tell a reader **where you found it**. They do not tell them **what it
is** — the bundle is the container, and the source is the constituent document
inside it. Cite both:

```markdown
Exports older than 90 days are purged without notice (Vendor Support Centre
article "Export retention", `help.example.com/exports/retention`, published
2024-03-19; supplied bundle §1, observed 2026-08-25 — `EV-RS-001`).
```

Citing only the bundle filename and a section number is the failure this rule
exists to prevent: every claim in the document then carries the same
provenance string, the distinct sources inside the bundle become
indistinguishable, and a reader cannot tell a support-centre article from an
engineering memo.

If the material genuinely states no identifier of its own — an untitled note,
an unattributed extract — say so explicitly (`no stated identifier; supplied
bundle §3`) rather than substituting a description that reads like one.

**Self-check before returning:** read each body section as though you had never
seen the ledger **and did not have the bundle**. If you cannot tell which
supplied document a claim came from, or could not ask someone else to fetch it
from what you wrote, the attribution is incomplete. `RES-§10` carries the same
identifiers, so the two must agree.

## Never claim without evidence

Do not state that a product behaves in a particular way without evidence. When
evidence cannot be obtained, the honest output is an `EV-GAP-###`:

```markdown
### EV-GAP-004 — no public evidence on approval SLAs
kind: gap
category: host-product
reason: unpublished-internal
attempted: ["vendor docs", "public help centre", "release notes"]
consequence: "EIS-§14 timing guidance is an assumption, not a precedent"
```

`category` is one of `host-product`, `competitor`, `adjacent` — **which
research area the gap falls in**. The critic reads it to decide which
Definition-of-Done point is `n/a`-eligible (`host-product` → point 11,
`competitor` → point 12); a gap with no `category`, or with a value outside
this set, is treated as **not recorded**.

`reason` is one of `unpublished-internal`, `paywalled`,
`no-comparable-product`, `search-unavailable`, `time-boxed-out` — **why** the
claim could not be evidenced. It is descriptive and never substitutes for
`category`.

`consequence` names what downstream must now treat as unevidenced. A gap
record with no consequence does no work.

## Conflicting sources

If sources conflict, note the conflict. Do not average them, do not pick the
convenient one, and do not quietly prefer the more recent one without saying
that recency was the tiebreak.

```markdown
### EV-RS-019 — conflicting evidence on invitation expiry
kind: observed
sources:
  - product docs (2025-11), "invitations expire after 7 days", tier 2
  - in-product help text (observed 2026-08-25), "invitations do not expire", tier 1
claim: CONFLICT — expiry behaviour is not established
resolution: unresolved; raised as Q-RS-003
```

A conflict that reaches the EIS unresolved appears under `## Contradictions /
Risks` in `decision-log.md`.

## Research modes

| Mode | Meaning |
|---|---|
| `full` | External and host-product research performed. |
| `degraded` | Research attempted but reached only part of the intended scope. Every unreached area has an `EV-GAP-###`. |
| `skipped` | No research performed — either requested by the user or no research tool was available. |

The mode is declared in the researcher's `research-summary` block, recorded in
the cumulative `Coverage — round N` record, and, for `skipped`, declared
verbatim at the top of `{out}/ux-pattern-research.md`.

A degraded or skipped run is a legitimate outcome. **A degraded run that
presents itself as full is not** — it is the failure this discipline exists to
prevent.

## Vacuity

Rendering the RES headings is not research. If `{stm}/ledger/evidence.md`
holds zero `PAT-###` records while RES-§9 renders at least one **data** row, or
while `research_mode` is `full`, the critic fails check C-10 **BLOCKING** with
rule `§5 — pattern verdicts not recorded`. The block was emitted; the work was
not done.

**Carve-out.** The RES-§9 column header row is not a data row. A `skipped` run
that renders the header alone, with no data rows and no `PAT-###` records, is
not vacuous — it is honest. A `skipped` run that renders data rows must back
each with a `PAT-###` record carrying `verdict: context-only`. See
`eis-document-contracts/references/research-doc-skeleton.md`, which owns this
rule.
