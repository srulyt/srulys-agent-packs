---
name: product-brief-framework
description: Framework for decision-grade product briefs with canonical section order, agency-over-formatting rules, section distinctness contract, hardcore brevity protocol, standalone document policy, and markdown lint compliance. Trigger keywords: product brief, decision memo, section order, decision ask, closing section, recommendation, next steps, call to action, summary, FAQ, evidence log, brevity, standalone.
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

## Brief Maturity Levels

Not all product briefs are the same. Briefs exist along a maturity spectrum based on the planning phase of the proposed feature or product. The orchestrator must assess the maturity level from the depth and breadth of the user's provided source material and scope the brief accordingly.

### Early-Stage (Concept / Problem Validation)

The user has a problem, a proposed solution idea, and possibly some business justification. Source material is thin — notes, a short description, or a conversation transcript.

**Include only**: Title, Executive Summary, Problem Statement, Proposed Solution, Closing Section (type determined by context — see Closing Section Types).

Early-stage briefs most commonly use Summary or Recommendation as the closing type, but any type is valid if its signals are present in the source material.

Do NOT force sections like Options/Tradeoffs, Metrics, Milestones, Financials, or Risks unless the source material explicitly contains that information. An early-stage brief with only 5 sections is valid and complete.

### Mid-Stage (Solution Shaping)

The user has more developed thinking — there may be multiple approaches discussed, some risk awareness, or stakeholder concerns surfaced.

**Include**: All early-stage sections (including the adaptive Closing Section) plus any of: Product Justification, Options/Tradeoffs, Risks/Open Questions — but only those supported by the source material.

### Late-Stage (Execution Planning)

The user has detailed planning artifacts — metrics, timelines, resource estimates, dependencies, financial models.

**Include**: Full section set as supported by the source material, potentially all 13 sections.

### Maturity Inference Rules

- Infer the maturity from the content and depth of the provided source material, not from the user's request phrasing.
- When in doubt, default to a lower maturity level rather than padding the brief with unsupported sections.
- Never artificially add sections to make a brief look more complete. A brief scoped to its maturity level is a feature, not a defect.
- The orchestrator must explicitly state the assessed maturity level before delegation.
- The closing section type is independent of the maturity level. A late-stage brief can close with a Summary (if purely informational), and an early-stage brief can close with a Decision Ask (if the decision request is explicit even with thin evidence).

## Canonical Section Order

