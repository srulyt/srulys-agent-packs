# Matrices — the five table contracts

Five tables in this pack have fixed column sets. Renaming, reordering, or
dropping a column is a defect.

---

## 1. Capability matrix — EIS-§7 (REQ-§11)

Permission modeling is mandatory whenever access differs between users. Model
at least **actor/subject × resource/object × action × conditions**.

| Capability | Consumer | Owner | Admin | Conditions |
| --- | --- | --- | --- | --- |
| Discover resource | Yes | Yes | Yes | Published resources |
| Request access | Yes | N/A | N/A | Eligible but not entitled |
| Approve request | No | Yes | Yes | Active approver |
| Use resource | Conditional | Yes | Yes | Active entitlement |

Column 1 is `Capability`; the last column is `Conditions`. The middle columns
are one per actor from EIS-§4 — as many as the feature has, named exactly as
EIS-§4 names them.

Cell values: `Yes`, `No`, `Conditional`, `N/A`, or `Unknown — <Q-id>`.

**`Unknown — <Q-id>` is required, not optional**, when a permission decision
has not been made. Do not invent a permission merely to fill the table, and do
not write `No` when the truth is "nobody has decided". An unflagged guess in
this table is the single easiest way to smuggle a fabricated requirement into
the specification.

Explicitly distinguish, in EIS-§7's `### Permission Rules`: discoverability,
visibility, access, use, modification, administration. These are six different
capabilities and collapsing them is a common modeling error.

`### Inheritance / Overrides / Expiration` documents, where applicable:
default, inherited, explicit, ownership-derived, organization-derived,
group-derived, temporary, conditional, and delegated permissions; admin
override; denial; precedence rules; revocation; expiration.

---

## 2. Cross-product pattern matrix — RES-§5 (REQ-§32)

| Problem | Host product | Competitor A | Competitor B | Industry pattern |
|---|---|---|---|---|

Column 1 is the **problem**, phrased as a question the design must answer
("How does access end?"), never as a feature name. Competitor columns are one
per product studied, named for the real product. The final column is the
generalised pattern, not a fourth product.

Every row must be traceable to `PAT-###` records in `{stm}/ledger/evidence.md`
and each cell to `EV-RS-###` or an explicit `EV-GAP-###`.

---

## 3. Evidence-to-recommendation matrix — EIS-§18 / RES-§9 (REQ-§25)

| Decision area | Host product precedent | External precedent | Recommendation | Rationale |
|---|---|---|---|---|
| Access request state | Existing jobs use a persistent Pending status | Competitors expose pending requests | Use a persistent Pending state | Consistent internally and familiar externally |

Five columns, exactly these names, in this order. Use it for every important
interaction decision influenced by research — especially when introducing a
new concept or changing an existing pattern.

A row whose `Host product precedent` and `External precedent` cells are both
empty is a recommendation with no evidence. Write
`None — EV-GAP-###` in the empty cell rather than leaving it blank, so the
absence is visible.

---

## 4. Requirements traceability matrix — EIS-§22 (REQ-§23)

| Requirement | Source | EIS sections | Status | Notes |
|---|---|---|---|---|

`Status` is drawn from a **closed list**:

- `Covered`
- `Partially covered`
- `Requires decision`
- `Out of scope`
- `Contradiction discovered`

Every `REQ-###` in `{stm}/ledger/requirements.md` appears as a row. A
requirement that is absent from this table is an untraced requirement, and the
critic's traceability audit (check C-4) fails on it.

### Derived, recommended, unresolved

Behaviours the analysis introduced that did not exist in the input are listed
in the same table with `Source: derived (DRV-###)` and marked in `Notes` as
one of:

- `derived requirement` — follows necessarily from what the inputs say;
- `recommended requirement` — the pack proposes it; nobody has agreed to it;
- `unresolved decision` — a choice is required and has not been made.

This is what stops a recommendation from silently becoming a requirement.
A `recommended requirement` must also appear under `## Recommendations
Awaiting Decision` in `decision-log.md`, never under `## Confirmed Decisions`.

---

## 5. Assumptions table — EIS-§20 (REQ-§23)

| Assumption | Basis | What would change if it were false |
| --- | --- | --- |
| Approvers act on a request within one working day | No SLA in the inputs; support themes imply days, not hours | Timing guidance in EIS-§14 becomes a requirement rather than a default, and the reminder flow in EIS-§9 gains a step |
| A revoked entitlement is not re-requestable for 24 hours | Product convention elsewhere in the host; not stated for this feature | EIS-§7 gains a permission rule and EIS-§16 gains a re-request edge case |

Column 1 is `Assumption`. **The last column is
`What would change if it were false`** — that heading is a **verbatim literal**,
copied from this file, exactly as the section headings are copied from
`eis-skeleton.md`. Middle columns are optional: add an id column, a `Basis`
column, or a `RES-§9` cross-reference column as the feature needs. Do not
rename, abbreviate, or re-word the first or last column.

Why the last column is pinned rather than described. The obligation it carries
— *every assumption states what would change if it were false* — is audited by
critic check C-12 and scored by Definition-of-Done point 14, and it was
previously specified only as a sentence for the author to paraphrase. Two runs
of this pack produced two different renderings of the same column, which means
neither the critic nor any downstream reader could rely on finding it. A
load-bearing label that everything downstream must locate is a literal, not a
description. The wording is identical to the prose obligation stated in the
author's pass guide and the critic's C-12, so there is exactly one spelling of
this fact in the pack.

Every row's last cell states a **consequence for this specification** — which
section, flow, state or permission changes — never "we would need to check" or
"this would be revisited". An assumption whose counterfactual has no
specification consequence is not load-bearing enough to list.

The same pinned label is used wherever assumptions are listed, including
`## Assumptions` in `decision-log.md`. EIS-§20 and that section must agree; the
critic reads the decision log for C-12.
