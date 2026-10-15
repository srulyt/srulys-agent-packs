---
name: brief-writer
description: "Create or edit a decision-grade product brief, one-pager, or decision memo for business stakeholders: audience-calibrated, championing-ready, evidence-grounded, and free of filler and AI-isms. Use when drafting, revising, tightening, or applying review feedback to a brief; not for detailed specs/PRDs, code, or general docs."
user-invocable: true
---

# Brief writer

Produce a brief the reader can re-pitch to their own leadership, without you in the room, in the reader's language and with every claim grounded in the user's sources. Follow the shape in the [template](assets/brief-template.md). Use it as a content checklist, not as a set of headings.

## Invariants

- **Audience first:** calibrate to the least-expert reader who must act on the brief. If the audience is unclear, ask before drafting. Assuming an expert reader causes the most rework. See [audience and championing](references/audience-and-championing.md).
- **Business outcomes lead:** frame each section around what the stakeholder is measured on (cost, revenue, risk, customers). Technical depth supports the outcome; it does not lead.
- **Type, maturity, closing:**
  - A **decision-brief** (the default) gets exactly one closing type, chosen by P1–P5 priority. A **scope-brief** describes boundaries and never manufactures an ask.
  - Include only the sections the source supports at its maturity. When unsure, choose the lower maturity.
  - See [structure](references/structure.md).
- **Posture:** state settled decisions declaratively, argue for proposed directions, and present open ones as options. Never invent uncertainty, and never overclaim.
- **No fabrication:** use only user-provided sources. Unsupported content becomes `Assumption`, `Open Question`, or `Insufficient data`. Unsourced numbers become qualitative or labeled estimates. Use web search, MCP tools, or internal knowledge only after the user approves, and label what they add. See [evidence](references/evidence.md).
- **Voice:**
  - Plain, confident, specific business language: 15–20 word sentences, a hard ceiling of 25, and the lead first.
  - No filler, buzzwords, or AI-isms, including writer scaffolding and metadiscourse.
  - State each caveat or evidence gap once, where it applies or in open questions. Write about the business, not about the source files or the brief itself.
  - See [writing style](references/writing-style.md).
- **Standalone document:** no links or URLs. Headings, not bold, for structure. Natural, neutral headings that never copy template labels. One name per concept.
- **Decision sections:** lead with the recommendation, then use the options, metrics, plan, and financials tables when the source supports them. See [decision framing](references/decision-framing.md).

## Working with the user

- **New brief:** read the source material. Determine the brief type, maturity, audience, closing type, and decision posture.
  - Ask only about genuine blockers: the audience, a missing decision target, or gaps that need external research.
  - Then draft directly.
- **Existing brief:** make the edits that were requested and preserve the author's decisions. Treat feedback as intent, not final copy. Propagate renames and fact changes everywhere. See [review and editing](references/review-and-editing.md).
- **Saving:** ask where to save the brief if that is unclear.

## Done when

The brief passes the [review checklist](references/review-and-editing.md) with no failures. Then tell the user:

- the file path
- the brief type, maturity, audience, closing type, and posture you used
- the word count
- the open questions and assumptions that need an owner
- any external content you added with their approval
