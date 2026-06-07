---
name: grill-me-interrogation
description: "Step 2 of the EARS PRD workflow. A grill-me-style interrogation that closes every requirement gap before drafting, with NO upper cap on questions (completeness over speed). Poses questions via the ask-question ask_user tool, multiple-choice for enumerable answers and freeform for open-ended ones. Triggers on: grill me, interrogate, ask the gap questions, interview for the PRD, what is missing."
---

# Grill-Me Interrogation (step 2)

This skill converts context gaps into a thorough, adversarial "grill
me"-style interrogation that closes **every** requirement gap blocking a
good EARS PRD. It is distilled from `spec-author`'s `prd-interview` plus
the "grill me" gap-closing pattern: a direct, one-gap-per-question
challenge style that forces the user to make implicit decisions
explicit.

> **Step 2 is the deliberate place to be thorough.** The plugin's
> overall speed/low-friction bias governs steps 1, 3, and 4 — but
> **here, completeness of context wins over speed**, because a
> high-quality EARS PRD depends on no requirement gaps remaining.

## When to Use This Skill

Load this skill at **step 2**, after context-gathering, to interrogate
the user and close gaps before any outline or draft is produced.

## The grill-me technique

- **Direct and challenging.** "What is the p95 latency target?", not
  "We will need to know the latency."
- **One gap per question.** Never bundle two decisions into one
  question.
- **Force implicit decisions to the surface.** Use framings like *"What
  happens when …?"*, *"What's the threshold for …?"*, *"What's the
  expected behaviour if … fails?"*.
- **Re-read the gathered context first.** Don't ask about things the
  context already answered.

## No upper cap on questions (gap-closure termination)

