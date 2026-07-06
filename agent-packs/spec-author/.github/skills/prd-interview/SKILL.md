---
name: prd-interview
description: "Grill-me interrogation discipline: convert context gaps into a relentless, adversarial, gap-closure-driven question set. Defines P0/P1/P2 tagging, gap-closure termination (no tight cap; large structural safety bound), the MC-vs-freeform rubric (2-6 choices + a 'Not sure / decide later' deferral, no 'Other'), do-not-invent-answers, and the bounded re-grill loop ending in [TBD]+OQ-NN. Triggers on: interview the user, grill me, structured PRD interview, gap questions, P0 questions."
---

# PRD Interview — Grill-Me Interrogation Patterns

This skill is loaded by `@prd-interviewer` (to author a
gap-closure-complete, choice-annotated question set) and
`@spec-author` (to render the questions interactively via
`ask_user` and run the bounded gap-closure loop).

The discipline is **grill-me**: relentless, adversarial,
one-gap-per-question interrogation that closes every open
requirement gap before drafting. Completeness over speed. The
sub-agent never speaks to the user; it emits the question set and
the orchestrator drives the interactive loop.

## When to Use This Skill

Load this skill when:

- Converting `gaps-json` into a gap-closure-complete, choice-
  annotated question set (interviewer).
- Rendering the questions via `ask_user` and running the bounded
  gap-closure loop after the user replies (orchestrator).

## Question-quality rules

1. **One gap per question.** Do not bundle. Re-read the gathered
   context first — never ask what the inputs already answer.
2. **Adversarial framing.** Pose questions that force implicit
   decisions to the surface: "What happens when…?", "What's the
   threshold for…?", "Who is allowed to…?", "What does the user do
   *before* this step?". Prefer the sharp edge case over the bland
   restatement.
3. **MC where enumerable, freeform where open-ended** — see the
   MC-vs-freeform rubric below.
4. **Group by target PRD section** so the user sees structure.
5. **Order by priority within each group.** P0 first.
6. **Gap-closure termination, not a question cap.** Keep asking
   until every P0 and every reasonably-closable P1/P2 gap is
   answered or explicitly deferred. There is **no tight cap** on
   question count. A large **structural safety bound** — on the
   order of dozens of questions — exists only to guarantee
   termination; it is **not** a quality cap and you should almost
   never approach it. Do not artificially truncate a genuinely
   gap-driven interrogation.
7. **Do not invent answers.** If you find yourself filling in a
   placeholder while drafting the question, the answer goes in the
   interview — not in the spec.

## MC-vs-freeform rubric

For every question, decide its `kind`:

- **`multiple_choice`** — use when the answer space is genuinely
  enumerable (a bounded set of distinct options). Rules:
  - Offer **2–6 distinct choices**.
  - **Always** include an explicit **`"Not sure / decide later"`**
    deferral choice as the final option. A user must never be
    forced into a bucket.
  - **Never** add a literal **`"Other"`** bucket — the freeform
    affordance (`allow_freeform: true`, set by the orchestrator when
    it renders `ask_user`) already covers "none of these".
  - Do **not** fabricate choices to pad to a count. If you can only
    name one real option, the question is freeform.
- **`freeform`** — use when the answer is open-ended: values,
  thresholds, narratives, names, rationale ("What is the P95
  latency target?", "Describe the primary user journey."). Do not
  invent buckets for open-ended answers.

## Priority tagging

| Tag | Meaning | Example |
|-----|---------|---------|
| **P0** | Blocker — drafter cannot fill the section without this. | "Who are the primary users? (without this, Users & Personas is empty)" |
| **P1** | Improves quality — answer makes the spec materially better. | "What latency is acceptable?" |
| **P2** | Nice — adds polish. | "Any preferred terminology for the new feature?" |

The orchestrator's re-grill loop only retries on unanswered (or
deferred) **P0** gaps. P1 and P2 unanswered always go straight to
"Open Questions" without retry.

## User-context question bank (bridge to `experience-surface`)

When `gaps-json` flags persona / JTBD / user-journey / roles-and-
permissions / usage-awareness gaps, draw questions from this bank.
The **priority is gated on the `experience-surface` axis** (set by
`@context-detective`):

- **`experience-surface` fired (UI-forward spec):** the persona /
  journey / role gaps needed for the "User Experience: Personas,
  Journeys & Roles" section are **P0** — the grill escalates on
  UI-forward specs.
- **axis did not fire:** the same gaps are **P1/P2**, feeding the
  *woven* context (a JTBD line in Users & Personas, a usage signal
  in Problem Statement); they never block drafting.

