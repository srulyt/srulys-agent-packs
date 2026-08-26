# eis-author — pass plan

This is an **agent-local reference** for `@eis-author`. It has **no
frontmatter** on purpose: the Copilot plugin loader registers only
`*.agent.md`, so this file sits beside the agent file in `agents/` without
being registered as an agent. Only `@eis-author` reads it.

It exists because the EIS is written across four separate invocations, each
with a fresh context window. The pass plan must survive a context reset; the
agent prompt cannot carry it and stay under its size ceiling.

---

## Two notations — never interchangeable

| Notation | Example | Where it is legal |
|---|---|---|
| **Heading literal** | `## 8. State Models` | The `##` line in `eis.md`, copied verbatim from the skeleton block. |
| **Reference shorthand** | `EIS-§8` | Prose, cross-references, ledgers, ownership tables, `sections_filled`, `lands_in`, envelope JSON. |

Throughout this file a section is introduced as `` `## 8. State Models` ``
(`EIS-§8`): **the backticked heading is the exact text to write**, and the
sigil in parentheses is the id used to refer to it everywhere else.

**`EIS-§` must never appear on a `##` line.** `## EIS-§8 State Models` is a
contract violation even though its title is right.

---

## The core discipline: skeleton-first, fill-in-place

`{out}/eis.md` is **not** an append-only file. Appending would place
`## 1. Executive Summary` (`EIS-§1`) — written last, in pass D — after
`## 22. Requirements Traceability` (`EIS-§22`), and the heading order is a hard
contract.

> **Skeleton-first is also the pack's write guarantee.** Materialising the
> skeleton is a real `apply_patch` call, and it is the *first* thing pass A
> does — before reading a ledger, before modeling anything. It exists so that
> `{out}/eis.md` is on disk from the earliest possible moment, whatever
> happens later in the pass. A pass that models beautifully and writes nothing
> has failed; see `## Write Mandate` in the agent prompt.

1. **Pass A materialises the skeleton first.** Copy the fenced skeleton block
   in `eis-skeleton.md` (from `eis-document-contracts/references/`) **verbatim**
   into `{out}/eis.md` — copy the heading lines rather than retyping them from
   the ownership table below. All 22 headings exist, in order, from that
   moment, each in its canonical `## <n>. <Title>` form. Each body is:

   ```
   <!-- EIS-PENDING: pass B -->
   _Pending — pass B._
   ```

   where the pass letter is the owner from the table below.
2. **Every pass replaces the sentinel block of the sections it owns, in
   place.** Pass A does this too, immediately after materialising.
3. **No pass touches a section owned by another pass.** Not to "improve" it,
   not to fix a typo, not to add a cross-reference. If pass C notices a defect
   in `EIS-§5`, it says so in `open-questions` and the orchestrator re-launches
   pass A.
4. **Pass D verifies zero sentinels remain** and reports
   `placeholders_remaining: []`. If any remain, list them as
   `EIS-§<n>:<owning-pass>` rather than inventing content.

The word *append* applies only to the STM ledgers (`decisions.md`,
`questions.md`, `evidence.md`, `coverage.md`). It never applies to `eis.md`.

---

## Ownership table

| Pass | Fills, in place | Also writes |
|---|---|---|
| **A** | `EIS-§2`, `EIS-§3`, `EIS-§4`, `EIS-§5`, `EIS-§6`, `EIS-§7` | the skeleton itself; `DEC-MD-###`, `Q-MD-###` |
| **B** | `EIS-§8`, `EIS-§9`, `EIS-§10`, `EIS-§11`, `EIS-§12`, `EIS-§13` | Mermaid diagrams; `coverage.md § Pass B — proposals_evaluated` |
| **C** | `EIS-§14`, `EIS-§15`, `EIS-§16`, `EIS-§17`, `EIS-§18` | `coverage.md § Pass C — governance_map`; `coverage.md § Pass C — discovery_probes` |
| **D** | `EIS-§1`, `EIS-§19`, `EIS-§20`, `EIS-§21`, `EIS-§22` | `{out}/decision-log.md`; `coverage.md § Pass D — core_objective_unanswered` |

Conditional sections: **`EIS-§12`** (owned by pass B) and **`EIS-§17`** (owned
by pass C). Conditional means *conditionally substantive*, never *optionally
present*. When not applicable, the body reads `Not applicable — <reason>`. A
sentinel is never a substitute for that line, and those two ids may appear in
`sections_marked_not_applicable` only in a pass-B or pass-C report
respectively.

---

## Pass A — skeleton and model core

**Read first**: `{stm}/ledger/requirements.md`,
`{stm}/ledger/context-ledger.md`, `{stm}/context/answers.md`,
`{out}/ux-pattern-research.md`.

