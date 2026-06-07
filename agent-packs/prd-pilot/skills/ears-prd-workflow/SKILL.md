---
name: ears-prd-workflow
description: "Master workflow for producing a high-quality EARS-style PRD fast, as a skills-only plugin with no custom agent. Owns the 4-step flow (gather context, grill, propose outline, format) and the outline-approval loop. Triggers on: write an EARS PRD, EARS spec, draft a requirements doc, spec authoring, PRD, requirements syntax, product requirements document."
argument-hint: "<feature or PRD topic>"
user-invocable: true
---

# EARS PRD Workflow (entry / master skill)

This is the **entry skill** for the lightweight EARS PRD plugin. It runs
on the host's **default agent** (Copilot CLI or VS Code Copilot) — there
is no custom agent. When the user asks to write an EARS PRD (or invokes
the `/prd-pilot:ears-prd-workflow` slash command), load this skill
first; it sequences four steps and hands off to three step specialist
skills by reference.

**Design philosophy: speed and low friction over first-pass
completeness — iteration is expected.** The one deliberate exception is
**step 2 (grill me)**, which prioritises *completeness of context* over
speed because a high-quality EARS PRD depends on closing every
requirement gap. Steps 1, 3, and 4 stay lean.

This is a lighter re-imagining of the multi-agent `spec-author` pack. It
keeps that pack's **quality bar** (EARS conventions, testable acceptance
criteria, P0/P1/P2 priority, open-questions discipline, evidence
discipline) and drops its heavyweight machinery (5 agents, Stop gates,
`state.json` sessions, version/changelog discipline, critic scoring
loop).

## When to Use This Skill

Load this skill when the user wants to author, draft, or format a PRD /
requirements document, especially in EARS shall-statement style.

## The 4-Step Flow

Run these in order. Hand off to the named skill at each step.

1. **Gather context** → load **`prd-context-gathering`**. Detect the
   available tools (fs-search, web-search, any `mcp_*` server), build a
   short in-conversation context digest, and degrade gracefully when
   tools are missing. Do **not** create files for this — findings stay
   in the conversation.
2. **Grill me** → load **`grill-me-interrogation`**. Run a thorough
   "grill me"-style interrogation that closes **every** requirement gap
   blocking a good EARS PRD. **There is no upper cap on questions** —
   keep asking until all gaps are closed or explicitly deferred. Pose
   questions via the built-in **ask-question (`ask_user`)** tool.
3. **Propose a very short outline** (this skill owns the loop — see
   below). Present the **canonical mandatory section names** from the
   `ears-prd-format` catalogue (Document Information, Problem Statement,
   Goals & Success Metrics, Users & Personas, Solution Summary,
   Functional Requirements, Risks & Mitigations, Open Questions, Out of
   Scope) plus a one-line intent each, and ask for approval. The outline
   may add sub-bullets, but the nine canonical section names MUST appear
   verbatim — do **not** rename or substitute them. **Do not draft the
   PRD until the user approves.**
4. **Format the final document** → load **`ears-prd-format`**. Produce
   the PRD using EARS shall-statements, nested testable acceptance
   criteria, the mandatory section catalogue, and the pre-present
   self-check. **Emit the COMPLETE formatted PRD CONTENT INLINE in your
   final assistant response** — every mandatory section, every FR
   shall-statement, and every Given/When/Then AC must be fully written
   out in the message itself. Writing the same content to the
   user-named output path is **optional and additional**; a file path
   pointer (e.g. "PRD written to X.md") is **never** a substitute for
   the inline content. If you also save a file, the inline PRD and the
   file MUST be identical.

## Step 3 — Outline-Approval Loop (this skill owns it)

No file state is used. The conversation history *is* the state.

1. After steps 1–2, present the outline as a **short bullet list**
   (section name — one-line intent) using the **nine canonical
   mandatory section names verbatim** (see `ears-prd-format`) and emit
   the `prd-outline` block (see Output Contract) with
   `status: proposed`. Then ask, via `ask_user`:

   > "Approve this outline, or tell me what to change?"
   > choices: ["Approve — draft the PRD", "Request changes"]

   Use `allow_freeform: true` so the user can describe changes inline.
2. **If approved** → proceed to step 4 (format).
3. **If rejected** → capture the user's feedback (it is the loop's only
   "state"), re-run **only the minimal slice** of steps 1–2 needed to
   address that feedback (re-grill just the touched gaps), and
   re-present a revised outline with `revisions_used` incremented.
