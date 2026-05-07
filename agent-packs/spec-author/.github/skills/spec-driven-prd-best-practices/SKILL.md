---
name: spec-driven-prd-best-practices
description: "Distilled spec-driven-development and PRD best practices: PR/FAQ framing (Working Backwards), structure-before-prose, outcome-over-output, P0/P1/P2 prioritisation, testable acceptance criteria, open-questions discipline. Triggers on: PRD best practices, spec-driven development, working backwards, PR/FAQ, outcome-over-output, testable acceptance criteria."
---

# Spec-Driven Development & PRD Best Practices

This skill captures the convergent guidance across the major
spec-driven-development and PRD-writing schools of thought. The
catalogue and complexity heuristic live in `prd-template`; this
skill is about **how to fill the sections well**.

## When to Use This Skill

Load this skill when:

- Researching context for a PRD (`@context-detective`).
- Drafting content (`@prd-drafter`).
- Building the Stop A summary (`@spec-author`).

## Domain neutrality

The practices below are industry-neutral. Domain-specific framing
(regulated workloads, vendor-specific quality attributes) is
deferred to user-supplied instructions.

## Core principles

### 1. Structure before prose (the "Stop A" reason)

The structure of a spec carries more leverage than the prose. Lock
the section set with the user before drafting. Skipping this step
is the leading cause of wasted re-drafting.

**Practical rule:** the orchestrator's Stop A presents the section
set; do not draft until the user approves.

### 2. Working Backwards (PR/FAQ)

Frame the spec as if writing the launch announcement first:

- **What problem does this solve, in the customer's voice?**
- **What is the press-release one-liner?**
- **What are the FAQs the customer would ask?**

This sharpens "Problem Statement", "Goals & Success Metrics", and
"Solution Summary". The drafter should write Problem Statement so
that an outsider could explain the customer's pain in one
paragraph.

### 3. Outcome over output

Goals should be **outcomes the user/business observes**, not
**features the team ships**.

Bad: "Ship a notifications panel."
Good: "Reduce time-to-first-action on a new alert from N minutes
to M minutes for >70% of users."

Every entry in "Goals & Success Metrics" must be measurable —
baseline + target + measurement window.

### 4. Testable acceptance criteria

Acceptance criteria must be falsifiable. Use Given / When / Then
or equivalent. Acceptance criteria verify the EARS shall-statement
of their FR (see §4a); the shall-statement is the contract,
Given/When/Then is the verification.

Bad: "AC-03: The notification appears quickly."
Good: "AC-03.1: Given a notification is generated, when the user
opens the app within 30s, then the notification appears within
2s p95."

The critic's D4 (content-quality) penalises non-testable ACs.

### 4a. EARS — Easy Approach to Requirements Syntax

Every Functional Requirement is written as **one** EARS
shall-statement using one of these patterns:

| Pattern | Template |
|---------|----------|
| Ubiquitous       | `The <system> shall <response>.` |
| Event-driven     | `When <trigger>, the <system> shall <response>.` |
| State-driven     | `While <state>, the <system> shall <response>.` |
| Optional-feature | `Where <feature is included>, the <system> shall <response>.` |
| Unwanted         | `If <undesired condition>, then the <system> shall <response>.` |
| Complex          | A combination, e.g. `When X, while Y, the <system> shall <response>.` |

Rules:

- Exactly one `shall` per FR.
- The `<system>` clause names the product / component, never "we"
  or "the user".
- Triggers and states are observable conditions, not intentions.
- Avoid passive voice in the response clause.
- EARS expresses **what**, never **how**. Implementation choices
  belong to engineering design, not the FR.
- Each FR is paired with one or more Acceptance Criteria written
  as Given / When / Then scenarios that verify the
  shall-statement. ACs are nested under their FR with hierarchical
  IDs (`AC-<FR>.<n>`).

Example:

> **FR-12** *(event-driven, P0)* — When a user opens an unread
> notification, the Notifications service shall mark it as read
> within 500ms p95.
>
> **AC-12.1** — Given a user has 1 unread notification, when the
> user taps it, then the unread badge decrements to 0 within 500ms
> in 95 of 100 sampled sessions.

### 5. P0 / P1 / P2 priority on requirements

Tag every requirement with a priority. P0 = blocker for first
ship; P1 = should-have; P2 = nice. This forces the team to declare
the minimum viable scope.

Source convergence: Lenny Rachitsky's PRD essays;
Aha! product-spec guide; Linear's "ship a draft, iterate"
cadence.

### 6. Open Questions are first-class

Anything the team has not yet decided becomes an `OQ-NN` entry
with an owner and a resolution-due date. The drafter never
silently picks one option when the inputs do not constrain it. If
the orchestrator or detective sees an ambiguity, it surfaces the
choice through Stop A — never decide it at runtime.

