# Evolution Cycle — Full Runbook (idempotent)

Overflow reference for `knowledge-brain/SKILL.md`. This is the detailed,
deterministic, **resumable** runbook for the 10-step knowledge-evolution
cycle. Every step is bracketed by an STM checkpoint (see
[`stm-schema.md`](stm-schema.md)). On resume after compaction, skip any step
whose artifact already exists for the current `input_hash` and continue
from `next_step`. Re-running a completed step is a **no-op**.

## Pre-flight (STEP 0 — before step 1, mandatory and unconditional)

The **first action** of every invocation, before any classification or
knowledge analysis, is to create the run directory and write BOTH
`checkpoint.json` and `state.json`. Do not defer this. Do not proceed to
step 1 until both files exist on disk.

1. Resolve `kb_root` (default `knowledge-base/`; honor a caller override).
2. Read `.product-knowledge-brain-stm/current-session.json`. Compute
   `input_hash = sha256(extracted-input)`.
3. **Resume vs new session**:
   - Resume the open run iff its `checkpoint.json` `input_hash` matches AND
     its recorded `kb_root` matches → jump to `next_step`.
   - Otherwise create a new run: generate `{YYYY-MM-DD}-{8-char-hex}`, create
     `.product-knowledge-brain-stm/runs/<session-id>/`, and **immediately
     write both files** (exact relative paths — evals assert on them):
     - `.product-knowledge-brain-stm/runs/<session-id>/checkpoint.json` =
       `{ "last_completed_step": 0, "next_step": 1, "input_hash": "sha256:…",
       "kb_root": "knowledge-base/", "step_artifact_hashes": {} }`
     - `.product-knowledge-brain-stm/runs/<session-id>/state.json` with
       `kb_root`, `cycle_phase: "step-1"`, `input_hash`.
     Then update `current-session.json` to point at it.
4. If `<kb-root>/` does not exist, scaffold the baseline layout (see
   `knowledge-organization/references/repo-layout.md`): `README.md`,
   `index.md`, `indexes/`, `evidence/`, `areas/`.

`checkpoint.json` MUST exist on disk from this point onward and is bumped by
**one tiny write** after every step (just `last_completed_step`/`next_step`
+ the step's artifact hash — never knowledge content). There is **no** branch
(including `failed-empty-input`) that proceeds without it — STEP 0 runs
before input validation, so even a fail-safe exit leaves the checkpoint on
disk.

**Runtime discipline (keep a correct cycle cheap).** `state.json` is written
once at STEP 0 and once at completion — not before every step. The per-step
planning JSON files below are **optional working notes**: for a small
single-note input keep one consolidated `plan.json` instead of seven files,
and persist a separate artifact only when its absence would break a resume.
Write each page, evidence descriptor, and index **once, in a single pass** —
do not re-open already-written files to "re-verify" them between steps; the
checkpoint pointer is the resume source of truth.

## Step 1 — Receive extracted information (`knowledge-brain`)

- **Validate**: input must be non-empty and intelligible. On empty/garbled
  input → set `cycle_status: failed-empty-input`, emit an `open_questions`
  note, write **no** pages, stop. (Failure mode 6 — fail safe.)
- Persist the incoming text verbatim to `input/extracted-input.md`.
- Checkpoint: `last_completed_step: 1`, `next_step: 2`.

## Step 2 — Classify information (`knowledge-consolidation`)

- Load `knowledge-consolidation`. Classify each distinct claim/entity into
  one or more of the six knowledge types (Product, Customer, Competitive,
  Organizational, Research, Strategic) — see
  `knowledge-consolidation/references/knowledge-types.md`.
- Extract entities (features, personas, segments, competitors, goals,
  decisions, research findings) and candidate evidence sources.
- Write `classification.json`:
  `{ "claims": [ { "text", "types": [...], "entities": [...],
  "evidence_source": "<source descriptor>" } ] }`.
- Checkpoint: `last_completed_step: 2`, `next_step: 3`.

## Step 3 — Determine affected areas (`knowledge-consolidation`)

- For each classified claim, locate the product area(s) and existing
  page(s) it touches. Search `<kb-root>/areas/*/knowledge/` and the
  cross-cutting dirs (`personas/`, `segments/`, `strategic/`,
  `competitive/`, `decisions/`).
- Write `affected-areas.json`:
  `{ "touched_pages": ["<rel path>"], "candidate_new": [ { "concept",
  "area", "type" } ], "new_areas": ["<area-slug>"] }`.
- Checkpoint: `last_completed_step: 3`, `next_step: 4`.

## Step 4 — Update existing knowledge (`knowledge-consolidation` + `knowledge-organization`)

- For each touched page, decide **update / merge / correct / expand**
  (prefer this over creating). Detect contradictions against the page's
  current understanding; queue them in `contradiction-queue.json` (see
  `knowledge-consolidation/references/contradiction-changelog.md`).
- Load `knowledge-organization` to apply the page template and write the
  updated page: refresh `## Current Understanding`, append a `## Change
  Log` entry (newest first) for any changed/superseded belief with
  rationale + evidence, bump `updated:`.
- Record decisions in `merge-plan.json`:
  `{ "updates": [ { "page", "action": "update|merge|correct|expand",
  "supersedes": "<old belief|null>" } ], "creates": [...] }`.
- Checkpoint: `last_completed_step: 4`, `next_step: 5`.

## Step 5 — Create new knowledge (only if needed) (`knowledge-organization`)

- Create a page **only** when no existing page can absorb the claim (per
  `merge-plan.json.creates`). Use the living-page template for the claim's
  knowledge type (`knowledge-organization/references/page-templates.md`).
- Place it product-centrically: area concepts under
  `areas/<area>/knowledge/<slug>.md`; cross-cutting concepts under the
  matching root dir. Scaffold a new `areas/<area>/` (with `area-index.md`
  and sub-dirs) if the area is new.
- Append created paths to `merge-plan.json`.
- Checkpoint: `last_completed_step: 5`, `next_step: 6`.

## Step 6 — Create relationships (`knowledge-organization`)

- Add typed edges to each touched/created page's front-matter
  `relationships:` and inline `[[...]]` wiki-links; ensure backlinks are
  reflected in each target's `## Related` (see
  `knowledge-organization/references/relationships-provenance.md`).