Sections are either required (always present) or optional (included only when the user's provided source material explicitly contains relevant information). The Closing Section (slot #11) is always required, but its type varies based on context — see the Closing Section Types section below. Do not generate or infer content for optional sections — omit them entirely when user context does not support them. See the Brief Maturity Levels section above for guidance on which optional sections are appropriate at each stage.

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
11. Closing Section *(required — type selected from: Decision Ask, Recommendation, Next Steps, Call to Action, Summary)*
    See the Closing Section Types section below for selection rules and content requirements for each type.
12. FAQ *(optional)*
13. Evidence Log *(include ONLY when the user explicitly requests it — never auto-include)*

## Closing Section Types

The closing section (slot #11 in the canonical order) resolves to exactly one of five types based on signals detected in the user's source material. The section is always required — only its type, heading, and content requirements vary.

The orchestrator performs closing type assessment after evidence extraction. The assessed type is recorded in the maturity assessment and communicated in delegation prompts to downstream agents.

Agency-over-formatting rules apply to the closing section heading — it must be content-descriptive, never a literal type label (e.g., never literally "Decision Ask" or "Summary" as a heading).

### Decision Ask

**When to use**: The source material contains an explicit decision request — funding approval, stakeholder buy-in, choosing between options, go/no-go, or any request for a formal decision from a reader with authority.

**Selection signals**:
- Source material explicitly requests approval, funding, or authorization
- Source material asks the reader to choose between defined options
- Source material frames the brief as a proposal requiring sign-off
- Language like "we need approval for," "requesting funding," "decide between," "seeking buy-in"

**Content requirements**:
- Exact decision requested (what the stakeholder must approve/decide)
- Scope of the commitment (resources, timeline, organizational impact)
- Timing/urgency (by-when, if known)
- Framed in stakeholder incentives: what they gain by approving, what they risk by not approving

### Recommendation

**When to use**: The analysis leads to a clear recommendation, but the source material does not contain an explicit decision request. The brief advocates for an approach without requiring formal approval.

**Selection signals**:
- Evidence and analysis clearly favor one option or direction
- Source material presents analysis or findings but does not ask for a decision
- The brief establishes a position but the reader is not the approver
- No explicit "approve," "fund," or "decide" language in source material

**Content requirements**:
- Clear statement of the recommended approach with one-sentence rationale
- Key supporting evidence (2–3 points max)
- What changes if the recommendation is adopted vs. not adopted
- Any conditions or dependencies for the recommendation to hold

### Next Steps / Plan of Action

**When to use**: The source material includes a concrete action plan, execution roadmap, or next-phase planning. The brief's purpose is to communicate what happens next rather than to request a decision.

**Selection signals**:
- Source material contains an execution plan, timeline, or phased rollout
- Source material describes work that is already approved or underway
- The brief is a status update, kickoff document, or planning artifact
- Language like "next steps," "action items," "implementation plan," "rollout schedule"

**Content requirements**:
- Ordered list of next actions with owners/DRIs (when known)
- Timeline or sequencing
- Key dependencies or blockers
- How progress will be communicated

### Call to Action (Non-Decision)

**When to use**: The brief needs specific input from the reader that is not a formal decision — feedback requests, additional context needed, dependency asks, collaboration invitations, or alignment requests.

**Selection signals**:
- Source material requests feedback, review, or input from stakeholders
- Source material identifies information gaps that require stakeholder input
- The brief surfaces dependency asks (other teams, external partners)
- Language like "we need your input on," "requesting feedback," "need alignment on," "please review"

**Content requirements**:
- Specific ask(s) stated clearly (what, from whom, by when)
- Why the input is needed (what it unblocks or informs)
- How to provide the input (format, channel, timeline)
- What happens after input is received

### Summary

**When to use**: The brief is informational or early-stage with no decision, recommendation, action plan, or specific call to action. This is the default fallback when no other type's signals are detected.

**Selection signals**:
- Source material is exploratory, informational, or early-stage
- No decision request, recommendation, action plan, or feedback request detected
- The brief synthesizes findings without advocating for a specific path
- The purpose is to inform rather than to persuade or request

**Content requirements**:
- Synthesis of the key takeaways (3–5 points max)
- Current state of the initiative (where things stand)
- What would need to be true before a decision or action is warranted
- Optional: open questions that remain

### Selection Logic

The closing section type is determined by priority-ordered signal detection:

| Priority | Closing Type | Signal Detection Rule |
|----------|-------------|----------------------|
| P1 | Decision Ask | Source material contains explicit decision language: "approve," "fund," "authorize," "decide between," "seeking buy-in," "go/no-go," or frames the brief as a proposal requiring stakeholder sign-off. The decision target (who decides, what they decide) must be identifiable. |
| P2 | Call to Action | Source material requests stakeholder input that is not a formal decision: feedback, review, additional context, dependency resolution, alignment. The ask must be specific (what input, from whom). |
| P3 | Recommendation | Evidence and analysis clearly favor one direction AND source material does not contain an explicit decision request (P1 signals absent). The recommendation must be supportable from evidence. |
| P4 | Next Steps | Source material contains concrete next actions, execution plans, timelines, or phased rollouts AND neither P1, P2, nor P3 signals are stronger. |
| P5 | Summary (default) | No signals for P1–P4 are detected, OR the brief is early-stage/informational with no clear direction yet. |

### Priority Resolution

When multiple closing types have signals present:

1. **Decision Ask wins over all others** — if an explicit decision is requested, that is the closing type regardless of whether recommendations, next steps, or feedback requests are also present.
2. **Call to Action wins over Recommendation/Next Steps/Summary** — a specific input request from stakeholders takes priority over passive recommendations or plans.
3. **Recommendation wins over Next Steps** — if both a recommendation and an action plan are present but no decision is requested, the recommendation is the stronger close.
4. **Next Steps wins over Summary** — concrete actions are more useful than a pure synthesis.
5. **Summary is the fallback** — used only when no other type has clear signals.

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
| Closing Section | Content depends on closing type. Decision Ask: exact decision, scope, timing. Recommendation: recommended direction with rationale. Next Steps: ordered actions with owners and timeline. Call to Action: specific input requested with context. Summary: key takeaways and current state. Must not summarize the entire brief regardless of type. |
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
- Closing Section (Decision Ask): exact stakeholder decision, scope, and timing. Frames the ask in terms of what the stakeholder gains by approving and risks by not approving.
- Closing Section (Recommendation): clear recommended direction with one-sentence rationale, key supporting evidence, and impact of adoption vs. non-adoption.
- Closing Section (Next Steps): ordered actions with owners/DRIs, timeline, dependencies, and progress communication plan.
- Closing Section (Call to Action): specific ask(s) with what, from whom, by when, why needed, and what it unblocks.
- Closing Section (Summary): 3–5 key takeaways, current state, and conditions for future decision or action.
- FAQ *(optional)*: customer-facing and internal execution questions.
- Evidence Log *(only when user explicitly requests it)*: key claims mapped to source pointers (file names, not paths). Must NEVER reference `.product-brief-agent-stm/` files or agent-generated artifacts. Only user-provided external sources qualify.

## Missing Data Policy

Required sections must never be omitted. If evidence is missing for a required section, write:

- `Insufficient data`
- `Assumptions`
- `Open Questions`

Optional sections are included only when the user's provided source material explicitly contains relevant information. Do not generate or infer content for optional sections — omit them entirely when user context does not support them.

Unsupported claims must never be presented as fact.

## External Knowledge Policy

All content in the brief must be traceable to user-provided sources. When source material is insufficient:

1. **Prefer provided context first.** Exhaust all user-provided material before considering external sources.
2. **Flag gaps explicitly.** Present the user with a clear list of what information is missing and which sections it would affect.
3. **Offer to fill from external knowledge.** The orchestrator may propose filling gaps using internal knowledge or web search, but must state the source type.
4. **Never include external knowledge without explicit user confirmation.** Wait for the user to approve each external addition before incorporating it.
5. **Label external contributions.** Any content sourced from outside the user's provided material must be noted as externally sourced in the working artifacts.

Preference order for filling gaps:

- User-provided context (always preferred)
- Ask the user for more context
- Internal knowledge (with user confirmation)
- Web search (with user confirmation)

This policy applies to all agents in the pipeline — evidence-analyst, strategy-modeler, and brief-composer must all refuse to fabricate content that lacks source backing.

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

### Headings Over Bold (Critical)

Use heading tags (`#`, `##`, `###`) for ALL document structure. Never use bold (`**text**`) as a substitute for headings, section labels, or structural elements. Bold is for inline emphasis only — to stress a word or phrase within running text.

Violation examples (NEVER produce):

- `**Problem**` followed by a paragraph — use `## Problem` instead
- `**Key Findings**` as a standalone line — use `### Key Findings` instead
- `**Recommendation:**` to introduce a block — use a heading or lead with the sentence directly

If content warrants a label, it warrants a heading. If it does not warrant a heading, it does not need a label.

### General Formatting Rules

- Blank line before and after every heading
- H1 for document title only; H2 for sections; H3 for subsections
- No skipped heading levels (H1 → H2 → H3, never H1 → H3)
- Consistent list markers: use `-` throughout
- No trailing whitespace on any line
- No inline HTML
- No multiple consecutive blank lines
- No empty headings
