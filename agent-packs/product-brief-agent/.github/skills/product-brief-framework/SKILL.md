---
name: product-brief-framework
description: Framework for decision-grade product briefs with canonical section order, agency-over-formatting rules, section distinctness contract, hardcore brevity protocol, standalone document policy, and markdown lint compliance. Trigger keywords: product brief, decision memo, section order, decision ask, FAQ, evidence log, brevity, standalone.
---

# Product Brief Framework

Use this skill to enforce structure, completeness, and quality for a decision-grade product brief.

## Stakeholder Championing Principle

A product brief is not just a decision document — it is a **championing tool**. The reader must be able to use this brief to advocate for the investment in their own meetings, with their own stakeholders, without the author present.

This principle shapes every other rule in this framework:

- **Executive Summary as pitch script**: The 3–5 sentence summary must work as the reader's verbal pitch in a leadership meeting.
- **Business outcomes over technical merit**: Lead every section with the outcome the stakeholder is measured on, not the technical approach.
- **Championing language**: Every major section needs at least one memorable, repeatable statement the reader can use in their own meetings.
- **Cognitive burden minimization**: Complexity creates anxiety. Simplify the framing without losing rigor — technical depth supports the business case, it does not lead it.
- **Incentive alignment**: The brief speaks to what the stakeholder is measured on (business outcomes, team perception, customer satisfaction) not what the author is measured on (technical delivery).

## Agency Over Formatting

The canonical section list (13 items below) defines **content requirements**, not output headings. Agents must create natural, content-descriptive headings that reflect the actual substance of each section.

### Rules

- The section list is a content checklist, not a heading template
- Every heading must be specific to the brief's content
- Parenthetical guidance text must never appear in output headings

### Anti-Pattern Headings (NEVER produce)

These headings copy framework labels or include instructional text. Reject them on sight:

- `## Problem Statement (Backward from customer/user)`
- `## Product Justification (Why this is worth doing)`
- `## Financials / Resourcing (Decision framing)`
- `## Success Metrics & Measurement Plan`

Any heading that reads like a template label, includes parenthetical instructions, or matches the canonical section list verbatim is an anti-pattern. Note: anti-patterns are specifically about copying framework section labels verbatim or including instructional parentheticals — simple professional labels that neutrally name a topic area (e.g., "Executive Summary") are NOT anti-patterns.

### Required Heading Characteristics

Instead of copying examples, internalize these traits for every heading:

- **Short**: 2–5 words preferred. Headings are labels, not sentences.
- **Neutral**: Name the topic area without editorializing, signaling urgency, or presuming the reader's conclusion. The heading says what the section covers; the section content makes the argument.
- **Professional**: Use plain, direct language. No marketing copy, no dramatic framing, no academic formality.
- **Non-prescriptive**: Do not tell the reader how to feel. A heading that neutrally identifies the subject is better than one that frames a narrative conclusion.
- **Simple is good**: A clear, straightforward label that accurately names the section topic is always acceptable. Not every heading needs to be clever or content-specific — clarity and professionalism beat creativity.

## Canonical Section Order