- Write `relationship-todo.json`:
  `{ "edges": [ { "from", "rel", "to" } ] }`.
- Checkpoint: `last_completed_step: 6`, `next_step: 7`.

## Step 7 — Update indexes (`knowledge-indexing`)

- Load `knowledge-indexing`. Refresh every discovery index touched by this
  cycle (`indexes/*.md`) and the relevant `areas/<area>/area-index.md` and
  repo-wide `index.md` so each references the new/updated page with a path
  + one-line **why it matters** (see
  `knowledge-indexing/references/index-schema.md`).
- Write `index-rebuild-todo.json`: `{ "indexes": ["<path>"] }`.
- Checkpoint: `last_completed_step: 7`, `next_step: 8`.

## Step 8 — Refactor structure if required (`knowledge-indexing`)

- **First (step 8a, unconditional check):** evaluate the dynamic-index-skill
  triggers — an area's `knowledge/` with **13+** concept pages, a discovery
  index with **26+** pages, **or an explicit caller request** for a
  dynamic/specialized index skill. If any fires, **immediately write** the
  file to `<kb-root>/_skills/<name>-knowledge-index/SKILL.md` (with a
  double-quoted `description`) before any other refactoring — do not defer
  it to a closing note (`knowledge-indexing/references/
  dynamic-index-skills.md`). This generation is **not** subject to the
  "favor stability" hedge; an explicit request or a clearly-crowded area is
  always sufficient. Idempotently regenerate if it already exists.
- **Then (step 8b, threshold-gated):** apply the remaining refactoring
  heuristics (`knowledge-indexing/references/refactoring-heuristics.md`):
  split oversized pages, merge duplicates, introduce new
  categories/hierarchies, rebuild affected indexes.
- Write `refactor-plan.json`:
  `{ "splits": [...], "merges": [...], "new_categories": [...],
  "dynamic_index_skills": ["<path>"] }`.
- Checkpoint: `last_completed_step: 8`, `next_step: 9`.

## Step 9 — Remove duplication (`knowledge-consolidation`)

- Final consolidation pass: detect near-duplicate pages produced this cycle
  or pre-existing, merge them (preserving both pages' evidence + change
  logs), and mark the retired page `status: superseded` with a pointer —
  never hard-delete a page that carried decisions.
- Append merges to `merge-plan.json`.
- Checkpoint: `last_completed_step: 9`, `next_step: 10`.

## Step 10 — Preserve provenance (`knowledge-organization`)

- Ensure every important claim cites an `E-<nnn>` evidence id inline
  (`[^E-031]`) and in the page front-matter `evidence:` list. Create an
  evidence descriptor `<kb-root>/evidence/E-<nnn>.md` per **source
  document** (one descriptor per source; per-claim inline citations) with
  source type, date, and a one-line summary — **not** the raw source.
- Uncited claims move to `## Open Questions / Uncertainties`.
- Checkpoint: `last_completed_step: 10`, `next_step: done`.

## Post-cycle

1. Mark `state.json` `cycle_phase: "complete"`; archive the run; clear the
   active pointer in `current-session.json`.
2. Emit the `knowledge-brain-summary` block (see the SKILL.md Output
   Contract) tallying pages created/updated, relationships, indexes,
   contradictions, evidence ids, dynamic index skills, and open questions.

## Idempotency invariants (must hold)

- Re-feeding identical input (same `input_hash`) resumes/completes the same
  run; it does **not** create duplicate pages.
- Re-running any completed step is a no-op (artifact already present).
- All page writes are update-over-create; the repo simplifies over time.
- All decision history is append-only (change-logs + ADRs).
