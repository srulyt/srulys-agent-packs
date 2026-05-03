---
name: prd-interview
description: "Question-bank patterns and rules for converting context gaps into a structured user interview. Defines P0/P1/P2 tagging, max-12 rule, do-not-invent-answers rule, and the partial-answer fallback (one targeted retry, then proceed with [TBD]). Triggers on: interview the user, structured PRD interview, gap questions, P0 questions."
---

# PRD Interview Patterns

This skill is loaded by `@prd-interviewer` (to author questions)
and `@spec-author` (to interpret coverage and apply the C5
partial-answer fallback).

## When to Use This Skill

Load this skill when:

- Converting `gaps-json` into a question set (interviewer).
- Applying the partial-answer fallback after the user replies
  (orchestrator).

## Question-quality rules

1. **One question per gap.** Do not bundle.
2. **Direct question form.** "What is the P95 latency target?",
   not "We will need to know the latency."
3. **Open-ended where the answer is qualitative**, multiple-choice
   where the answer space is bounded ("Is this internal-only,
   limited GA, or GA?").
4. **Group by target PRD section** so the user sees structure.
5. **Order by priority within each group.** P0 first.
6. **Never exceed 12 questions in total.** If you find yourself at
   13, drop the lowest-value P2.
7. **Do not invent answers.** If you find yourself filling in a
   placeholder while drafting the question, the answer goes in the
   interview — not in the spec.

## Priority tagging

| Tag | Meaning | Example |
|-----|---------|---------|
| **P0** | Blocker — drafter cannot fill the section without this. | "Who are the primary users? (without this, Users & Personas is empty)" |
| **P1** | Improves quality — answer makes the spec materially better. | "What latency is acceptable?" |
| **P2** | Nice — adds polish. | "Any preferred terminology for the new feature?" |

The orchestrator's C5 fallback only retries on unanswered P0
questions. P1 and P2 unanswered always go straight to "Open
Questions" without retry.

## Partial-answer fallback (C5)

After the user replies:

1. Map every answered question by the interviewer's
   `coverage-json` IDs.
2. If any P0 is unanswered AND `interview_retries == 0`:
   - Re-prompt with **only the unanswered P0 questions**, prefixed
     with one line: "Could you also answer Q3 and Q5? These block
     the spec being useful."
   - Increment `interview_retries`. Wait for the user.
3. After the single retry, if any P0 remains unanswered:
   - Tell `@prd-drafter` to fill those sections with
     `[TBD — interview question N unanswered]`.
   - Add a verbatim entry in the spec's "Open Questions" section
     referencing each unanswered P0.
4. P1/P2 unanswered → straight into "Open Questions" with no
   retry.
5. **Cap retries at 1.** `prd-interviewer` runs at most once per
   session; do not invoke it a second time.

## Anti-patterns

| Anti-pattern | Problem | Fix |
|--------------|---------|-----|
| 20 questions covering every detail | User abandons | Cap at 12; pick highest-leverage. |
| Compound questions ("What's the latency target and the rollout window?") | One half gets answered | Split into two questions. |
| Closed yes/no when the answer is qualitative | Loses information | Ask "Why?" or "What does that look like?" |
| Asking about the obvious ("What's this feature called?") | Wastes attention | Re-read inputs first. |
| Retrying P1/P2 if unanswered | Slows the user; not a blocker | Promote to "Open Questions" silently. |

## Quality checklist

- [ ] ≤ 12 questions.
- [ ] Every question tagged P0 / P1 / P2.
- [ ] Every question maps to a specific PRD section in
      `coverage-json`.
- [ ] No compound questions.
- [ ] `interview-md` and `interview-questions.md` agree
      byte-for-byte.
