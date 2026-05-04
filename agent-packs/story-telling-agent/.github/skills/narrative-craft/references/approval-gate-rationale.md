# Approval-Gate Rationale

> Why the orchestrator's Stop-B gate (Phase 4) is non-negotiable. Loaded
> by `@story-orchestrator` when a user pushes back on the gate or asks
> why the proposal step can't be skipped.

## The Invariant

The orchestrator MUST present the proposal to the user, end its turn,
and **wait** for an explicit reply before invoking `@deck-builder`.
Building a deck without approval:

- Wastes 3–10 minutes of the user's time on a deck that may not match their intent
- Wastes ~30k–80k tokens of model spend per build
- Burns trust ("the agent built the wrong thing and didn't ask")
- Encourages users to over-specify in the initial prompt to compensate, which paradoxically reduces narrative quality

## Why Proposal-First Beats Build-First

A deck is a high-bandwidth artifact. Reviewing one requires opening
PowerPoint, clicking through 10–15 slides, and reading speaker notes.
Reviewing a proposal requires reading 1–2 pages of structured markdown.
The asymmetric cost means: any defect surfaced at proposal-review time
saves ~10× the cost of catching it at deck-review time.

## Why It Cannot Be "Skipped for Quick Asks"

Users sometimes ask: "Just build the deck — I trust you." Empirically:

- The narrative framework choice (SCR vs. Hero's Journey vs. Problem-Solution) materially changes the slide sequence; the user's first reaction to a proposal often surfaces a framework mismatch the prompt didn't reveal.
- Slide count expectations vary 2–3× per audience; only the proposal exposes this before the deck commits.
- The "So What?" test for the target audience is something only the user can validate cheaply.

If the user explicitly opts out of the gate, surface this as a session
override and document it in `state.json.errors[]` so the audit trail is
clear. The gate behavior itself is not removed.

## What the Gate Is Not

The gate is **not** a confirmation of design quality. The visual-QA
loop (Phase 6, `@deck-critic`) handles that. The proposal gate confirms
**narrative intent and slide outline**, before any python-pptx code is
written. They are two distinct gates with two distinct purposes.

## Failure Modes Without the Gate

Documented in past iterations:

- Strategist picks SCR for an investor deck where the user actually wanted Hero's Journey. Builder produces 12 slides. User rejects entirely. ~$0.50 token spend wasted, ~5 minutes of user time wasted.
- Strategist treats the goal as "inform" when the user meant "decide". Builder produces a status update where the user wanted a buy-in pitch. Total rewrite required.
- Strategist over-fills enhancing gaps via web research, citing sources the user considers untrusted. Surfaced at deck-review time, the user must skim every speaker-note for citation laundering.

All three are surfaced cheaply at the proposal gate.

## Implementation Mandate

The Stop-B Protocol in `story-orchestrator.agent.md` is the operational
form of this rationale. Pre-flight checklist:

1. Proposal presented in a **previous** message (not this turn).
2. User replied with explicit approval OR option selection.
3. `state.json.user_approved == true`.
4. `state.json.phase == "build"`.

Any failure → STOP. No exceptions; no "to save time" overrides.
