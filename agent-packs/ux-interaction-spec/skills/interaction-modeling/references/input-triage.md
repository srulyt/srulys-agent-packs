# Input triage (REQ-§6, §37, §38, §39)

Analyse the input before asking questions.

## What to extract (REQ-§6)

explicit requirements · implicit requirements · constraints · assumptions ·
goals · non-goals · actors · entities · workflows · dependencies · success
criteria · technical limitations that affect UX · business rules · compliance
or governance constraints · unresolved decisions · contradictions

Each becomes a `REQ-###` record in `{stm}/ledger/requirements.md` with a
`kind` (`functional`, `constraint`, `business-rule`, `technical-limit`,
`governance`, `success-criterion`, `non-goal`) and a `confidence` (`stated`,
`implied`, `inferred`). Never upgrade a confidence.

**Do not treat every statement in a PRD as equally authoritative.** A stated
business rule and an aside in a background paragraph are different kinds of
claim, and the `confidence` field is where the difference is recorded.

## Conflicts

If multiple supplied artifacts conflict, **identify the disagreement**. Do not
silently choose an interpretation.

Each conflict is a `CON-###` record naming both sources, both statements, and
what it blocks. Conflicts survive to `## Contradictions / Risks` in
`decision-log.md` unless a user answer resolves them.

The three conflict shapes worth hunting for:

1. **Direct contradiction** — two sources state incompatible facts.
2. **Unmodeled operation** — one source describes an operation (often
   asynchronous) that another source's model has no state for.
3. **Absent rule** — a source implies a permission or policy that no source
   actually states. This one reads as a gap, not a conflict, and is the
   easiest to miss; record it as a `CON-###` with `statement_b: absent`.

## Before asking, try to answer (REQ-§7)

Do not ask a question merely because information is absent. First establish
whether the answer can be:

- inferred safely from existing context;
- discovered through host-product research;
- discovered through competitor research;
- derived from an established product convention.

Ask the user only when an unresolved decision is genuinely a **product
choice**.

Good questions look like: Can users discover resources they do not have
permission to use? · Can an approval be revoked after it has been granted? ·
Is access granted to the requesting person or to their organization/team? ·
Who becomes the approver if ownership changes? · Is approval permanent or time
limited? · Can more than one pending request exist? · Does deleting the parent
object revoke derived access? · Can an administrator bypass normal approval? ·
What should happen if provisioning succeeds for only part of the resource? ·
Is the requested operation expected to be immediate or asynchronous?

Poor questions ask for information that can easily be researched from existing
documentation.

## Very incomplete input (REQ-§37)

A rough concept is a legitimate input. Do not demand a complete PRD before
helping. Work the ladder:

1. Extract the underlying user problem.
2. Identify likely actors and objects.
3. Research the host product.
4. Research established solutions to the problem.
5. Develop candidate interaction models.
6. Identify consequential product choices.
7. Ask focused follow-up questions.
8. Recommend defaults when evidence supports them.
9. Clearly label assumptions.
10. Progressively construct the EIS.

One purpose of this pack is to **expose requirements that have not yet been
considered**. A thin input produces a specification with more labelled
assumptions and more open questions — not a thin specification.

## Input that already contains UX concepts (REQ-§38)

Treat supplied interaction concepts as **proposals**, not immutable
requirements, unless explicitly identified as requirements.

Each becomes a `PROP-###` record with `status: not-yet-evaluated`. The author
evaluates every one at pass B against: user goals · host-product conventions ·
competitor conventions · permissions · state complexity · scalability · edge
cases · consistency · technical constraints — and records the verdict in
`{stm}/ledger/coverage.md § Pass B — proposals_evaluated`.

If a concept appears problematic, explain why and recommend alternatives. **Do
not merely formalize a flawed concept because it appeared in the input.** An
unevaluated `PROP-###` is a BLOCKING finding (critic check C-12).

## Visual hints supplied in any input (REQ-§29)

Whenever an input supplies a visual or UI detail — a colour, a component name,
a layout, "a modal with two tabs" — **you** record it as a `VIS-###` record in
`{stm}/ledger/context-ledger.md`. You are the only agent that writes that
ledger, so if you do not record the hint, nothing does.

```markdown
### VIS-001 — "a modal with two tabs"
kind: visual-hint
source: inputs/design-brief.md §3
behavioural_content: "user chooses between duration-based and ticket-based justification"
verdict: layout-detail-withheld
```

`behavioural_content` is the requirement hiding under the presentation — what
must be true, stripped of how it looks. The author specifies that; the
presentation detail stays here. The rewrite move, with worked examples, is in
`eis-quality-bar/references/anti-requirements.md`; the *writing* of the record
is yours alone.

Never silently drop a visual hint. The user asked for something and is owed an
answer about what happened to it.

## Existing UI supplied (REQ-§39)

Analyse screenshots, prototypes, or UI documentation for: visible concepts ·
actions · terminology · hierarchy · permissions · state handling · consistency
with the rest of the product · **missing states** · **hidden assumptions** ·
potential interaction conflicts.

Focus on what the UI implies about the **product model**, not on aesthetic
critique. "The row has no state for a failed provisioning attempt" is the
finding; "the table is cramped" is not.

Visual details lifted out of the input are recorded as `VIS-###` records (see
above) with their `behavioural_content` and a verdict, so the substitution is
auditable rather than silent.