Sections are either required (always present) or optional (included only when the user's provided source material explicitly contains relevant information). Do not generate or infer content for optional sections — omit them entirely when user context does not support them.

When included, all sections follow this fixed order:

1. Title *(required)*
2. Executive Summary — 3–5 sentences *(required)*
3. Problem Statement — backward from customer/user *(required)*
4. Proposed Solution *(required)*
5. Product Justification — why this is worth doing *(optional)*
6. Options and Tradeoffs *(optional)*
7. Success Metrics & Measurement Plan *(optional)*
8. Plan, Milestones, Dependencies *(optional)*
9. Financials / Resourcing — decision framing *(optional)*
10. Risks, Open Questions, Mitigations *(optional)*
11. Decision Ask *(required)*
12. FAQ *(optional)*
13. Evidence Log *(include ONLY when the user explicitly requests it — never auto-include)*

## Section Distinctness Contract

Each section has a unique purpose. Overlap between sections is a quality defect.

| Section | Unique Job |
|---------|-----------|
| Title | Product name as the document heading. Nothing else. |
| Executive Summary | Full arc in 3–5 sentences: problem → solution → impact → ask. Must not repeat the title verbatim. |
| Problem Statement | Deep-dive: who hurts, why, how bad. Must go deeper than the summary's problem sentence. |
| Proposed Solution | What will be built: in-scope and out-of-scope. Must not re-explain the problem. |
| Product Justification | Why this and why now. Strategic fit, rejected alternatives, opportunity cost. Must not restate the solution. |
| Options and Tradeoffs | Viable options with comparative criteria. Must not re-justify the recommendation. |
| Success Metrics | Measurable outcomes (KPIs/OKRs) and tracking methods. Must not restate features. |
| Plan/Milestones | Execution phases, dependencies, owners. Must not restate metrics. |
| Financials/Resourcing | Investment needed and value returned. Must not restate the plan. |
| Risks/Open Questions | What could go wrong and unresolved items. Must not duplicate known facts. |
| Decision Ask | Exact decision requested, scope, and timing. Must not summarize the entire brief. |
| FAQ | Anticipated stakeholder questions. Must not duplicate prior sections. |
| Evidence Log | Claim-to-source reference table (only when user explicitly requests it). Raw references only, no narrative. Sources must be user-provided external material — never `.product-brief-agent-stm/` or agent artifacts. |

## Section Completion Checks

- Executive Summary: includes what, who, why now, impact, and decision requested. Contains at least one memorable business-outcome statement the reader could repeat in a leadership meeting.
- Problem Statement: customer/persona, failing job-to-be-done, user + business pain, evidence pointers.
- Proposed Solution: in-scope, out-of-scope, high-level UX intent.
- Product Justification *(optional)*: strategic fit, alternatives, differentiation, opportunity cost of inaction, why now.
- Options and Tradeoffs *(optional)*: at least two viable options and explicit decision criteria.
- Success Metrics *(optional)*: 3–7 KPIs/OKRs with baseline, target, guardrails, and measurement approach.
- Plan/Milestones *(optional)*: phased rollout, dependencies, and owners/DRIs when known.
- Financials/Resourcing *(optional)*: key cost/value framing with ranges when uncertain.
- Risks/Open Questions *(optional)*: top risks, mitigations, unresolved blockers.
- Decision Ask: exact stakeholder decision, scope, and timing. Frames the ask in terms of what the stakeholder gains by approving and risks by not approving.
- FAQ *(optional)*: customer-facing and internal execution questions.
- Evidence Log *(only when user explicitly requests it)*: key claims mapped to source pointers (file names, not paths). Must NEVER reference `.product-brief-agent-stm/` files or agent-generated artifacts. Only user-provided external sources qualify.

## Missing Data Policy

Required sections must never be omitted. If evidence is missing for a required section, write:

- `Insufficient data`
- `Assumptions`
- `Open Questions`

Optional sections are included only when the user's provided source material explicitly contains relevant information. Do not generate or infer content for optional sections — omit them entirely when user context does not support them.

Unsupported claims must never be presented as fact.

## Hardcore Brevity Protocol

### Word Count Targets

- **Target**: 1,500–2,000 words (3–4 pages)
- **Hard ceiling**: 2,500 words (5 pages)
- Drafts exceeding the ceiling are rejected and returned for condensation

### Anti-Bloat Rules

1. No filler paragraphs that introduce the next section
2. No restating content from a previous section
3. No "in conclusion" or "to summarize" paragraphs within the body
4. Prefer a single strong sentence over three weak ones
5. Tables and lists over paragraphs when the content is structured data
6. No bridging paragraphs between sections
7. No background context that does not directly inform the decision

### Enforcement

- Brief-composer applies these rules during drafting
- Orchestrator performs a condensation editing pass after receiving the draft
- Orchestrator rejects drafts that exceed the hard ceiling

## Standalone Document Policy

The final brief must be self-contained and readable without external access.

- Zero markdown links `[text](url)`
- Zero bare URLs or hyperlinks
- All essential information inlined in the document
- Source references use descriptive text: "per the February 2026 admin-roles transcript"
- Evidence log uses file names and dates, not file paths or links

## Markdown Lint Rules

All brief output must comply with these formatting rules:

- Blank line before and after every heading
- H1 for document title only; H2 for sections; H3 for subsections
- No skipped heading levels (H1 → H2 → H3, never H1 → H3)
- Consistent list markers: use `-` throughout
- No trailing whitespace on any line
- No inline HTML
- No multiple consecutive blank lines
- No empty headings
- Do not use bold (`**text**`) for document structure; use heading tags (`#`, `##`, `###`) instead
- Bold is for emphasis only within running text, never as a substitute for headings or section labels
