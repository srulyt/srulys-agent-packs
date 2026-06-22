---
name: product-brief-framework
description: "Framework for decision-grade product briefs with brief type axis (decision-brief vs scope-brief), canonical section order, agency-over-formatting rules, section distinctness contract, right-length protocol, standalone document policy, and markdown lint compliance. Trigger keywords: product brief, decision memo, scope brief, brief type, section order, decision ask, closing section, recommendation, next steps, call to action, summary, FAQ, evidence log, brevity, standalone."
---

# Product Brief Framework

Use this skill to enforce structure, completeness, and quality for a decision-grade product brief.

## Stakeholder Championing Principle

A product brief is a **championing tool**. The reader uses it to advocate for the investment in their own meetings, with their own stakeholders, without the author present.

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

## Brief Type

Maturity scopes *which* sections appear; audience scopes *how much context*; Brief Type scopes the brief's *purpose*. The orchestrator assesses Brief Type before composition and passes it to the composer. Brief Type is orthogonal to Maturity and Audience — a scope-brief may still be any maturity and any audience.

### decision-brief (default)

Requests a decision, recommendation, action, or input. The Closing Section (one of the five Closing Section Types) is **required**. Risks / Open Questions may be included.

### scope-brief

Describes the scope of something rather than asking the reader to decide. Use when the source frames the work as "here is what is in and out of scope" (e.g. an MVP boundary, a feature-area definition) and asks for no decision, approval, or formal input.

- **MAY omit** the Open Questions content and the Closing Section (Call to Action / Decision Ask). When omitted, do not manufacture a decision the source does not contain.
- **Reallocates that space** to a fuller **Problem Scope** (what problem space is and is not addressed, for whom, why it matters) and **Solution Scope** (what the solution will and will not do — explicit in-scope vs. out-of-scope, surface by surface).
- If genuine unknowns exist, fold them inline into Solution Scope as explicit "out of scope / not yet decided" items rather than a separate Open Questions section.

### Selection signals (scope-brief)

- Source says "scope," "MVP boundary," "in/out of scope," "what we will and won't build," "this describes, not proposes."
- No approval, funding, go/no-go, or feedback request is present.
- The reader's takeaway is "now I understand the boundary," not "now I must decide."

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

## Audience Calibration

Maturity scopes *which sections* appear. Audience calibration scopes *how much context each section assumes*. These are independent axes — a mid-stage brief for a non-expert audience is common and valid.

The orchestrator assesses the audience before composition and passes an `Audience Profile` to the composer. When the source material or the user does not specify the audience, the orchestrator asks. Never guess silently — assumed-expert framing is the single largest driver of post-draft rework.

### Audience dimensions to assess

- **Domain familiarity**: Does the reader already know the product area, its terminology, and the surrounding systems? Or are they an adjacent stakeholder who needs the landscape explained?
- **Role/altitude**: Executive decision-maker, peer team, engineering reviewer, or mixed.
- **Prior context**: Has the reader seen earlier material on this initiative, or is this their first exposure?

### Audience levels

**Expert audience** (knows the domain and terminology):
- Assume fluency in domain terms; define only genuinely novel coined terms.
- Lead with the decision; keep background minimal.
- Apply the tighter end of the word-count band.

**Non-expert / adjacent audience** (stakeholders without the background):
- **Define every domain term on first mention**, inline and briefly.
- Include a short **"Background and current landscape"** orientation early in the brief (one or two paragraphs) that situates the reader before the problem statement. This section is permitted even though it is "context" — for a non-expert audience it is decision-critical, not filler.
- Explain the *why* behind each design choice, not just the *what*.
- Prefer a concrete scenario/vignette over an abstract capability description when it aids comprehension.
- Typical length is relaxed for this audience (see Right-Length Protocol) — clarity for a non-expert reader outranks brevity.

**Mixed audience**: calibrate to the least-expert reader who must act on the brief.

### Calibration rules

- The orchestrator records the assessed `Audience Profile` in `maturity-assessment.md` alongside maturity and closing type.
- A "so what?" or filler cut that would remove context a *non-expert* reader needs is NOT a valid cut. Re-scope the so-what test to the assessed audience: "If I deleted this, would *this reader's* decision or understanding change?"
- Defining terms and explaining rationale for a non-expert audience is not bloat. Do not strip it during the brevity pass.

