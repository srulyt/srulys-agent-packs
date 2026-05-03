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
or equivalent.

Bad: "AC-03: The notification appears quickly."
Good: "AC-03: Given a notification is generated, when the user
opens the app within 30s, then the notification appears within
2s p95."

The critic's D4 (content-quality) penalises non-testable ACs.

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

### 8. Citation discipline

Every claim in Background / Market / Persona sections cites the
source it came from. Citations are preserved in the Citations
appendix. The drafter does not repeat factual claims without a
trace back to the context pack.

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
- [ ] Every FR has a priority (P0/P1/P2).
- [ ] Every AC is testable (Given / When / Then or equivalent).
- [ ] Every claim is cited or traceable to the context pack.
- [ ] Open Questions section non-empty if any uncertainty exists.
- [ ] Out of Scope section non-empty.
