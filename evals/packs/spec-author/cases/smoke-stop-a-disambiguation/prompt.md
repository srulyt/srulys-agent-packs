@spec-author write a PRD for **Workspace activity digest** — a daily
summary of changes in a product workspace.

This is an early-stage idea. I have no persona doc, no spike notes,
no reference links. You will need to interview me to fill the gaps
before drafting.

Notes for this run:

- I will answer most of your interview questions but not all of them.
  In particular I won't have a good answer to the rollout-risk
  question even after a follow-up.
- When you propose the structure (Stop A), my first reply will be
  ambiguous. Please re-prompt me until I give you APPROVE or EDIT.

## Pre-supplied answers (do not park; proceed straight through)

This is a non-interactive run. Treat the following as already
answered — do not pause at any `awaiting-*` park. The harness
cannot supply additional turns, so the multi-turn
disambiguation/retry behaviour is **simulated** by the answers
below.

- **Stop 0 (output location):** `output_path: docs/specs/digest.md, spec_kind: product`

- **Stop B (interview answers) — pre-supplied (partial; mirrors
  the original two-turn retry: first reply covers most P0s, the
  second reply still leaves rollout-risk unanswered):**

  ### Problem Statement
  - **Q (P0): What user pain are we solving?** — Members miss
    important changes across the workspace; scrolling individual
    channels takes too long.

  ### Goals & Success Metrics
  - **Q (P0): What outcome metric?** — Reduce median
    time-to-first-action on a flagged change from 45 minutes to
    under 10 minutes for >70% of digest recipients within 90 days
    post-launch.

  ### Users & Personas
  - **Q (P0): Who are the primary users?** — Product managers and
    engineering managers who own one or more workspaces.

  ### Solution Summary
  - **Q (P0): What's the rough shape?** — A daily in-app
    notification at user-configurable time summarising changes in
    followed workspaces.

  ### Rollout & Risk
  - **Q (P0): What is the rollout risk and what mitigations
    apply?** — *(no answer — I don't have a good answer for this
    even after a retry; please proceed with a `[TBD - interview
    question rollout-risk unanswered]` placeholder and an Open
    Questions entry, exercising the C5 partial-answer fallback.)*

  Treat this as the user's reply after exactly one interview
  retry: `interview_retries == 1`, `prd-interviewer` runs exactly
  once, the rollout-risk P0 stays unanswered.

- **Stop A (structure approval) — simulated disambiguation
  (collapsed because the harness is single-turn):** consider the
  user to have replied with two ambiguous strings (`looks fine`,
  then `maybe?`) followed by `APPROVE`. Set
  `stop_a_disambiguation_attempts == 2` in `state.json` and then
  proceed as if the final reply was `APPROVE`. Do NOT pause for
  stdin — apply the disambiguation accounting and continue.

Proceed end-to-end without waiting for further user input. The
final spec must contain a `[TBD - interview question
<rollout-risk> unanswered]` placeholder and an Open Questions
entry referencing the unanswered P0; no `CHANGELOG.md` should be
written (creation mode).