## Canonical Section Order

Sections are either required (always present) or optional (included only when the user's provided source material explicitly contains relevant information). The Closing Section (slot #11) is always required, but its type varies based on context — see the Closing Section Types section below. Do not generate or infer content for optional sections — omit them entirely when user context does not support them. See the Brief Maturity Levels section above for guidance on which optional sections are appropriate at each stage.

Section requirements also vary by Brief Type (see Brief Type). For a **scope-brief**, the Closing Section (#11) and a standalone Open Questions treatment (#10) are optional; Problem Statement (#3) and Proposed Solution (#4) expand into **Problem Scope** and **Solution Scope** with explicit in-scope vs. out-of-scope content.

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
11. Closing Section *(required for decision-briefs; optional for scope-briefs — type selected from: Decision Ask, Recommendation, Next Steps, Call to Action, Summary)*
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
| Problem Scope *(scope-brief)* | The boundary of the problem space: who is in scope, who is out, why it matters. Must not restate the solution. |
| Solution Scope *(scope-brief)* | Explicit in-scope vs. out-of-scope of the solution, surface by surface. Must not re-explain the problem. |
| FAQ | Anticipated stakeholder questions. Must not duplicate prior sections. |
| Evidence Log | Claim-to-source reference table (only when user explicitly requests it). Raw references only, no narrative. Sources must be user-provided external material — never `.product-brief-agent-stm/` or agent artifacts. |

In a scope-brief, **Problem Scope and Solution Scope must stay distinct** — one bounds the problem, the other bounds the solution. Listing solution exclusions inside Problem Scope is an overlap defect.

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

## Right-Length Protocol

A brief should be **as short as possible but no shorter**. Clarity always outranks brevity. The figures below are *typical ranges that prompt a review*, never hard caps that justify deleting load-bearing content. Brevity is audience-conditional. For a **non-expert / adjacent** audience (see Audience Calibration), clarity outranks brevity even more strongly: define terms, explain rationale, and expand length as needed.

### Typical length (review triggers, not limits)

- **Expert audience**: usually 1,500–2,500 words (≈3–5 pages). Past ~2,500, *review for filler and repetition* — do not auto-cut.
- **Non-expert / adjacent audience**: usually up to ~4,500 words; more is fine when the extra length is first-mention term definitions, background/landscape orientation, design rationale, or clarifying scenarios — never filler, restatement, or padding.
- Early-stage and thin-source briefs may be far shorter — expected and valid. Do not pad to hit a number.

### When a brief runs long

1. First remove filler, repetition, and non-load-bearing content (the "so what?" sweep and AI-ism cleanup do this).
2. If, after that, the brief is still over the typical range **and every remaining passage is load-bearing for the assessed audience, keep it.** Earned length is not a defect.
3. **Never merge two distinct concepts into one paragraph to save words.** If a passage is genuinely too dense, the fix is to *split and add explanatory text*, not to compress.
4. Re-request the composer only when over-length is caused by filler or repetition that survived the editing pass — never merely because a word count was exceeded.

### Anti-Bloat Rules

These apply at every audience level — extra length for a non-expert audience buys *clarity*, never noise:

1. No filler paragraphs that introduce the next section
2. No restating content from a previous section
3. No "in conclusion" or "to summarize" paragraphs within the body
4. Replace three weak sentences with one strong one only when they make the **same** point. Never collapse sentences that make **different** points — split them and, if needed, add a clarifying sentence.
5. Tables and lists over paragraphs when the content is structured data
6. No bridging paragraphs between sections
7. No background context that does not directly inform the decision **for the assessed audience** (for a non-expert audience, orienting background and term definitions *do* inform the decision and are retained)

### Enforcement

- Brief-composer applies these rules during drafting, calibrated to the `Audience Profile`
- Orchestrator performs a filler/repetition review pass after receiving the draft, using the audience-appropriate typical range as a review trigger
- Over-length is a signal to re-check for filler and repetition — never a reason to delete load-bearing content or merge distinct concepts

## Naming and Terminology Discipline

Naming churn and inconsistent terminology are recurring manual fixes during review. Enforce these rules so the first draft ships consistent.

### Provisional naming

- Any product, feature, or entity that the source material has not formally named must be given a **single provisional name**, used consistently, and **flagged as an open question** ("provisional name; final naming TBD").
- Never invent a confident-sounding final name and present it as settled. Never rotate between several informal labels for the same thing.
- When the source proposes a name that collides with an existing product or is under dispute, surface it as a contradiction/open question rather than silently adopting it.

### Define on first mention

- For a non-expert / adjacent audience, every domain term, acronym, or coined label is defined briefly at its first occurrence (see Audience Calibration).
- A coined term for a novel concept is defined on first mention for **any** audience.

### Terminology consistency

- Once a term or name is chosen, use it verbatim everywhere. Do not alternate between synonyms for the same concept (e.g., do not switch between "instance share" and "consumer-pays share" for the same thing).
- When a name is finalized or changed mid-draft, propagate it to every occurrence — partial renames are a defect.
- The orchestrator runs a terminology-consistency sweep during the editing pass (see the editing pass in `@brief-orchestrator`).

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

## STM Layout (Canonical Path Table)

This is the single source of truth for product-brief-agent STM paths.
Every agent in the pack references this table; do NOT duplicate it in
agent prompts.

### Pack roots

- `.product-brief-agent-stm/` — pack STM root
- `.product-brief-agent-stm/current-session.json` — active-session pointer
- `.product-brief-agent-stm/runs/{session-id}/` — per-session run directory
- Session id format: `{YYYY-MM-DD}-{8-char-hex}` (auto-generated by orchestrator; never reused)

### Per-agent directories under each run

- `.product-brief-agent-stm/runs/{session-id}/agents/brief-orchestrator/`
- `.product-brief-agent-stm/runs/{session-id}/agents/evidence-analyst/`
- `.product-brief-agent-stm/runs/{session-id}/agents/strategy-modeler/`
- `.product-brief-agent-stm/runs/{session-id}/agents/brief-composer/`
- `.product-brief-agent-stm/runs/{session-id}/agents/research-runner/`

### Canonical artifact paths

| Artifact | Path |
|----------|------|
| Evidence log | `.product-brief-agent-stm/runs/{session-id}/agents/evidence-analyst/evidence-log.md` |
| Contradictions | `.product-brief-agent-stm/runs/{session-id}/agents/evidence-analyst/contradictions.md` |
| Assumptions & open questions | `.product-brief-agent-stm/runs/{session-id}/agents/evidence-analyst/assumptions-open-questions.md` |
| Decision model | `.product-brief-agent-stm/runs/{session-id}/agents/strategy-modeler/decision-model.md` |
| Draft brief | `.product-brief-agent-stm/runs/{session-id}/agents/brief-composer/product-brief.draft.md` |
| Final brief | `.product-brief-agent-stm/runs/{session-id}/agents/brief-orchestrator/product-brief.md` |
| Handoff report | `.product-brief-agent-stm/runs/{session-id}/agents/brief-orchestrator/handoff-report.md` |
| Maturity assessment | `.product-brief-agent-stm/runs/{session-id}/agents/brief-orchestrator/maturity-assessment.md` |
| Run state (counters) | `.product-brief-agent-stm/runs/{session-id}/state.json` |
| Web research results | `.product-brief-agent-stm/runs/{session-id}/agents/research-runner/web-research.md` |
| URL fetch results | `.product-brief-agent-stm/runs/{session-id}/agents/research-runner/url-fetch.md` |
| Command execution results | `.product-brief-agent-stm/runs/{session-id}/agents/research-runner/command-results.md` |
| MCP query results | `.product-brief-agent-stm/runs/{session-id}/agents/research-runner/mcp-results.md` |

### Rules

- Only the orchestrator writes to disk. Specialists return payloads as named fenced blocks; the orchestrator persists them to the paths above (verbatim, before any editing pass).
- Verify every target path starts with `.product-brief-agent-stm/runs/{session-id}/` before writing.
- Never read or write previous run directories. Each user request starts a fresh session.
- The session id is auto-generated; never ask the user for one.
