# Ledger formats — short-term memory schemas

Every ledger lives under `{stm}/ledger/` where `{stm}` is
`.ux-interaction-spec-stm/runs/{session-id}/`.

**All ledgers are append-only.** Never rewrite, re-sort, deduplicate, or
delete an existing ledger line. Corrections are appended as a new record that
supersedes the old one and says so. (`{out}/eis.md` is the opposite: it is
skeleton-first and filled in place, never appended to.)

## The highest-round rule

Several ledger records are written once per review round and carry a
`— round N` suffix. Because the ledgers are append-only, **round 1's record
still exists after round 2 is written**. Every reader of a round-suffixed
record — the critic, the orchestrator's review task prompt, and any sweep —
must select the record with the **highest** `N` present in the file, not the
first match, not the last line, and never a merge across rounds.

## Ledger inventory

| File | Owner (append) | Readers |
|---|---|---|
| `context-ledger.md` | `eis-context-analyst` | author, critic |
| `requirements.md` | `eis-context-analyst` | author, critic |
| `evidence.md` | `ux-pattern-researcher` | author, critic |
| `coverage.md` | `eis-author` | critic |
| `decisions.md` | `eis-author`, `ux-pattern-researcher` | critic |
| `questions.md` | `eis-context-analyst`, `ux-pattern-researcher`, `eis-author` | orchestrator, critic |

`questions.md` is the one ledger with three appending owners: each specialist
appends the `Q-IN-###` / `Q-RS-###` / `Q-MD-###` records it raised. The
orchestrator **reads** it but does not write it — the answers it collects go to
`{stm}/context/answers.md`, which is orchestrator-owned and is not a ledger.

## ID namespacing (collision-free by construction)

Each prefix has exactly one writing agent, and all runs are sequential, so no
ID coordination protocol is needed. A record whose prefix is written by an
agent other than its owner below is a defect.

| Prefix | Owner | Meaning |
|---|---|---|
| `REQ-###` | analyst | Extracted input requirement (frozen after `analyze`) |
| `CON-###` | analyst | Contradiction between supplied artifacts |
| `PROP-###` | analyst | Supplied UX concept, treated as a proposal |
| `VIS-###` | analyst | Visual hint lifted out of an input, with its behavioural content |
| `EV-RS-###` | researcher | Evidence record |
| `EV-GAP-###` | researcher | Named unverifiable gap |
| `PAT-###` | researcher | Pattern verdict (adopt / adapt / reject / context-only) |
| `DEC-RS-###` | researcher | Research-derived recommendation |
| `DEC-MD-###` | author | Modeling decision |
| `DRV-###` | author | Derived requirement introduced by analysis |
| `UX-###` | author | Interaction scenario / contract |
| `RQ-###` | author | Research top-up request |
| `Q-IN-### / Q-RS-### / Q-MD-###` | analyst / researcher / author | Question raised by that agent |
| `BLK-### / CNC-###` | critic | Blocking issue / concern |

`VIS-###` is **analyst-owned**. The rewrite move in
`eis-quality-bar/references/anti-requirements.md` describes what a `VIS-###`
captures, but the agents that load that file — author, researcher, critic —
cannot write `context-ledger.md`. The record is created at intake by
`@eis-context-analyst` (see
`interaction-modeling/references/input-triage.md`); everyone else reads it.

---

## 1. `context-ledger.md` — analyst

One record per finding. Record kinds: `CON-###` (conflict), `PROP-###`
(proposal found in an input), `visual-hint` (a visual/UI detail lifted out of
an input so it is not silently promoted into the EIS).

```markdown
### CON-003 — pending-request count contradicts between sources
kind: conflict
sources: [inputs/product-requirements.md §4, inputs/operations-notes.md §2]
statement_a: "a user may hold at most 3 pending requests"
statement_b: "there is no cap on pending requests"
blocks: EIS-§7, EIS-§8
resolution: unresolved
```

```markdown
### PROP-002 — auto-approve requests under 24h duration
kind: proposal
source: inputs/product-requirements.md §6
proposed_by: source-document
status: not-yet-evaluated
```

```markdown
### VIS-001 — "a modal with two tabs"
kind: visual-hint
source: inputs/design-brief.md §3
behavioural_content: "user chooses between duration-based and ticket-based justification"
verdict: layout-detail-withheld
```

`PROP-###` records are what the author's `proposals_evaluated` sweep in
`coverage.md` is audited against (critic check C-12).

---

## 2. `requirements.md` — analyst

One record per extracted requirement.

```markdown
### REQ-014 — approver must see the requester's current access
kind: functional
source: inputs/product-requirements.md §5
verbatim: "Approvers need to know what the requester can already do."
confidence: stated
```