**Do**

1. Materialise the skeleton (above). Report `skeleton_materialised: true`.
   Then **verify the headings before going further**: re-read every `^## ` line
   of `{out}/eis.md` and confirm each is the canonical `## <n>. <Title>` form
   and that **none** contains `EIS-§`. Rewrite any that do, from the skeleton
   block. Headings are frozen from this point; passes B, C and D edit bodies
   only.
2. `## 2. Scope` (`EIS-§2`) — In Scope / Out of Scope / Dependencies. Out-of-scope items
   are *decisions*, not omissions: each says why.
3. `## 3. Experience Goals` (`EIS-§3`) — User Outcomes, Business Outcomes, Design
   Principles, Design Invariants. An invariant is a property that must hold in
   every flow you later model; write it so pass B and pass C can be checked
   against it.
4. `## 4. Actors and Roles` (`EIS-§4`) — every human and system actor, including the
   ones the input never names (approvers, auditors, admins, the system
   itself). Each actor gets what it wants, what it can do, and what it must
   never be able to do.
5. `## 5. Conceptual Model` (`EIS-§5`) — Objects, Relationships, and the explicit
   user-facing-vs-implementation concept split. If the input's vocabulary is
   an implementation vocabulary, say so and give the user-facing name.
6. `## 6. Terminology` (`EIS-§6`) — one row per term: the term, what it means here, what
   it must **not** be confused with, and where the name came from (host
   product convention, input document, or derived).
7. `## 7. Permissions and Capabilities` (`EIS-§7`) — the capability matrix
   (`actor × object × action × conditions`), permission rules, inheritance,
   overrides, expiration. **Mandatory whenever access differs between users.**
   Unknown permission decisions become `Q-MD-###`, never invented rules.

**Emit**: `DEC-MD-###` to `{stm}/ledger/decisions.md`; `Q-MD-###` to
`{stm}/ledger/questions.md`. Do not write `coverage.md` in pass A.

**Self-lint before returning**: no visual attributes; no implementation
technology; no filler adjectives; no collapsed distinction between a role and
a permission, or between an object and a view of an object.

---

## Pass B — behaviour

**Read first**: everything pass A wrote, plus
`{stm}/ledger/context-ledger.md` for `PROP-###` records and the
`visual-inventory` when present.

**Do**

1. `## 8. State Models` (`EIS-§8`) — one subsection per stateful object. States,
   transitions, who or what triggers each, and what is visible in each. Use a
   Mermaid `stateDiagram-v2` **in addition to** prose, never instead of it.
   Include the non-happy states: pending, processing, partial success,
   failure, expired, revoked, stale, superseded.
2. `## 9. Entry Points and Discovery` (`EIS-§9`) — how each actor arrives. This is one
   of only two sections where interface-layer content is permitted, and it is
   phrased as a constraint on design: *"the request action must be reachable
   from the resource itself"*, not *"a button in the top-right"*.
3. `## 10. User Journeys` (`EIS-§10`) — the front-stage view, per actor, end to end.
4. `## 11. Business / System Workflows` (`EIS-§11`) — the back-stage view: what the
   system does, in what order, with what timing and what failure semantics.
   **Keep §10 and §11 as separate representations.** Never conflate them.
5. `## 12. Service Blueprint` (`EIS-§12`) — only when there is meaningful cross-actor or
   front-stage/back-stage choreography; otherwise
   `Not applicable — <reason>`.
6. `## 13. Interaction Scenarios` (`EIS-§13`) — `UX-001`, `UX-002`, … one per behaviour
   where ambiguity would otherwise land on the UX designer. Use the
   interaction-contract field list verbatim.

**Evaluate every `PROP-###`** against the proposal criteria and append
`## Pass B — proposals_evaluated` to `{stm}/ledger/coverage.md`: id, verdict
(`adopt` / `adapt` / `reject`), and a `why`. A problematic supplied concept
gets a reason and an alternative — do not merely formalise it.

---

## Pass C — resilience, cross-cutting, handoff

**Read first**: passes A and B, `{stm}/ledger/evidence.md`,
`{out}/ux-pattern-research.md § RES-§9`.

**Do**

1. `## 14. System Feedback and Notifications` (`EIS-§14`) — who is told what, when,
   through what channel, and what happens when they are not reachable.
   Auditability and activity-history surfacing land here.
2. `## 15. Error and Recovery Behavior` (`EIS-§15`) — per failure, what the user sees,
   what they can do, and what the system does on its own.
