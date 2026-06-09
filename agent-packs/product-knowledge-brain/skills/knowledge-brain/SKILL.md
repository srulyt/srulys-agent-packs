---
name: knowledge-brain
description: "Maintain and evolve a Product Management knowledge base / living wiki from already-extracted text. Owns the 10-step knowledge-evolution cycle and a durable STM checkpoint so a mid-cycle context compaction loses nothing; routes to consolidation, organization, and indexing specialist skills. Triggers on: knowledge base, knowledge brain, institutional memory, product wiki, consolidate knowledge, update the knowledge base, record decision, product knowledge, evolve knowledge, living wiki, organizational memory."
user-invocable: true
---

# Knowledge Brain (entry / master skill)

This is the **entry skill** for the Product Knowledge Brain plugin. It runs
on the host's **default agent** (Copilot CLI or VS Code Copilot) — there is
**no custom agent**. Load this skill first whenever a process needs to
**write to or evolve** a Product-Management knowledge base from
already-extracted text. It sequences the **10-step knowledge-evolution
cycle**, checkpoints to a durable STM between every step, and hands off to
three specialist skills by reference.

**Mission.** Turn already-extracted information into durable, evolving
**institutional memory** — a *living wiki*, not a document dump. The
knowledge base is the primary artifact; source materials are **evidence**.
Prefer **consolidation over proliferation**: the repo must get *simpler*
and *more valuable* over time. Every operation is **idempotent** and
**crash-safe**.

**Scope boundary (carried from the spec).** NOT in scope: document
ingestion, file/PowerPoint/email parsing, transcript retrieval, MCP /
external integration. All source content is assumed **already extracted
into text** by upstream tools. This skill begins at *"I have extracted
text; evolve the brain."* It writes only curated pages and evidence
**descriptors** — never raw source material.

## When to Use This Skill

Load this skill when the caller wants to consolidate extracted information
into a knowledge base, update a product wiki, record a decision, link
knowledge across product areas, refresh discovery indexes, or otherwise
evolve organizational product knowledge.

## Inputs

- **Extracted text** (required): the already-extracted information, passed
  inline by the caller or via a path the caller names. If empty or
  unintelligible, **fail safe** (see Failure Handling) — write no pages.
