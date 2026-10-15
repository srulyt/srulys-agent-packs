# Brief Structure

Three independent axes shape every brief:

- **Brief type** sets the purpose.
- **Maturity** sets which sections appear.
- **Audience** sets how much context each section assumes (see `audience-and-championing.md`).

A scope-brief can have any maturity and any audience.

## Brief Type

### decision-brief (default)

A decision-brief requests a decision, recommendation, action, or input. The closing section is required, using one of the five closing types below. Risks and open questions may be included.

### scope-brief

A scope-brief describes the scope of something rather than asking the reader to decide. Use it when the source frames the work as "here is what is in and out of scope" (for example an MVP boundary or a feature-area definition) and asks for no decision, approval, or formal input.

- It may omit Open Questions and the closing section. When the closing is omitted, do not manufacture a decision the source does not contain.
- Use that space for a fuller **Problem Scope** and **Solution Scope**:
  - Problem Scope covers which problem space is and is not addressed, for whom, and why it matters.
  - Solution Scope covers what the solution will and will not do, with explicit in-scope and out-of-scope items, surface by surface.
- Fold genuine unknowns into Solution Scope as explicit "out of scope / not yet decided" items instead of a separate Open Questions section.
- The executive summary ends on the scope boundary, not on an ask.

Signals that a scope-brief fits:

- The source uses words like "scope," "MVP boundary," "in/out of scope," "what we will and won't build," or "this describes, not proposes."
- There is no request for approval, funding, a go/no-go, or feedback.
- The reader's takeaway is "now I understand the boundary," not "now I must decide."

## Maturity Levels

Infer maturity from the depth and breadth of the source material, not from how the request is phrased. When in doubt, choose the lower level. A brief scoped to its maturity is a feature, not a defect. Never add sections just to make a brief look complete.

| Level | Typical source | Sections |
|---|---|---|
| Early (concept / problem validation) | Notes, a short description, or a transcript | Title, Executive Summary, Problem, Solution, Closing. Five sections is valid and complete. |
| Mid (solution shaping) | Several approaches, some risk awareness, or stakeholder concerns | Early sections, plus Justification, Options/Tradeoffs, or Risks/Open Questions, but only where the source supports them |
| Late (execution planning) | Metrics, timelines, resource estimates, dependencies, or financial models | Any of the 13 sections the source supports |

Do not force Options, Metrics, Milestones, Financials, or Risks into an early-stage brief unless the source contains that information. Closing type is independent of maturity: a late-stage brief can close with a Summary, and an early-stage brief can close with a Decision Ask.

## Canonical Section Order

The list below is a **content checklist, not a heading template**. Write natural headings (see Headings).

1. Title *(required)*
2. Executive Summary, 3–5 sentences *(required)*
3. Problem Statement, written backward from the customer or user *(required; Problem Scope in a scope-brief)*
4. Proposed Solution *(required; Solution Scope in a scope-brief)*
5. Product Justification: why this is worth doing *(optional)*
6. Options and Tradeoffs *(optional)*
7. Success Metrics and Measurement Plan *(optional)*
8. Plan, Milestones, Dependencies *(optional)*
9. Financials / Resourcing *(optional)*
10. Risks, Open Questions, Mitigations *(optional)*
11. Closing Section *(required for decision-briefs, optional for scope-briefs)*
12. FAQ *(optional)*
13. Evidence Log *(only when the user explicitly asks for it)*

An audience exception applies: for non-expert readers, a short "Background and current landscape" orientation may come before the problem (see `audience-and-championing.md`).

## Section Distinctness

Each section has one job. Overlap between sections is a defect.

With thin source material, a section that has nothing deeper than the summary must not reword it. Keep the summary to the arc. Give the Problem and Solution sections only the specifics (evidence, quotes, scope details), even if that leaves them a sentence or two. Never restate a summary sentence in different words.

| Section | Unique job |
|---|---|
| Title | Names the product. Nothing else. |
| Executive Summary | The full arc in 3–5 sentences: problem → solution → impact → ask (or scope boundary). Must not repeat the title verbatim. |
| Problem Statement | A deep dive on who hurts, why, and how badly. Goes deeper than the summary's problem sentence. |
| Proposed Solution | What will be built, in scope and out of scope. Does not re-explain the problem. |
| Product Justification | Why this and why now: strategic fit, rejected alternatives, opportunity cost. Does not restate the solution. |
| Options and Tradeoffs | The viable options compared on explicit criteria. Does not re-justify the recommendation. |
| Success Metrics | Measurable outcomes and how they are tracked. Does not restate features. |
| Plan / Milestones | Phases, dependencies, owners. Does not restate metrics. |
| Financials / Resourcing | The investment needed and the value returned. Does not restate the plan. |
| Risks / Open Questions | What could go wrong, and what is unresolved. Does not duplicate known facts. |
| Closing | Content depends on the closing type. Never a summary of the whole brief. |
| Problem Scope *(scope-brief)* | The boundary of the problem space: who is in, who is out, why it matters. Does not restate the solution. |
| Solution Scope *(scope-brief)* | In scope vs out of scope for the solution, surface by surface. Does not re-explain the problem. Listing solution exclusions under Problem Scope is an overlap defect. |
| FAQ | Questions stakeholders are likely to ask. Does not duplicate earlier sections. |
| Evidence Log | A table mapping each claim to its source. Raw references only, no narrative. |