`kind` is one of `functional`, `constraint`, `business-rule`,
`technical-limit`, `governance`, `success-criterion`, `non-goal` — a closed
seven-value set, matching the analyst's own prompt. Records with
`kind: governance` are exactly the set the critic's check C-11 audits against
the author's `governance_map`, so a mis-tagged record is an unenforced
requirement.

`confidence` is one of `stated` (the input says it), `implied` (it follows
from what the input says), `inferred` (the analyst concluded it). Never
upgrade a confidence level.

---

## 3. `evidence.md` — researcher (**append-only**)

Record kinds: `EV-RS-###` (observed fact), `EV-GAP-###` (a claim that could
not be evidenced), `PAT-###` (a cross-product pattern verdict),
`Coverage — round N` (one per research round).

```markdown
### EV-RS-007 — GitHub org invitations expire after 7 days
kind: observed
source: https://docs.github.com/... (org invitations), observed 2026-08-25
tier: 2
claim: "invitations expire after 7 days and can be resent"
```

```markdown
### EV-GAP-004 — no public evidence on approval SLAs
kind: gap
category: host-product
reason: unpublished-internal
attempted: ["vendor docs", "public help centre", "release notes"]
consequence: "EIS-§14 timing guidance is an assumption, not a precedent"
```

`category` is one of `host-product`, `competitor`, `adjacent` — **which
research area the gap falls in**. This is the field the critic reads to decide
which Definition-of-Done point is `n/a`-eligible (`host-product` → point 11,
`competitor` → point 12), so an `EV-GAP-###` with no `category`, or with a
value outside this set, is treated as **not recorded**.

`reason` is one of `unpublished-internal`, `paywalled`,
`no-comparable-product`, `search-unavailable`, `time-boxed-out` — **why** the
claim could not be evidenced. It is descriptive: no check branches on it, and
it never substitutes for `category`.

### `PAT-###` — pattern verdict

```markdown
### PAT-005 — time-bounded elevation with automatic revocation
verdict: adopt
res_section: RES-§6
matrix_row: "How does access end?"
evidence: [EV-RS-007, EV-RS-011]
axes_considered: [familiarity, cognitive-load, scalability, reversibility, discoverability, admin-burden, error-risk, host-consistency, strategic-fit]
axes_rationale: |
  familiarity: matches the host product's existing token expiry mental model.
  cognitive-load: one duration choice, no separate revoke step.
  scalability: removes the manual-cleanup backlog at 10k+ grants.
  reversibility: expiry is the reversal; re-request is cheap.
  discoverability: expiry date shown on the grant row.
  admin-burden: falls to near zero versus periodic access reviews.
  error-risk: over-granting self-heals; under-granting is a re-request.
  host-consistency: consistent with existing PAT tokens.
  strategic-fit: supports the stated least-privilege objective.
```

`verdict` is one of `adopt`, `adapt`, `reject`, `context-only`.
`context-only` is the degradation verdict: a pattern that informs the
specification but could not be evidenced well enough to adopt, adapt or reject
— it is what the researcher emits for affected verdicts in `degraded` and
`skipped` modes, and it is rendered as an unverified RES-§9 row rather than
under RES-§6/§7/§8. `axes_considered` must be the
**closed nine-axis list** (REQ-§41) verbatim, and `axes_rationale` must carry
one line per axis. `axes_rationale` is the only place the critic's check C-10a
can read the axis reasoning — the researcher's fenced output block is not
readable by the critic.

### `Coverage — round N` — **cumulative for the run**

```markdown
### Coverage — round 2
host_product: partial
competitors: 3
adjacent: 2
mode: degraded
```

**Cumulative semantics.** The values are the totals **for the whole run so
far**, not for round `N` alone. A top-up round that only touched host-product
sources still restates the competitor and adjacent totals reached in earlier
rounds. This is what stops a top-up from appearing to have researched zero
competitors and wrongly making Definition-of-Done point 12 `n/a`-eligible.
Readers take the highest-`N` record; a reader that instead maxes each field
across all rounds must reach the same answer, and if it does not, the
researcher wrote a non-cumulative record and that is the defect.

`host_product` is one of `high`, `partial`, `none` — how far host-product
research reached, not a source count. Only `none` makes Definition-of-Done
point 11 `n/a`-eligible.

`mode` is one of `full`, `degraded`, `skipped`. **`top-up` is not a legal
value here.** `top-up` is an invocation mode, not a coverage mode: a top-up
round records the run's underlying `research_mode`, because the record is
cumulative for the whole run and a later round cannot retroactively change how
the run was conducted. For `mode: skipped` the values are pinned:
`host_product: none`, `competitors: 0`, `adjacent: 0`.