4. **Loop bound**: at most **2 outline revisions** (3 presentations
   total). On the 3rd rejection, draft the PRD anyway from
   best-available context, mark contested areas `[TBD — reason]` with
   matching `OQ-NN` Open Questions, emit the outline with
   `status: forced-complete`, and tell the user the outstanding
   disagreements are recorded as Open Questions.

This bound prevents an infinite outline loop.

## Operating Boundaries (the host agent must obey these)

Copilot CLI has no runtime path-scoping, so these are enforced
in-prompt. The host agent acts within them while running this workflow.

| Permission | Scope |
|------------|-------|
| **Read** | workspace files (`read`/`search`), the web (`web`), any `mcp_*` tool the environment exposes, this plugin's own skills. |
| **Write** | the PRD is **always rendered inline** in the response; **optionally** also saved to the user-named output PRD path (the only allowed file write). |

## Must NOT

- MUST NOT ship or rely on a custom `.agent.md` file — this is a
  skills-only plugin; the host is the default agent.
- MUST NOT create a `state.json`, session directory, or artifacts dir.
- MUST NOT write scratch, companion, or digest files. The **only**
  allowed file write target is the user-named output PRD path, and that
  write is **optional** — the full PRD MUST always be returned inline in
  the response regardless of whether a file is written. A file-path
  pointer alone (without inline content) is a contract violation.
- MUST NOT replace the inline PRD with a reference to an external file.
- MUST NOT draft the PRD before the user approves the outline.
- MUST NOT exceed **2 outline revisions** before forced completion.
- MUST NOT invent answers to fill the spec — unknowns become
  interrogation questions (step 2), then `[TBD — reason]` + `OQ-NN`.

## Graceful Degradation (pointer)

Tool availability is never guaranteed. `prd-context-gathering` (step 1)
owns the graceful-degradation contract: record what was skipped, proceed
with built-ins, **never hard-fail**. Surface skipped tools to the user
in the `degraded_tools` field of the final `prd-summary` block.

## Output Contract (the deliverable)

The host agent's **final response** that completes the workflow MUST
contain the **full PRD content inline** plus two machine-parseable
fenced blocks so evals and downstream tooling can assert on the result.

**The complete formatted PRD MUST appear inline in the response text** —
all nine mandatory sections, every EARS shall-statement FR, and every
Given/When/Then acceptance criterion rendered in full. A pointer to an
external file (e.g. "PRD written to foo.md") does **not** satisfy this
contract; the content itself must be present and verifiable in the
message. Saving the same content to `output_path` is optional and
additional.

The `prd-outline` block is emitted **at step 3** (before drafting) with
`status: proposed` for the approval gate, and **re-emitted at
completion** with the final `status`.

````markdown
```prd-outline
- <Section Name> — <one-line intent>
- ...
status: proposed | approved | forced-complete
revisions_used: <int 0..2>
```

```prd-summary
output_path: <user-named PRD path>
fr_count: <int>
ears_valid: <int passing>/<int total>
open_questions: <int>
degraded_tools: ["<tool>", "..."]   # empty list if all expected tools used
```
````

The PRD body itself is rendered **inline** in the final response using
the `ears-prd-format` section catalogue and EARS conventions, and is
**optionally also** written to `output_path`. The inline content is the
authoritative deliverable; the file (if any) must be identical.

## Step Specialist Skills (handoff by reference)

- **`prd-context-gathering`** — step 1: tool detection + graceful
  degradation.
- **`grill-me-interrogation`** — step 2: no-cap gap-closing
  interrogation via `ask_user` (multiple-choice vs. freeform).
- **`ears-prd-format`** — step 4: EARS patterns, section catalogue,
  self-check (the quality bar).

## Quality Checklist

- [ ] All 4 steps run in order; step 2 favours completeness over speed.
- [ ] Outline presented (and `prd-outline` emitted) **before** drafting,
      using the nine canonical mandatory section names verbatim.
- [ ] Outline-approval loop respected; ≤ 2 revisions; forced completion
      on the 3rd rejection.
- [ ] The **complete PRD is rendered inline** in the final response (all
      9 sections, EARS FRs, Given/When/Then ACs); any file write is an
      identical optional copy, never a substitute.
- [ ] Final response emits both `prd-outline` and `prd-summary` blocks.
- [ ] No invented answers; unknowns are `[TBD — reason]` + `OQ-NN`.