## Section Completion Checks

- **Executive Summary:** covers what, who, why now, impact, and the decision requested (or, in a scope-brief, the scope boundary). Includes at least one memorable business-outcome statement the reader could repeat in a leadership meeting.
- **Problem:** names the customer or persona, the failing job-to-be-done, the user pain and the business pain, and the evidence behind them.
- **Solution:** states what is in scope, what is out of scope, and the high-level UX intent.
- **Justification:** covers strategic fit, alternatives, differentiation, the cost of inaction, and why now.
- **Options:** at least two viable options, including the status quo, with explicit decision criteria.
- **Metrics:** 3–7 KPIs/OKRs, each with a baseline, target, guardrail, and measurement method.
- **Plan:** phased rollout, dependencies, and owners when known.
- **Financials:** cost and value framing, using ranges when uncertain.
- **Risks:** the top risks, their mitigations, and unresolved blockers.
- **FAQ:** both customer-facing and internal execution questions.
- **Evidence Log:** each key claim mapped to a source given as a file name or descriptive reference, never a path or link.

## Closing Types

Choose exactly one closing type from the source signals. The closing heading describes its content. It is **never** the literal type label (for example, never a heading that just says "Decision Ask" or "Summary").

| Priority | Type | Use when | Must contain |
|---|---|---|---|
| P1 | **Decision Ask** | The source explicitly requests approval, funding, authorization, a choice between options, buy-in, or a go/no-go, and you can identify who decides what. | The exact decision; the scope of the commitment (resources, timeline, organizational impact); the timing, if known; what the approver gains by saying yes and risks by saying no. |
| P2 | **Call to Action** | The source asks for specific non-decision input, such as feedback, review, missing context, a dependency, or alignment. | Each ask, stated as what, from whom, and by when; why it is needed and what it unblocks; how to respond; what happens after. |
| P3 | **Recommendation** | The evidence clearly favors one direction, and no decision is requested. | The recommended approach with a one-sentence rationale; 2–3 key pieces of evidence; what changes if it is adopted vs not; the conditions it depends on. |
| P4 | **Next Steps** | The source contains an action plan, an execution roadmap, or work already approved or underway. | Ordered actions with owners when known; timeline or sequencing; dependencies and blockers; how progress will be communicated. |
| P5 | **Summary** (fallback) | The brief is exploratory or informational, with no clear direction yet. | 3–5 key takeaways; where things stand now; what would need to be true before acting; optionally, the open questions that remain. |

When more than one type has signals, the higher priority wins: Decision Ask beats everything, Call to Action beats Recommendation, Next Steps, and Summary, and so on. **Never invent a phantom ask.** If the source requests no decision, the closing must not imply one. The executive summary's last sentence must agree with the closing type.

## Headings

Headings are content-descriptive labels:

- **Short:** 2–5 words.
- **Neutral:** they name the topic and leave the argument to the content.
- **Professional:** no marketing copy or dramatic framing.
- **Non-prescriptive:** they do not tell the reader how to feel.

A simple label such as "Executive Summary" is fine.

Never produce headings that copy the checklist labels verbatim or contain instructional parentheticals. For example:

- `## Problem Statement (Backward from customer/user)`
- `## Product Justification (Why this is worth doing)`
- `## Financials / Resourcing (Decision framing)`
- `## Success Metrics & Measurement Plan`

## Missing Data

- Never omit a required section. If the evidence is missing, write `Insufficient data`, `Assumptions`, or `Open Questions` in that section.
- Include an optional section only when the source material contains relevant information. Otherwise omit it entirely. Do not infer content for it.
- Never present an unsupported claim as fact.

## Naming and Terminology

- Give anything the source has not formally named a **single provisional name**, use it consistently, and flag it as an open question ("provisional name; final naming TBD"). Never invent a confident final name, and never rotate between informal labels.
- If a proposed name collides with an existing product or is disputed, raise it as an open question rather than silently adopting it.
- Define a coined term for a novel concept at its first mention, for any audience. For non-expert readers, define every domain term and acronym at its first mention.
- Once a term is chosen, use it verbatim everywhere. Do not alternate synonyms for the same concept.
- When a name changes, update every occurrence. A partial rename is a defect.

## Standalone and Markdown Rules

The brief must read on its own:

- Use zero markdown links and zero bare URLs.
- Inline all essential information.
- Reference sources descriptively, for example "per the February 2026 admin-roles transcript."

Markdown:

- **Use headings for all structure, never bold.** A line such as `**Problem**` or `**Recommendation:**` acting as a label is a defect. If content warrants a label, it warrants a heading.
- Use H1 only for the title, H2 for sections, and H3 for subsections. Never skip a level.
- Put a blank line before and after every heading. Do not leave empty headings or multiple consecutive blank lines.
- Use `-` for every list marker.
- No inline HTML and no trailing whitespace.