3. `## 16. Edge Cases` (`EIS-§16`) — the classes the input never mentions: concurrent
   modification, duplicate action, resource deleted mid-flow, permission lost
   mid-flow, external collaborator, policy changed after approval,
   discoverability of sensitive resources.
4. `## 17. Accessibility / Localization Considerations` (`EIS-§17`) — behavioural only
   (focus order semantics, announcement content, text-expansion tolerance,
   locale-sensitive semantics), or `Not applicable — <reason>`.
5. `## 18. UX Requirements for Design Handoff` (`EIS-§18`) — the second and last section
   where interface-layer content is permitted, again as constraints: what the
   design must make possible, what information must be available at each
   point, what must be confirmable.

**Two sweeps, both recorded.**

- **Governance placement** → `## Pass C — governance_map`. Sweep the ten
  governance items using the placement map in
  `interaction-modeling/references/cross-cutting-constraints.md`. Each item
  gets `lands_in: EIS-§n` with its `source: REQ-###`, or
  `lands_in: not-applicable — <reason>`. Governance behaviour with no
  `REQ-###` and no `EV-RS-###` behind it goes to `EIS-§20` labelled
  *recommendation requiring validation*. **Never invent a legal, security,
  privacy or compliance requirement.**
- **Discovery probes** → `## Pass C — discovery_probes`. All 14 probes from
  `eis-quality-bar/references/discovery-probes.md`, each with exactly one
  outcome: `answered-by-input` (cite the `REQ-###`), `derived` (cite the
  `DRV-###`), or `product-choice` (cite the `Q-MD-###`). If all 14 come back
  `answered-by-input`, **say so explicitly in the pass summary** — by the
  probe set's own standard that is a reformatted PRD, and the critic will
  block on it whether or not you mention it.

---

## Pass D — ledger and synthesis

**Read first**: everything. This is the only pass that reads the whole
document.

**Do**

1. `## 19. Confirmed Decisions` (`EIS-§19`) — decisions actually confirmed by the user or
   stated in an input. Cross-reference `RES-§9` rows; never duplicate the
   matrix.
2. `## 20. Assumptions` (`EIS-§20`) — the pinned assumptions table from
   `eis-document-contracts/references/matrices.md § 5`: first column
   `Assumption`, last column **`What would change if it were false`**, copied
   verbatim, and every row populating that last column with a consequence for
   this specification. Every recommendation resting on an `EV-GAP` lives here,
   not in `EIS-§19`.
3. `## 21. Open Questions` (`EIS-§21`) — every unresolved `Q-IN-###` / `Q-RS-###` /
   `Q-MD-###`, marked blocking or non-blocking.
4. `## 22. Requirements Traceability` (`EIS-§22`) — every `REQ-###` from the frozen
   inventory with a status; every behaviour you introduced marked *derived
   requirement*, *recommended requirement*, or *unresolved decision*.
5. `## 1. Executive Summary` (`EIS-§1`) — written **last**, filled **in place at the top
   of the existing skeleton**. What this specifies, for whom, and what remains
   undecided.
6. `{out}/decision-log.md` — the six-heading skeleton verbatim, each entry
   carrying `Status:`, `Decision:`, `Rationale:`, `Evidence:`,
   `Implications:`. Every `CON-###` from the analyst appears under
   `Contradictions / Risks` as unresolved unless a user decision is recorded.

**Evidence cross-reference sweep.** For each `RES-§9` row, `EIS-§19` (or
`EIS-§20` if still an assumption) cites the row, and the decision-log entry's
`Evidence:` lists that row's `EV-RS-###` ids. Where your decision **differs**
from the matrix recommendation, record a `DEC-MD-###` with the reason.
Divergence is allowed; silent divergence is not.

**Core-objective coverage self-check** → `## Pass D —
core_objective_unanswered`. Map all 16 items from
`interaction-modeling/references/core-objective-coverage.md` to at least one
filled EIS section. Any item with no home is recorded with its reason. An
empty list is a claim the critic verifies against your actual section bodies —
do not report `[]` to look complete.

**Finally**: scan for `<!-- EIS-PENDING` across the whole document. Report
`placeholders_remaining: []` only if the scan is genuinely empty.

---

## Fix rounds

When the orchestrator re-invokes you as `author-pass-{p}-fix{n}` with a review
artifact path and a list of `BLK-###` ids:

- Read `{stm}/artifacts/review-full-{n}.md` for those ids only.
- Fix **only** the named sections, in place, within your pass's ownership.
- If a fix requires touching a section another pass owns, say so in
  `open-questions` and return — do not reach across the boundary.
- Append a new `## Pass <X> — <field> (round n)` section to `coverage.md` for
  any sweep you re-ran. **Never edit the earlier round's section**; the critic
  reads the highest round.
