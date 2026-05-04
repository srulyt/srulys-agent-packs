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

### 7. Out of Scope is a section, not an afterthought

Explicit non-goals prevent scope creep and clarify what the team
is **not** signing up for. Every spec lists at least one
out-of-scope item; if you cannot think of one, the scope is
probably not yet sharp.

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

### 9. Writing for clarity

PMs, engineers, and stakeholders must be able to read a section
once and act on it. Apply these rules:

- **One idea per paragraph.** If a paragraph contains "and also",
  split it.
- **Active voice, present tense.** "The service publishes events"
  not "events will be published by the service".
- **Names, not pronouns.** Replace "it" / "they" with the named
  entity on first use of each paragraph.
- **No filler.** Strike "in order to", "it should be noted that",
  "obviously", "simply".
- **No marketing words.** Strike "seamless", "robust",
  "world-class", "magical".
- **Concrete numbers, not adjectives.** "p95 ≤ 500ms" not "fast".
- **Define jargon on first use** or push it to Glossary.
- **Headers, not bold, carry structure.** A bolded line that
  introduces a paragraph is a missing `###` header.
- **Do not hard-wrap body text.** Let the editor wrap. Hard wraps
  break diffs, table of contents, and search.
- **Lists for parallel items, prose for narrative.** Do not write
  a list of one item.
- **Length budget.** Problem Statement ≤ 250 words; Solution
  Summary ≤ 400 words; each FR ≤ 2 sentences (one shall-statement
  + at most one clarifier).

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
- [ ] Out of Scope section non-empty and contains no boilerplate
      "implementation details are out of scope" item.
