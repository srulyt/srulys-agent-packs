@spec-author write a PRD for **Workspace activity digest** — a daily
summary of changes in a product workspace.

Treat this as an early-stage idea. I have no persona doc, no spike
notes, no reference links. You will need to interview me to fill
the gaps before drafting.

When you ask me clarifying questions (Stop B), I will answer them
all. When you then propose the structure (Stop A), I will reply
`APPROVE`.

## Pre-supplied answers (do not park; proceed straight through)

This is a non-interactive run. Treat the following as already
answered — do not pause at any `awaiting-*` park. Use the answers
below verbatim where they map to your generated interview questions.

- **Stop 0 (output location):** `output_path: docs/specs/digest.md, spec_kind: mixed`
- **Stop B (interview answers) — pre-supplied:**

  ### Problem Statement
  - **Q (P0): What user pain are we solving?** — Members miss
    important changes across the workspace; scrolling individual
    channels takes too long. We have user research showing PMs and
    EMs both cite this in NPS comments.

  ### Goals & Success Metrics
  - **Q (P0): What outcome metric?** — Reduce median
    time-to-first-action on a flagged change from 45 minutes to
    under 10 minutes for >70% of digest recipients within 90 days
    post-launch.
  - **Q (P1): Business outcome?** — Increase weekly engagement
    among PM/EM cohorts by 8 points.

  ### Users & Personas
  - **Q (P0): Who are the primary users?** — PMs and Engineering
    Managers. Both want a one-shot daily summary, not a feed.

  ### Solution Summary
  - **Q (P0): What's the rough shape?** — A daily in-app
    notification at user-configurable time (default 9 AM local)
    summarising changes in the workspace they own or follow.

  ### Functional Requirements
  - **Q (P1): MVP requirements?** — (1) digest delivery; (2)
    opt-in/out; (3) time configuration; (4) per-workspace
    filtering.

  Treat the answers above as the user's **first** reply to your
  interview. They cover all P0 questions, so no second interview
  retry should be needed.

- **Stop A (structure approval):** `APPROVE` (first ask)

The orchestrator should still invoke prd-interviewer once (so the
`interview-questions.md` artifact is produced and the rubric can
check it), then immediately apply the answers above as the user's
reply (write `interview-answers.md` from the content above) and
proceed to drafting without parking for stdin.