This addresses the canonical failure mode: "the spec quietly
assumes X, the team builds X, the customer needed Y."

### 7. Out of Scope is a section, but not a fishing expedition

Explicit non-goals prevent scope creep — but only when they are
**load-bearing**. A non-goal earns its place only if a competent
reader of the rest of the spec would otherwise reasonably assume
the item was in scope. If a topic was never raised, do not
introduce it just to negate it.

**The only-when-load-bearing rule.** Include an Out-of-Scope
bullet iff at least one of the following is true:

1. The Problem Statement, Goals, Solution Summary, or Functional
   Requirements use language that would lead a reader to expect
   the item is in scope (adjacency-by-language).
2. A stakeholder, prior version, or roadmap document the
   detective surfaced explicitly conflated this work with the
   item being excluded.
3. The user, at Stop A or in the prompt, named it as a non-goal.

If none of (1)–(3) holds, the item does not belong here. An
empty Out-of-Scope section is acceptable and preferred over
fabricated negations like *"performance tuning is out of scope"*
or *"no migration required"* when those topics were never
adjacent to the spec.

This rule generalises to any negation phrasing elsewhere in the
spec — *"not supported"*, *"no additional work required"*,
*"<X> is not in scope of this revision"*. Apply the same
adjacency-by-language test before writing it.

### 8. Evidence & citation discipline

A spec is a product document, not an annotated bibliography. Quote
sources sparingly. A citation earns its place only when **all three**
of the following hold:

1. The evidence is critical for additional context the reader cannot
   reconstruct from the spec body alone, AND
2. It comes from an **authoritative, durable** source — public web
   documentation, a published standard or RFC, a separately
   versioned specification, an ADO work item, a SharePoint document,
   an internal wiki page with a stable URL, or a vendor / regulator
   reference, AND
3. There is a high probability the reader will actually need to
   open it (to verify a requirement, follow a regulation, reproduce
   a metric).

When a source qualifies, prefer the **primary** source — the
standard, RFC, vendor doc, ADO item itself — never a secondary
location that merely *mentions* the source.

**Never** cite a path that the workspace's `.gitignore` matches.
The agent treats `.gitignore` as authoritative; the patterns below
are an illustrative subset that callers should expect to see, but
ANY gitignored path is non-citable, even if it is not on this list.

Common categories the agent sees in this pack's runs:
- Pack STM directories: `.spec-author/`, `.copilot-factory/`,
  `.factory/`, `.prompts/`, `.local/`, any `*-stm/` directory.
- Eval scratch: `evals/packs/*/workspaces/`,
  `evals/packs/*/results-local/`, `evals/packs/*/reports/`,
  `evals/packs/*/fixtures/`, `evals/data/`.
- IDE / system: `.vscode/`, `.idea/`, `node_modules/`,
  `__pycache__/`.

These are ephemeral working notes the reader cannot retrieve. A
citation that would only resolve inside the agent's scratch space
is, by definition, not citable.

If you are tempted to cite a fact you can only point to via a
gitignored path, that fact must be either (a) inlined into the
spec body with attribution to its real upstream source, or
(b) marked `[TBD — needs primary source URL]` and added as an
`OQ-NN` entry, or (c) dropped if it does not earn its place.

**Notation.** Use markdown footnotes for citations:

> The notification queue handles roughly 4M events/day per the
> 2024 platform-load review.[^load-2024]
>
> [^load-2024]: Platform Load Review 2024 — https://contoso.sharepoint.com/.../platform-load-2024.pptx

Do not use a numbered "Citations" appendix table. Footnotes are
inline, scoped, and do not encourage padding.

**Internal cross-references** use anchored links, never bare
section names:

- ✅ `see [Acceptance Criteria](#acceptance-criteria)`
- ❌ `see the Acceptance Criteria section`

**External references** always include the actual URL (web URL,
SharePoint URL, ADO link), not just the document title.

### 9. Voice & craft

