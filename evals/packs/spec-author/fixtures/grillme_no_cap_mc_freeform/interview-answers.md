# Scripted interview answers (grill-me: no-cap MC/freeform)

The orchestrator parks at `awaiting-interview-answers`; the scripted
user supplies these as the reply to the grill-me question set. Answers
are grouped by target section; the orchestrator maps them onto the
interviewer's questions. For any multiple-choice question, the scripted
user picks a concrete option (never "Not sure / decide later") so the
loop closes without residue.

## Problem Statement
- What user pain are we solving? — Team members lose track of tasks
  reassigned to them across projects; there is no single place that
  shows "what changed for me". Support tickets and interviews both
  cite this.

## Goals & Success Metrics
- What outcome metric? — Reduce median time-to-acknowledge a
  reassigned task from 6 hours to under 1 hour for >70% of active
  users within 90 days.

## Users & Personas
- Who are the primary users? — Individual contributors (task
  assignees) and team leads (who reassign work).

## Solution Summary
- Rough shape? — A per-user "assigned to me" activity list updated in
  near-real-time, with configurable notification frequency.

## Functional Requirements
- MVP requirements? — (1) list of items assigned to the current user;
  (2) mark-as-acknowledged; (3) notification frequency setting
  (immediate / hourly digest / daily digest); (4) filter by project.

## Non-Functional / Rollout / Other
- Notification frequency options? — immediate, hourly digest, daily
  digest.
- Rollout? — single-team internal first, then GA; no kill switch
  needed.
- Any regulatory regime? — none.