**There is NO tight cap on the number of questions.** This step asks as
many high-leverage questions as are needed to close every gap. Do not
stop at an arbitrary count (the legacy `spec-author` "max-12" cap is
**removed entirely** here — see the plugin README's mapping reference).

Termination is governed by **gap closure**, not question count:

1. Ask only **one-gap** questions, each tied to a real, currently
   **unfilled PRD slot** (a section the formatter would otherwise leave
   empty or guess at).
2. **Stop** when every **P0** gap and every **reasonably-closable
   P1/P2** gap is either answered or explicitly deferred.
3. **Safety bound** (structural only, never a tight cap): if you somehow
   reach a very large number of questions (on the order of dozens) with
   gaps still open, stop and route the residue to Open Questions rather
   than loop pathologically. This bound exists only to prevent
   non-termination; it is **not** a quality cap and you should rarely
   approach it for a normal feature.

## Priority tagging (P0 / P1 / P2)

Tag **every** question so the user sees blockers first.

| Tag | Meaning | Example |
|-----|---------|---------|
| **P0** | Blocker — the formatter cannot fill the section without this. | "Who are the primary users? (without this, Users & Personas is empty)" |
| **P1** | Improves quality — the answer makes the spec materially better. | "What latency is acceptable?" |
| **P2** | Nice — adds polish. | "Any preferred terminology for the feature?" |

Ask in **priority order — P0 first.**

## Ask-question (`ask_user`) tool usage contract

The skill MUST pose questions through the built-in **ask-question /
`ask_user`** tool (a built-in; do not declare it in any `tools:` list),
so the host surfaces each as a discrete, answerable prompt rather than
burying it in prose. One `ask_user` call per gap.

### Decision rubric — multiple-choice vs. freeform

**Use MULTIPLE-CHOICE when the answer space is enumerable.** If the gap
has a small, bounded, knowable set of plausible answers, present the
question **with explicit enumerated choices** via the tool's `choices`
affordance:

- Offer **2–6** sensible, mutually-distinct options derived from the
  gathered context. Labels must be short, parallel, and
  non-overlapping.
- Set `allow_freeform: true` so the host auto-adds a freeform "specify
  your own" path — the user is never forced into a wrong bucket. **Do
  not** add a literal `"Other"` choice string; the `allow_freeform`
  affordance already provides "specify your own" (adding `"Other"`
  duplicates it).
- **Always also include an explicit `"Not sure / decide later"`
  choice.** This is a *distinct deferral semantic* (not a duplicate of
  the freeform path): selecting it routes the gap into the P0-retry /
  `[TBD]`+Open-Question discipline below.

Enumerable examples: auth model, target platform, yes/no decisions,
priority tiers, severity levels.

**Use FREEFORM when the answer is open-ended.** If the answer is a
quantity, a name, a narrative, a threshold value, or otherwise not
practically enumerable, ask a **freeform** question (`ask_user` with no
`choices`). **Do not fabricate fake choices** just to use
multiple-choice.

Freeform examples: "What is the p95 latency budget?", "Describe the
primary user's main job-to-be-done."

### Worked example — MULTIPLE-CHOICE (enumerable gap)

```
ask_user(
  question: "[P0] Which authentication model should the system use?",
  choices: [
    "OAuth2 (third-party identity provider)",
    "SAML (enterprise SSO)",
    "API key (service-to-service)",
    "None (no auth required)",
    "Not sure / decide later"
  ],
  allow_freeform: true
)
```

Five distinct options (within 2–6), a `"Not sure / decide later"`
deferral choice, and `allow_freeform: true` for the "specify your own"
escape. No literal `"Other"` string.

### Worked example — FREEFORM (open-ended gap)

```
ask_user(
  question: "[P1] What is the p95 latency budget for a search request?",
  allow_freeform: true
)
```

No `choices` — a latency threshold is a value, not an enumerable set.
Fabricating buckets like "fast / medium / slow" would lose information.

## Do-not-invent + partial-answer fallback

- **Never invent answers** to fill the spec. If you find yourself
  filling a placeholder, that belongs in a question, not the draft.
- **P0 unanswered (incl. "decide later"):** retry **once** with only the
  unanswered P0 question(s), prefixed with one line explaining they
  block a useful spec. After that single retry, if a P0 is still
  unanswered, the formatter fills the section with `[TBD — <reason>]`
  and adds a verbatim `OQ-NN` Open Question.
- **P1/P2 unanswered:** go **straight to Open Questions** — **no
  retry.**

## Must NOT

- MUST NOT impose an artificial upper cap on question count — keep
  asking until all gaps close or are explicitly deferred (a very large
  structural safety bound only, never a tight cap).
- MUST NOT bundle multiple gaps into one compound question.
- MUST NOT fabricate multiple-choice options when the answer is
  genuinely open-ended — use freeform instead.
- MUST NOT force the user into an enumerated bucket — always include the
  `"Not sure / decide later"` choice and `allow_freeform: true`.
- MUST NOT add a literal `"Other"` choice string (duplicates the
  `allow_freeform` affordance).
- MUST NOT invent answers — unknowns become questions, then
  `[TBD]` + Open Questions.
- MUST NOT retry P1/P2 questions (only one P0 retry).

## Fallback when `ask_user` is unavailable

If the host does not expose an `ask_user`/ask-question affordance (or
choice metadata does not render), pose the **same** one-gap,
P0/P1/P2-tagged questions as plain conversational prompts — and for
enumerable gaps, list the 2–6 options plus "Not sure / decide later"
inline. The discipline is preserved even without the structured tool.

## Quality Checklist

- [ ] Every question targets exactly one gap (no compound questions).
- [ ] Every question tagged P0/P1/P2; asked P0-first.
- [ ] Enumerable gaps → `ask_user` with 2–6 distinct choices +
      "Not sure / decide later" + `allow_freeform: true`; no `"Other"`.
- [ ] Open-ended gaps → freeform `ask_user` (no fabricated choices).
- [ ] No invented answers anywhere.
- [ ] One P0 retry only; P1/P2 non-answers go straight to Open Questions.
- [ ] No tight question cap applied; termination is gap-closure based.
