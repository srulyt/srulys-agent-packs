# Audience and Championing

A brief is a **championing tool**. The reader takes it into their own meetings and argues for the investment without the author in the room. Technical quality alone does not drive organizational decisions: a brilliant brief that stakeholders cannot easily champion internally loses to a simpler brief they can.

## Audience Calibration

Audience decides how much context each section assumes. It is independent of maturity: a mid-stage brief for a non-expert audience is common and valid.

**Ask the user when the audience is unclear.** Never guess silently. Assuming an expert reader is the single largest driver of post-draft rework.

Assess three things:

- **Domain familiarity:** does the reader already know the product area, its terms, and the surrounding systems?
- **Role and altitude:** executive decision-maker, peer team, engineering reviewer, or a mix?
- **Prior context:** is this the reader's first exposure to the initiative?

| Audience | Calibration |
|---|---|
| Expert | Assume fluency in domain terms and define only genuinely novel coined terms. Lead with the decision and keep background minimal. Aim for the tight end of the length band. |
| Non-expert / adjacent | Define every domain term briefly, inline, at first mention. Add a short "Background and current landscape" orientation (one or two paragraphs) before the problem; for this reader it is decision-critical, not filler. Explain the *why* behind each design choice. Prefer a concrete scenario to an abstract capability description. Clarity outranks brevity. |
| Mixed | Calibrate to the least-expert reader who must act on the brief. |

Defining terms and explaining rationale for a non-expert reader is not bloat. Scope every "so what?" cut to the audience: "If I deleted this, would *this reader's* decision or understanding change?"

## The Cascade Principle

Your reader is usually not the final decision-maker. They will re-pitch the proposal to their own leadership.

- Write as if the reader will present the brief in a meeting you are not in.
- The executive summary must work as a standalone verbal pitch.
- Every major section needs at least one clear, repeatable statement the reader can use in that meeting.
- If a section takes domain expertise to explain, it will die in the cascade.

**Cascade test.** Could the reader explain this section to their boss in 30 seconds without looking back at the document?

- **Yes:** the section passes.
- **No:** simplify the framing until a non-expert can relay it confidently.
- **Partly:** pull the core business outcome into one lead sentence and move the complexity into supporting detail.

## Make "Yes" Feel Safe and "No" Feel Costly

Stakeholders are measured on business outcomes and team perception, not technical delivery. Approving something they cannot explain is psychological risk with no clear reward.

- Lead with familiar business outcomes: lower cost, faster delivery, happier customers, lower risk.
- Align the proposal with what the stakeholder is already measured on.
- Show the de-risking: phasing, reversibility, early validation.
- Make the cost of inaction concrete, in business terms the stakeholder owns, and connect it to metrics they report on.
- Mention competitor or peer moves only when they are relevant and backed by evidence.

Anti-patterns:

- Arguing technical superiority without business context.
- Detail that leaves the reader anxious about defending something they cannot grasp.
- Framing that requires the reader to become a domain expert before they can advocate.

## Minimize Cognitive Burden

Simplify the framing without losing rigor. Technical depth supports the business case; it does not lead it.

- Make one core message per section. A section that makes three points leaves the reader remembering none.
- Use concrete numbers over abstractions ("40% fewer tickets," not "significant efficiency improvement"), but only when the number has a source (see `evidence.md`).
- Put plain business language in lead sentences. Technical precision can follow.
- Use a familiar analogy to introduce a novel concept.
- Give the conclusion first and the evidence second.
- Keep headings short and neutral. Dramatic headings trigger skepticism.

## Align with the Reader's Incentives

Write to what the stakeholder is measured on, not what the author is measured on.

| Author's incentive | Stakeholder's incentive | Emphasize |
|---|---|---|
| Technical correctness | The business outcomes they report on | Revenue, cost, customer satisfaction, risk |
| Comprehensive analysis | Confident decision-making | A clear recommendation with bounded risk |
| Engineering elegance | Team perception and credibility | Proven approaches, phased delivery, peer validation |
| Feature completeness | Time to value | What ships first and the impact it delivers |

For every technical benefit, ask: "What business outcome does this create for the person reading this?" For example:

- "Modular architecture" → "We can ship phase 1 in Q3 and iterate based on real usage data."
- "Improved test coverage" → "Lower risk of production incidents that disrupt customers."
- "Refactored permissions model" → "Admins can self-serve instead of filing 200 tickets per month."

## Championing Language

Each major section should contain at least one statement that is:

- **Memorable:** short enough to repeat from memory.
- **Outcome-focused:** about revenue, cost, risk, or customer impact.
- **Defensible:** backed by evidence in the brief.
- **Repeatable:** usable word for word in someone else's meeting.

The examples below are illustrative; numbers must come from the source.

| Weak | Strong |
|---|---|
| "The proposed RBAC system addresses several administrative pain points in the current architecture" | "This eliminates 200 admin escalation tickets per month and unblocks self-service for 340 admins" |
| "We recommend a phased approach to implementation" | "Phase 1 ships in Q3 and pays for itself within 90 days through reduced support load" |
| "The solution aligns with our strategic technical direction" | "Three enterprise customers have flagged this as a blocker for renewal" |

Championing language matters most for Decision Ask and Recommendation closings, but every brief should give the reader repeatable statements.

## Decision Posture

Frame the brief from the owner's actual stance in the source:

- **Settled design:** the owning team has decided. State the choice declaratively. Tradeoffs are about execution, not about whether to do it.
- **Advocacy:** the author is arguing for a direction that has not been ratified. Argue for it, with alternatives.
- **Exploratory:** the direction is still open. Present it as one option among several.

Identify who authored the source and who owns the initiative. The author is often the owning team itself, not an outside party, so frame the brief from that vantage point.