| Concept | Example question | Typical kind |
|---------|------------------|--------------|
| Usage awareness | "What does telemetry / support data show about how users hit this problem today?" | freeform |
| Personas | "Which distinct user types will use this? (pick all that apply, or add your own)" | multiple_choice (+ deferral) |
| JTBD | "For persona X, what job are they hiring this for — 'When …, I want to …, so I can …'?" | freeform |
| User journey | "Walk me through the end-to-end steps the user takes to reach the goal." | freeform |
| Roles & permissions | "Which roles exist, and for capability Y, who is allowed and who is denied?" | multiple_choice (+ deferral) or freeform |
| Access model | "Is access decided by role only, or also by object ownership / attributes?" | multiple_choice: RBAC / RBAC + ownership (ReBAC) / attribute-based (ABAC) / Not sure / decide later |

Reference the full templates in
[`spec-driven-prd-best-practices` §11](../spec-driven-prd-best-practices/SKILL.md#11-user-context-weaving-personas-jtbd-journeys-roles)
and
[`user-context-patterns.md`](../spec-driven-prd-best-practices/references/user-context-patterns.md).

## Bounded gap-closure loop (C5)

The interviewer emits the full gap-closure-complete question set
once; the **orchestrator** renders each question via `ask_user`
(enumerable → `choices` + `allow_freeform: true`; open-ended →
freeform) and drives the loop:

1. Map every answered question by the interviewer's coverage IDs.
   A `"Not sure / decide later"` reply counts as **deferred**, not
   answered.
2. **Re-grill remaining or newly-revealed P0 gaps.** After a round
   of answers, if any P0 gap is still unanswered/deferred, OR an
   answer reveals a new P0 gap, issue a focused follow-up round
   asking **only** those P0 gaps (prefixed with one context line,
   e.g. "A couple more before I can draft — these block the spec").
   Repeat until every P0 gap is answered or explicitly deferred.
3. **Structural safety bound (termination guarantee, not a quality
   cap).** Cap the loop at a large structural bound — on the order
   of a handful of re-grill rounds / dozens of total questions.
   This exists only to prevent non-termination; a well-scoped spec
   closes P0 gaps in one or two rounds. Do NOT treat the bound as a
   target or use it to truncate a genuinely open interrogation.
4. **Residue → do-not-invent fallback.** When the loop ends with a
   P0 still unanswered/deferred: tell `@prd-drafter` to fill that
   section with `[TBD — interview question N unanswered]` and add a
   verbatim `OQ-NN` entry to the spec's "Open Questions" section.
   Never fabricate the answer.
5. **P1/P2 unanswered → straight to "Open Questions", no retry.**
   They never block progress and are never re-grilled.

## Anti-patterns

| Anti-pattern | Problem | Fix |
|--------------|---------|-----|
| Artificial tight cap ("stop at 12") | Leaves P0 gaps open; the spec ships with holes | Terminate on gap closure; only the large structural safety bound applies. |
| Fabricated multiple-choice buckets | Misleads the user; invents structure | If you can name only one real option, make it freeform. |
| Forcing the user into a bucket with no deferral | User can't say "unknown"; produces bad data | Every MC question ends with `"Not sure / decide later"`. |
| Adding a literal `"Other"` choice | Redundant with the freeform affordance | Drop `"Other"`; rely on `allow_freeform: true`. |
| Compound questions ("latency target AND rollout window?") | One half gets answered | Split into two questions. |
| Closed yes/no when the answer is qualitative | Loses information | Ask "Why?" / "What does that look like?" (freeform). |
| Asking about the obvious ("What's this feature called?") | Wastes attention | Re-read inputs first. |
| Retrying P1/P2 if unanswered | Slows the user; not a blocker | Promote to "Open Questions" silently. |

## Quality checklist

- [ ] No artificial cap — the set is sized by gap closure, not a
      fixed number; only the large structural safety bound applies.
- [ ] Every question is one gap, adversarially framed.
- [ ] Every question tagged P0 / P1 / P2, P0 first.
- [ ] Every question has a `kind` (multiple_choice | freeform).
- [ ] Every `multiple_choice` question has 2–6 real choices, ends
      with `"Not sure / decide later"`, and has no `"Other"`.
- [ ] Every question maps to a specific PRD section in the coverage
      output.
- [ ] User-context gaps are P0 iff `experience-surface` fired, else
      P1/P2.
- [ ] No compound questions.
- [ ] The fenced question set and `interview-questions.md` agree
      byte-for-byte.