Specs are read by engineers and PMs who will *implement against
them*. The voice is **professional-technical**: substantive,
confident, specific, free of filler. Procedural prose ("the
following section will describe…") and decorative qualifiers
("robust", "seamless", "modern") are both out.

Adapted from
[`executive-writing-style` §"Persuasive Structure" + §"Tone Rules"](../../../../product-brief/.github/skills/executive-writing-style/SKILL.md).
The decision-maker / championing framing in that skill does NOT
apply here — spec readers are implementers, not approvers — but
the structural and tonal rules below port directly.

#### Lead with the point

Every section opens with its conclusion or key claim, not
background. Supporting evidence follows. A Problem Statement
that opens with "Historically, the team has been investigating…"
is broken; rewrite it to open with the problem itself.

#### The "so what?" test

After each paragraph, ask: *"If I deleted this, does an
implementer's understanding change?"* If no, delete it. If
maybe, tighten to one sentence.

#### Tone

| Aspect | Rule | Example |
|--------|------|---------|
| Confidence | Write recommendations as decisions, not options. | ✅ "The service publishes events via the queue." ❌ "The service could potentially publish events via the queue." |
| Honest uncertainty | When genuinely uncertain, state the range AND the reason. | ✅ "Throughput target is 4–6k req/s p95; range reflects unknown cache hit-ratio after migration." ❌ "Throughput might be reasonably high." |
| Hedging without reason | Strike "might", "could potentially", "we believe", "should be able to" unless real uncertainty exists AND is named. | — |

#### Sentence & paragraph craft

- Target 15–20 words / sentence. Hard ceiling 25.
- One idea per sentence; "and" connecting two distinct thoughts → split.
- Subject-verb-object order. Active voice by default.
- One point per paragraph, 3–4 sentences max.
- Lead sentence carries the point.

#### Word choice

- Simplest accurate word: **use** (not utilize), **start** (not
  initiate), **help** (not facilitate), **enough** (not
  sufficient), **build** (not construct).
- Replace abstractions with specifics: not "improves
  performance" but "reduces p95 latency from 800ms to 200ms".
- Cut nominalisations: "we decided" not "a decision was made";
  "we recommend" not "the recommendation is".
- Names, not pronouns: replace "it" / "they" with the named
  entity on first use of each paragraph.
- Define jargon on first use, or push to Glossary.
- Headers (`#` / `##` / `###` / `####`) carry structure. A
  bolded line that introduces a paragraph is a missing header.
- Do not hard-wrap body prose — let editors wrap.

#### Filler phrases — strike on sight

- "It is important to note that…"
- "It should be mentioned that…"
- "In order to…" → "To"
- "At the end of the day…"
- "Moving forward…"
- "Needless to say…"
- "For all intents and purposes…"

If the sentence still parses without the phrase, the phrase was
filler. Adapted from
[`executive-writing-style` Filler Phrase Blacklist](../../../../product-brief/.github/skills/executive-writing-style/SKILL.md#filler-phrase-blacklist).

#### Buzzword inflation — say what you mean

| Inflated | Plain |
|----------|-------|
| "leverage X to drive outcomes" | "use X to <outcome>" |
| "robust, scalable architecture" | (delete; cite the actual NFR) |
| "best-in-class performance" | (delete; cite the actual target) |
| "seamless integration" | "calls API X via mechanism Y" |
| "holistic approach" | (delete; describe the approach) |
| "end-to-end solution" | (delete; name the boundaries) |

Adapted from
[`executive-writing-style` Buzzword Inflation](../../../../product-brief/.github/skills/executive-writing-style/SKILL.md#buzzword-inflation).
Adjective-stacking signals the writer has nothing specific to say.

#### Length budgets

Length is a secondary control; the primary control on upper
sections is signal density (see §10). For lower sections:

- Each FR ≤ 2 sentences (one shall-statement + at most one
  clarifier). Longer FRs almost always pack two requirements
  into one — split.

For upper-section backstop caps (Problem Statement, Solution
Summary, Goals narrative, Personas narrative) see §10. The caps
there are intentionally generous; the test that matters is
whether the content earns its place by the §10 heuristics.

#### Good vs bad — Problem Statement

**BAD** (template fill-in / procedural):

> The Problem Statement section will describe the challenges
> faced by users when interacting with the existing notification
> subsystem. It is important to note that there are several
> significant pain points that impact user experience.

**GOOD** (substantive / spec voice):

> Notifications today land in a single inbox with no priority
> signal. 47% of users miss high-severity alerts within 4 hours,
> per the Q4 2025 telemetry sample (n=18,400). Support volume
> for "I missed the alert" tickets has grown 3.2× YoY.

The bad version is *procedural* (it talks about itself); the
good version is *substantive* (it states the problem and gives
the implementer numbers to design against).

#### Good vs bad — Solution Summary

**BAD**:

> We will develop a robust, scalable solution leveraging modern
> architectural patterns to deliver a seamless user experience
> across all notification surfaces.

**GOOD**:

> Add a per-notification severity field (`P0..P3`) and a
> severity-aware inbox view. P0/P1 surface in a separate top-of-
> inbox row with audible cue; P2/P3 fall back to the current
> behaviour. No changes to the publish API.

### 10. Upper-section signal density

Sections above Functional Requirements — Document Information,
Problem Statement, Goals & Success Metrics, Users & Personas,
Stakeholders & Reviewers (when gated-in), Solution Summary —
constitute the **upper sections**. They orient the reader; they
do not deliver the contract.

**The principle.** Upper sections must contain only content that
materially helps a reader understand the plan and the most
consequential decisions. Per-feature reasoning, edge cases, open
questions, per-requirement rationale, and trade-off / alternatives
discussion have canonical homes lower in the spec (FR
`*Rationale*` lines, ACs, Open Questions, Risks & Mitigations,
Technical Considerations, Alternatives Considered when
Stop-A-approved). Putting them in the upper sections is wrong not
because they exceed a budget but because **they dilute the signal
the upper sections exist to deliver**: orientation to the problem,
the chosen approach at the highest level, and the decisions that
gate everything below.

A reader who has finished the upper sections should know what is
being solved, for whom, what we are building at the highest level,
and what gates the rest of the document — and nothing more.

**Heuristics for "does this earn its place?"** Apply in order:

1. **Lower-section displacement.** Move the sentence to its
   canonical lower-section home and re-read the upper section. If
   the reader is still oriented, the sentence belonged lower.
2. **Gating.** Content that gates a downstream decision
   (`spec_kind`, complexity axes, scope boundaries, versioning
   posture, persona-driven AC variation) earns its place.
   Non-gating context does not.
3. **"So what?"** If deleting this paragraph leaves an
   implementer's grasp of the *plan* unchanged, delete it. If
   only their grasp of a *specific feature* changes, push to that
   FR.
4. **Trade-off.** "We chose X over Y because…" sentences belong
   in Risks & Mitigations or Alternatives Considered, never in
   Solution Summary.
5. **Edge case / caveat.** Hedges describing when the plan does
   not apply belong in the relevant FR / AC or Open Questions.

**Backstop word caps** (the critic enforces these as `info` /
`minor`-tier signals, not as primary findings):

| Section | Backstop cap |
|---------|--------------|
| Problem Statement | ≤ 400 words |
| Solution Summary | ≤ 350 words, up to 3 paragraphs |
| Goals & Success Metrics narrative | ≤ 200 words (table carries the weight) |
| Users & Personas narrative | ≤ 150 words |

Caps are a backstop against runaway sprawl, not the primary
control. The primary control is the signal-density principle plus
the heuristics. Expect to land far below these caps in well-
written specs; hitting a cap is a smell — re-apply the heuristics.

**Worked examples** (borderline cases, illustrating the judgment):

*Trade-off rationale in Solution Summary — push out.*

> ❌ "We will add severity (`P0..P3`). We considered a separate
> Inbox tab but rejected it because telemetry shows users dwell
> 3.4× longer on the unified inbox and a tab would require a
> separate read-state model."
>
> ✅ "Add severity (`P0..P3`); P0/P1 surface in a top-of-inbox
> row, P2/P3 retain current behaviour." Tab-vs-unified reasoning
> moves to Risks & Mitigations or Alternatives Considered.

*Capacity figure in Problem Statement — depends on gating.*

> "Median inbox session is 38s on mobile, 2.4 minutes on
> desktop." earns its place iff a downstream FR / AC differs by
> surface, or `spec_kind` was forced to `mixed` because of
> mobile-platform work. Otherwise push to a per-FR rationale or
> drop.

*Open question parenthetical in Goals — push out.*

> ❌ "Goal: 80% reduction in 90 days. (Whether the Q3 mobile
> redesign affects this baseline is being confirmed.)"
>
> ✅ "Goal: 80% reduction in 90 days." Parenthetical moves
> verbatim to Open Questions.

## Anti-patterns

| Anti-pattern | Problem | Fix |
|--------------|---------|-----|
| Vague goals like "improve UX" | Cannot tell when done | Outcome metric with baseline + target. |
| Acceptance criteria that paraphrase the requirement | Not testable | Given / When / Then with concrete inputs and observable result. |
| Fabricated quotes / data to make the problem statement vivid | Erodes trust; fails D4 | Use real evidence or mark `[TBD]`. |
| Locking on a solution before context is clear | Wastes drafting; misses the real problem | Stop A discipline + complexity heuristic. |
| "We will figure that out later" sprinkled through the doc | Hidden risk | Promote each one to `OQ-NN`. |

## Quality checklist

- [ ] Problem Statement explainable to an outsider in one paragraph.
- [ ] Every goal has baseline + target + measurement window.
- [ ] Every FR has a priority (P0/P1/P2) and is written as a single
      EARS shall-statement.
- [ ] Every AC is testable (Given / When / Then), nested under its
      FR with `AC-<FR>.<n>` IDs.
- [ ] Every external citation is a markdown footnote, links to a
      primary authoritative source, and would be useful to a
      reader.
- [ ] No citation references a gitignored or session-internal path.
- [ ] Internal cross-references use anchored links, not bare
      section names.
- [ ] Body paragraphs are not hard-wrapped; structure uses headers
      (`#` / `##` / `###` / `####`), not bolded lines.
- [ ] Open Questions section non-empty if any uncertainty exists.
- [ ] Out of Scope contains only items that pass the
      adjacency-by-language test (§7); an empty list is acceptable.
      No boilerplate "implementation details are out of scope".