---

## 4. `coverage.md` — author (**append-only**)

Carries the four enforcement fields from `coverage-json` that the critic must
be able to read from disk. Sections are `## Pass <X> — <field>`, with a
`— round N` suffix on revise rounds.

```markdown
## Pass C — discovery_probes — round 1
| # | Probe | Answered in | Note |
|---|---|---|---|
| 1 | Who initiates this? | EIS-§4 | requester role |
| ... | ... | ... | ... |
| 14 | What happens at scale? | EIS-§16 | 10k grants |
```

```markdown
## Pass C — governance_map — round 1
| REQ id | Governance item | Placed in |
|---|---|---|
| REQ-021 | approval chain | EIS-§11 |
| REQ-022 | audit trail | EIS-§14 |
```

```markdown
## Pass B — proposals_evaluated — round 1
| PROP id | Verdict | Where recorded |
|---|---|---|
| PROP-002 | rejected — conflicts with REQ-014 | EIS-§20 |
```

```markdown
## Pass D — core_objective_unanswered — round 1
| # | Objective | Status | Where |
|---|---|---|---|
| 3 | permissions and capabilities | answered | EIS-§7 |
| 12 | localization | not-applicable | EIS-§17 |
```

**A missing section is not a pass.** When the critic looks for a section and
it is absent, the corresponding check fails **BLOCKING** with that check's
`not recorded` rule. It is never scored `pass` and never silently skipped.

---

## 5. `decisions.md` — author and researcher

```markdown
### DEC-MD-004 — requests expire rather than being cancelled
made_by: eis-author
pass: B
basis: PAT-005
alternatives_rejected: ["manual cancel", "indefinite pending"]
status: assumed
supersedes: none
```

`status` is one of `confirmed-user`, `confirmed-source`, `assumed`. A
correction appends a new record with `supersedes: DEC-MD-004`; the original
line stays.

---

## 6. `questions.md` — analyst, researcher, author

Each specialist appends the questions it raised, in the classification
vocabulary of `question-format.md`. The `asked` / `answer` / `answered_at`
fields are filled in by whichever agent next observes the outcome; the
orchestrator's own record of answers lives in `{stm}/context/answers.md`.

```markdown
### Q-IN-002 — is there a cap on concurrent pending requests?
gate: 1
classification: important
why_it_matters: "a cap changes the shape of EIS-§8 and adds an edge case"
asked: true
answer: "yes, 3"
answered_at: 2026-08-25T14:02:11Z
```

`classification` is one of `blocking`, `important`, `can-safely-default` — the
same closed set the `open-questions` block uses. `why_it_matters` must name the
structural consequence: which flow's shape, which state's existence, which
entry point, or which permission boundary changes if the default is wrong.
"The user might want to know" is not an answer to `why_it_matters`.

---

## What is persisted here versus what stays in a fenced block

The critic reads **only** disk (`{stm}/**` and `{out}/**`). It cannot read
another agent's fenced output block. Anything the critic must enforce is
therefore persisted to a ledger above.

These fields are **deliberately in-block only** — they are orchestration
signals, not enforcement data, and no check may depend on them:

- Analyst: `analysis-summary` (all fields), `conflicts-json`,
  `research-brief`, `location-proposal`, `open-questions`,
  `ready-for-research`.
- Researcher: `research-summary` counters (`sources_cited`, `observed_facts`,
  `inferences`, `evidence_gaps`, `conflicts_noted`, `res_headings_present`,
  `matrix_rows_in_res9`, `deferred_resolved`), `deferred-answers-json`,
  `open-questions`, `ready-for-modeling`.
- Author: `pass-summary` counters (`skeleton_materialised`,
  `eis_headings_present`, `sections_filled`, `sections_marked_not_applicable`,
  `placeholders_remaining`, `next_pass`), the non-enforcement half of
  `coverage-json` (`requirements_addressed`, `requirements_deferred`,
  `derived_requirements`), `research-requests`, `open-questions`,
  `ready-for-review`.
- Critic: `blocking-issues-json[].owner`, `concerns-json`, `open-questions`.

The four `coverage-json` fields that **are** enforcement data
(`discovery_probes`, `governance_map`, `proposals_evaluated`,
`core_objective_unanswered`) are persisted to `coverage.md` above, and the
researcher's `axes_considered` / `axes_rationale`, `Coverage — round N` and
`EV-GAP-###.category` are persisted to `evidence.md` above. If a future check
needs a field from the in-block-only list, the field must first be given a
ledger home — do not teach a check to read a fenced block.