- **KB root** (optional): the knowledge-base root path. **Default
  `knowledge-base/`**, caller-overridable (`kb_root: <path>` or "use
  `<path>` as the knowledge base"). Record the chosen `kb_root` in the STM
  `state.json`.

## STEP 0 — Write the STM checkpoint FIRST (mandatory, unconditional)

> **Do this before reading, classifying, or analysing anything.** The very
> **first action** of every invocation — before any knowledge work — is to
> create the run directory and write BOTH `state.json` and `checkpoint.json`
> to disk. This is not optional, not deferrable, and not reserved for
> "larger" tasks. A run that does any knowledge analysis before these two
> files exist on disk is **non-conformant**.

Concretely, on every invocation, in this order:

1. Resolve `kb_root` (default `knowledge-base/`) and compute
   `input_hash = sha256(extracted-input)`.
2. Read `.product-knowledge-brain-stm/current-session.json`. **Resume** the
   open run iff its `checkpoint.json` `input_hash` AND `kb_root` match;
   **else** auto-generate a new `{YYYY-MM-DD}-{8-char-hex}` session id
   (**never prompt the user**).
3. **Immediately create** `.product-knowledge-brain-stm/runs/<session-id>/`
   and write these two files verbatim (exact relative paths — these are the
   paths evals assert on):

   - `.product-knowledge-brain-stm/runs/<session-id>/checkpoint.json`
     ```json
     { "last_completed_step": 0, "next_step": 1,
       "input_hash": "sha256:<hash>", "kb_root": "knowledge-base/",
       "step_artifact_hashes": {} }
     ```
   - `.product-knowledge-brain-stm/runs/<session-id>/state.json`
     ```json
     { "session_id": "<id>", "kb_root": "knowledge-base/",
       "cycle_phase": "step-1", "input_hash": "sha256:<hash>",
       "created_at": "<ISO-8601>", "updated_at": "<ISO-8601>" }
     ```
   Then point `current-session.json` at the run.

4. Only AFTER both files exist do you proceed to Step 1 of the cycle.

After Step 0, advance the run with a **single cheap write per step**:
re-write `checkpoint.json`, bumping `last_completed_step`/`next_step` (and
recording the step's artifact hash). It is a **tiny pointer file** — never a
copy of knowledge content — so this per-step update costs almost nothing.
`checkpoint.json` is the single source of truth for resume: you do **not**
re-read, re-emit, or re-verify already-written pages/indexes between steps.
At no point after Step 0 should the run directory lack a `checkpoint.json`;
there is no branch — not fail-safe-empty-input, not a tiny note, not a
resume — in which the cycle proceeds without it on disk.

## The 10-Step Evolution Cycle

Run these **in order** after STEP 0. Each step is **owned by a skill** and
closed by a single cheap `checkpoint.json` bump. Write `state.json` once at
STEP 0 and once at completion — **not** before every step. Persist a
planning artifact only when it carries state a resume would otherwise lose;
for a small single-note input keep the plan in **one consolidated
`plan.json`** rather than seven separate files. Do each step in a single
pass — no "write then re-read everything to re-verify" loops. Hand off to the
named specialist skill at each step. The full runbook is in
[`references/evolution-cycle.md`](references/evolution-cycle.md).

| # | Step | Owner skill | STM artifact (optional; consolidate into `plan.json`) |
|---|---|---|---|
| 1 | Receive extracted information | `knowledge-brain` | `input/extracted-input.md` |
| 2 | Classify information | `knowledge-consolidation` | `classification.json` |
| 3 | Determine affected areas | `knowledge-consolidation` | `affected-areas.json` |
| 4 | Update existing knowledge | `knowledge-consolidation` + `knowledge-organization` | `merge-plan.json` |
| 5 | Create new knowledge (only if needed) | `knowledge-organization` | `merge-plan.json` |
| 6 | Create relationships | `knowledge-organization` | `relationship-todo.json` |
| 7 | Update indexes | `knowledge-indexing` | `index-rebuild-todo.json` |
| 8 | Refactor structure if required | `knowledge-indexing` | `refactor-plan.json` |
| 9 | Remove duplication | `knowledge-consolidation` | `merge-plan.json` |
| 10 | Preserve provenance | `knowledge-organization` | page `evidence:` + change-log |

Steps 2→9 enforce **update-over-create** before any new page is written.
Contradictions found in steps 2–4 are queued in `contradiction-queue.json`
and resolved via change-log / ADR entries — **never** silent overwrites.

## STM Checkpoint Protocol (no-data-loss guarantee)

State is shared **only** through on-disk STM files under the pack-unique
root `.product-knowledge-brain-stm/` — never in conversation memory. Full
schema in [`references/stm-schema.md`](references/stm-schema.md).

1. **On invocation** (see STEP 0 above — do this FIRST): create the run dir
   and write `checkpoint.json` (`last_completed_step: 0`, `next_step: 1`)
   **and** `state.json` before any analysis. Resume an open run only if its
   `checkpoint.json` `input_hash` and `kb_root` match; else create a new
   session (auto-generate a `{YYYY-MM-DD}-{8-char-hex}` id — **never prompt
   the user** for it).
2. **After each step (the only mandatory per-step write):** bump
   `checkpoint.json` (`last_completed_step`, `next_step`) — one tiny write
   that must exist on disk at all times after STEP 0. Persist a step's
   planning artifact only if a resume would need it; consolidate into one
   `plan.json` for small inputs. Write each page/index once (single pass).
3. **At completion only:** update `state.json` to `complete`. `state.json`
   is written at STEP 0 and at completion — not redundantly before every
   step.
4. **On resume after compaction**: read `checkpoint.json`, skip completed
   steps, continue from `next_step`. Completed steps are content-hash
   keyed, so re-running one is a **no-op** (idempotent — no duplicate
   pages).
5. **On completion**: archive the run (mark `state.json` complete / move to
   `history/`) and clear the active pointer.

Write `state.json` and `checkpoint.json` as **complete files**
(read → modify → write) — never partial JSON.

## Routing to Specialist Skills (handoff by reference)

- **`knowledge-consolidation`** — steps 2, 3, 4, 9: classify into the six
  knowledge types, determine affected areas, decide
  **update / merge / correct / expand vs create**, detect contradictions,
  remove duplication.
- **`knowledge-organization`** — steps 4, 5, 6, 10: on-disk layout,
  living-page templates per knowledge type, typed relationships +
  backlinks, and the provenance / evidence schema.
- **`knowledge-indexing`** — steps 7, 8: maintain discovery indexes, apply
  refactoring heuristics at size thresholds, and generate dynamic
  specialized **index skills**. Generation is **mandatory** (it MUST emit
  `<kb-root>/_skills/<slug>-knowledge-index/SKILL.md`) when an area's
  `knowledge/` holds **> 12** concept pages, when a discovery index lists
  **> 25** pages, **or when the caller explicitly asks for a dynamic/
  specialized index skill** for a named area/domain — even if other
  thresholds are not crossed.

> **Committed deliverable.** When the caller explicitly asks for a dynamic
> index skill (or an area is already past threshold at invocation time),
> treat emitting `<kb-root>/_skills/<slug>-knowledge-index/SKILL.md` as a
> **required deliverable of this run**, not an optional end-of-cycle nicety.
> If you must abbreviate, still write this file — it is as mandatory as the
> STM checkpoint. The run is non-conformant if it completes without it.

A caller may need only one specialist (e.g. "just update the indexes"); in
that case load that skill directly. The default flow runs the whole cycle.

## Operating Boundaries (the host agent must obey these)

Copilot CLI has no runtime path-scoping, so these are enforced **in-prompt**.
The host acts within them while running this workflow.

| Permission | Allowed Paths |
|------------|---------------|
| **Read** | `<kb-root>/**`, `.product-knowledge-brain-stm/**`, this plugin's own `skills/**`, plus caller-provided extracted input |
| **Write** | `<kb-root>/**` (the knowledge base, incl. generated `_skills/`) and `.product-knowledge-brain-stm/runs/{session-id}/**` (STM) **only** |

## Must NOT

- MUST NOT write outside `<kb-root>/` or the STM run dir — no source/repo
  files, no `.github/`, no other packs.
- MUST NOT write or mutate **raw source material**. The KB stores only
  curated pages and evidence **descriptors** (it does not own ingestion).
- MUST NOT create a new page when an existing page should be updated
  (update-over-create — prefer consolidation).
- MUST NOT silently overwrite a historical decision. Preserve the
  superseded belief + rationale + evidence in the page `## Change Log` and,
  for org-level reversals, an `ADR-<nnn>`.
- MUST NOT skip an STM checkpoint between steps, or depend on in-memory
  state across steps.
- MUST NOT invent provenance. Every important claim cites an `E-<nnn>`
  evidence id; uncited claims go under `## Open Questions / Uncertainties`,
  never asserted as fact.
- MUST NOT prompt the user for a session id; auto-generate it.

## Failure Handling

- **Empty / malformed extracted input** (step 1): validate non-empty,
  intelligible input. On failure, write **no** pages, emit an
  `open_questions` note in the summary, and stop (fail safe — no partial
  corruption).
- **KB / STM divergence**: if the requested `kb_root` differs from the open
  STM session's recorded `kb_root`, start a **new** session rather than
  corrupting the prior run.

## Output Contract (the deliverable)

The completing response MUST emit this machine-parseable fenced block so
evals and downstream tooling can assert on the result:

````markdown
```knowledge-brain-summary
kb_root: <path>
session_id: <YYYY-MM-DD>-<8hex>
cycle_status: complete | resumed-complete | failed-empty-input | partial
last_completed_step: <int 0..10>
pages_created: <int>
pages_updated: <int>
relationships_added: <int>
indexes_updated: ["<index path>", "..."]
contradictions: <int>            # detected this cycle
evidence_added: ["E-<nnn>", "..."]
dynamic_index_skills: ["<kb-root>/_skills/<name>/SKILL.md", "..."]  # [] if none
open_questions: ["<note>", "..."]  # [] if none
```
````

## Quality Checklist

- [ ] STM session resumed or created; `kb_root` recorded in `state.json`.
- [ ] A checkpoint was written **before and after every** cycle step.
- [ ] Steps 2→9 preferred **update-over-create**; no near-duplicate pages.
- [ ] Pages are curated *living* articles (Current Understanding / Why /
      Open Questions / Change Log), not transcripts.
- [ ] Every important claim cites an `E-<nnn>`; evidence descriptors exist
      under `<kb-root>/evidence/`.
- [ ] Contradictions resolved via change-log / ADR — no silent overwrite.
- [ ] Affected discovery indexes and `area-index.md` refreshed (step 7).
- [ ] Final response emits the `knowledge-brain-summary` block.
