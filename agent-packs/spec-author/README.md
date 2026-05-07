# `spec-author` — Copilot-native PRD / Specification Authoring Pack

A multi-agent pack for GitHub Copilot CLI that **authors and evolves
product specifications** (PRDs) end-to-end.

- **Creation mode** — write a new spec from a problem statement,
  transcripts, supporting docs, links, and any locally available
  MCPs / CLIs.
- **Update mode** — evolve an existing spec with first-class
  versioning, change-log, ID stability, and naming-evolution
  discipline (semver-for-specs + RFC-style headers + ADR deprecation +
  Keep-a-Changelog categories).

The pack is **fully domain-agnostic**. It ships no industry-specific
templates, names, or rules. Domain framing (regulated workloads,
specific compliance regimes, vendor-specific section names) is the
consumer's responsibility — inject it via the user prompt or
`.github/copilot-instructions.md` in the consuming repo.

## Topology

```
                 ┌────────────────────────┐
    user ──▶     │  Spec Author           │ ◀── only user-facing agent
                 │  (@spec-author)        │
                 └────────┬───────────────┘
                          │ task tool
         ┌────────────────┼────────────────┬────────────────┐
         ▼                ▼                ▼                ▼
   Context Detective  PRD Interviewer  PRD Drafter      PRD Critic
   (@context-detective) (@prd-interviewer) (@prd-drafter) (@prd-critic)
```

Four sub-agents, one orchestrator. Each agent's frontmatter `name:`
is its friendly display name; you invoke it with `@<filename-slug>`
(e.g. `@spec-author`, `@context-detective`). The two MAY differ —
`name:` is human-readable, the slug is derived from the kebab-case
filename. The orchestrator surfaces the friendly `name:` in its
user-facing messages, and `/agents` displays both. Sub-agents never call each other
or themselves. **PRD Interviewer** only runs on the
context-missing path.

## Three hard user-feedback stops

The orchestrator enforces three stops in code paths (state-machine
gates), not just in prose:

- **Stop 0 — Output location & spec kind.** Before any sub-agent
  is invoked, the orchestrator resolves the workspace path where
  the final spec will be written (`output_path`) and the spec
  kind (`product` | `technical` | `mixed`). If either is missing
  from the prompt, the orchestrator parks at
  `awaiting-output-location` and asks the user. `output_path` must
  be a repo-relative `.md` path that does not begin with
  `.spec-author/` and does not escape the workspace.
- **Stop V — Mode decision (draft vs. published).** Runs after
  Stop 0 and before context-discovery. Implements
  `versioning-discipline` §V4–V7. Resolves `Status: draft` vs.
  `published` using (1) explicit user statement, (2) git branch
  inference (delegated to `@context-detective` as a narrow
  `probe: branch-only` task), (3) previous state. When the working
  branch is trunk and the spec is still draft and the user has not
  stated mode in the current turn, the orchestrator parks at
  `awaiting-mode-decision` and presents the V6 verbatim
  `PUBLISH / KEEP-DRAFT / ABORT` prompt. Initial publish offers
  both `0.1.0` (default) and `1.0.0` per OQ-1.
- **Stop A — Structure approval.** Before the drafter runs, the
  user is shown the proposed mode (`creation` | `update`), the
  spec kind, the target output path, the chosen section set
  (mandatory + complexity-gated include / omit), open questions,
  and the versioning bump-line (one of three shapes per
  `versioning-discipline`: initial-draft creation, re-draft of
  published, or initial/redraft publish — never silent). The
  orchestrator only advances when the user replies `APPROVE` or
  `EDIT: <changes>`. Ambiguous replies are re-prompted with a
  binary template until matched.
- **Stop B — Interview.** When **Context Detective** reports
  unfilled P0 gaps, the orchestrator delegates a structured
  interview to **PRD Interviewer**, presents the questions to the
  user, and parks state at `awaiting-interview-answers` until the
  user answers. If any P0 remains unanswered after one targeted
  retry, the drafter proceeds with `[TBD]` placeholders and
  surfaces the gaps in the spec's "Open Questions" section.

## Versioning discipline (draft vs. published)

The pack enforces a two-mode lifecycle for every spec, governed by
the [`versioning-discipline`](.github/skills/versioning-discipline/SKILL.md)
skill (rules V1–V18):

- **V2 — Initial state.** Every newly created spec lands at
  `Status: draft`, `Version: 0.0.1-draft`. The drafter MUST emit
  those values verbatim — no silent starter version, even if the
  user prompt mentions one.
- **V3 — Draft invariants.** Edits in draft do NOT bump the
  version, and NO `CHANGELOG.md` entry is written until publish
  (per user OQ-5). All edits accumulate under one draft tag.
- **V8 — Publish transition.** Triggered ONLY by an explicit
  user gesture (`PUBLISH <ver>`, "publish this", "ship it"). At
  publish, the drafter strips `-draft`, freezes numbering, sets
  `Status: published`, and writes the changelog entry (aggregate
  `### Added` summary at initial publish per OQ-5; enumerated
  Keep-a-Changelog categories on subsequent publishes).
- **V9 — Post-publish stability.** Published IDs are immutable;
  removals become `[Deprecated in vX.Y]` markers in place.
- **V11 — Re-draft cycle.** Editing a published spec sets
  `<next>-draft` as the working version; prior-published IDs stay
  frozen (OQ-6 strict freeze); newly added items in the re-draft
  window may be reordered until publish.
- **V12 — Cross-reference integrity.** Every renumber/insert/
  delete updates all internal references atomically; the drafter's
  `cross-ref-audit-json` and the critic's `d6.cross-ref-integrity`
  sub-rubric (blocker) enforce this.

## Installation

Copy this pack into your repo:

```
agent-packs/spec-author/.github/agents/    →   .github/agents/
agent-packs/spec-author/.github/skills/    →   .github/skills/
```

Confirm:

```
copilot --list-agents
```

## Usage

### Creation mode (greenfield)

```
@spec-author write a PRD for "Workspace activity digest" — a daily
summary of changes in a product workspace. Personas attached at
docs/personas.md. Save to docs/specs/digest.md.
```

If you don't include a `save to <path>` / `output: <path>`
clause, the orchestrator will ask you at Stop 0. It will also
confirm whether the spec is a `product`, `technical`, or `mixed`
spec.

Flow:

1. Orchestrator opens a session under `.spec-author/sessions/<id>/`
   and resolves **Stop 0** (output path + spec kind).
2. **Context Detective** synthesises a context pack and proposes
   the section set + detected mode.
3. If gaps exist → **Stop B** interview. Otherwise → **Stop A**.
4. After `APPROVE`, **PRD Drafter** writes the spec to the user's
   chosen `output_path` (and `CHANGELOG.md` next to it in update
   mode).
5. **PRD Critic** scores the draft; up to 2 revise loops, then
   the final spec path is returned.

### Update mode

```
@spec-author update the spec at docs/specs/digest.md to add a
keyboard-shortcut FR and deprecate FR-07. Bump the version
appropriately.
```

Flow is the same plus:

- Drafter loads `prd-evolution` skill.
- The Stop A message includes the proposed semver bump
  (MAJOR / MINOR / PATCH) and the planned `Updates:` /
  `Obsoletes:` header.
- Drafter emits both `specification.md` (revised) **and**
  `CHANGELOG.md` (Keep-a-Changelog categories).
- Critic adds dimensions D5–D8 (changelog, ID-stability,
  versioning-correctness, section-stability).

### Spec format conventions

The drafter and critic enforce a small set of authoring
conventions in every generated spec:

- **EARS shall-statements for FRs.** Each Functional Requirement
  is a single shall-statement using one of the EARS patterns
  (ubiquitous, event-driven, state-driven, optional-feature,
  unwanted-behaviour, complex). See the canonical pattern catalogue:
  [`.github/skills/spec-driven-prd-best-practices/SKILL.md` §4a — EARS](.github/skills/spec-driven-prd-best-practices/SKILL.md#4a-ears--easy-approach-to-requirements-syntax).
- **Acceptance Criteria nested under their FR**, with hierarchical
  IDs `AC-<FR>.<n>` (e.g. `AC-12.1`, `AC-12.2`). There is no
  separate top-level Acceptance Criteria section.
- **Headers, not bold, carry structure.** `#` / `##` / `###` /
  `####` are used for layout; bolded lines as pseudo-headers are
  rejected.
- **No hard wraps in body prose.** Each paragraph is one logical
  line in the markdown source.
- **Footnotes are rare and high-value.** Most specs ship with
  zero footnotes. A footnote is added only when (a) the evidence
  is non-reconstructable from the spec body, (b) the source is
  authoritative AND primary (web doc / standard / RFC / ADO /
  SharePoint / vendor doc / regulation), AND (c) the reader will
  plausibly open the URL. Use markdown footnotes (`[^slug]`) —
  not a numbered "Citations" appendix or `S1, S2` scheme. Never
  cite a path the workspace's `.gitignore` matches; see
  [`.github/skills/spec-driven-prd-best-practices/SKILL.md` §8](.github/skills/spec-driven-prd-best-practices/SKILL.md#8-evidence--citation-discipline)
  for the canonical policy.
- **Anchored internal links**, e.g.
  `[Acceptance Criteria](#acceptance-criteria)` — not bare
  section names.

### Spec kind: product / technical / mixed

The orchestrator resolves a `spec_kind` axis at Stop 0:

- **`product`** *(default)* — PRD posture. Implementation-shaped
  sections (Data Model, API Contract, Capacity & Performance
  Targets, Threat Model Summary, Versioning & Deprecation Policy,
  NFR↔FR Traceability) are excluded even when their underlying
  axis fires. FRs describe externally observable behaviour only.
- **`technical`** — full engineering / SDD posture. All gated
  sections behave per the complexity heuristic.
- **`mixed`** — product-led but with a permitted "Technical
  Considerations" appendix. FRs stay product-shaped; the appendix
  carries any implementation detail.

Boilerplate "implementation is out of scope" non-goals are never
auto-added; in product / mixed mode the boundary is implicit. The
Out-of-Scope section header is mandatory but the bullet list MAY
be empty — non-goals only earn their place when surrounding spec
language would otherwise lead a reader to assume the item was in
scope.

### Adaptive sectioning

The pack does **not** mechanically reproduce a fixed section list.
The `prd-template` skill declares each section as `mandatory` or
`complexity-gated:<axis>` and ships the heuristic that decides
inclusion. Simple specs are correctly trimmed; complex specs retain
everything.

The complexity heuristic and section catalogue live entirely in the
`prd-template` skill so the drafter and critic apply identical
logic.

### MCP / CLI discovery

`context-detective` opportunistically detects MCPs and CLIs from
three sources (user prompt mentions, `.github/copilot-instructions.md`
declarations, harness runtime tool listing) and uses them when
relevant. **It never hard-fails when none are present** — it writes
`discovery.json` with `graceful_degradation: true` and proceeds with
built-in research tools only.

## Pack runtime session state

Per-run state lives under `.spec-author/`. The **final spec lands
at the user-chosen `output_path`** in the consumer workspace
(e.g. `docs/specs/<feature>.md`); the session directory keeps
research, review, and transcripts only.

```
.spec-author/
├── current-session.json
├── sessions/
│   └── {YYYY-MM-DD}-{8hex}/
│       ├── state.json                 (incl. output_path, spec_kind)
│       ├── context/
│       │   ├── user-request.md
│       │   ├── interview-answers.md   (Stop B path only)
│       │   └── attachments/
│       └── artifacts/
│           ├── discovery.json
│           ├── context-pack.md
│           ├── interview-questions.md (Stop B path only)
│           └── spec-review.md
└── history/

# The published spec + changelog are NOT in .spec-author/:
<output_path>                      ← FINAL SPEC (user-chosen path)
<changelog_path>                   ← CHANGELOG.md, sibling of <output_path> in update mode
```

### `state.json` schema

The full field reference and JSON Schema for the per-session state
file live in
[`.github/skills/prd-template/references/state-schema.md`](.github/skills/prd-template/references/state-schema.md).
That page is the single source of truth; this README intentionally
does not restate the field list to avoid drift.

## Evals

The companion eval pack lives at `evals/packs/spec-author/`.
Thirteen smoke cases ship at this cut (8 original + 5 new for
versioning-discipline):

1. `smoke-greenfield-context-complete` — Stop A path only
   (`spec_kind: product`).
2. `smoke-greenfield-context-missing-interview` — Stop B → Stop A
   (`spec_kind: mixed`).
3. `smoke-update-existing-spec` — full update-mode round trip
   (`spec_kind: technical`).
4. `smoke-simple-spec-section-reduction` — adaptive sectioning
   (`spec_kind: product`).
5. `smoke-mcp-cli-graceful-degradation` — degrades cleanly when
   zero MCPs are detected (`spec_kind: product`).
6. `smoke-stop-a-disambiguation` — exercises the C4 binary-disambiguation
   loop at Stop A and the C5 partial-answer fallback at Stop B in a
   single end-to-end run (`spec_kind: product`).
7. `smoke-product-mode-d9-scope-discipline` — exercises the new D9
   scope-discipline rubric: a product-mode prompt that smuggles
   implementation nouns (Postgres, Kafka, Redis, MongoDB) into the
   user framing must be recast into externally-observable FRs, and
   the critic must surface at least one D9 finding.
8. `smoke-evidence-discipline-no-gitignored-cite` — bait-prompts
   the drafter to cite a session-internal context-pack path under
   a gitignored directory. Asserts the published spec contains
   zero gitignored citations, no `## Appendix: Citations` table,
   and no `S1, S2` legacy scheme. Exercises the D4 evidence-
   discipline severity schedule: any such citation forces a
   `blocker` finding and a `block` verdict.
9. `smoke-creation-initial-draft-state` — V2: a newly created spec
   lands at `Status: draft`, `Version: 0.0.1-draft`. No
   `CHANGELOG.md` is written. Drafter's `version-bump-json` reads
   `kind: none-still-draft`.
10. `smoke-draft-renumber-with-cross-refs` — V12 / V13: user adds
    an FR in the middle of the draft list; successors renumber AND
    every cross-reference (`AC-<FR>.<n>`, "see FR-N", anchored
    links) is updated atomically. Drafter's `cross-ref-audit-json`
    is non-empty and `orphaned_references` is empty.
11. `smoke-main-branch-still-draft-prompt` — V5/V6: branch probe
    returns `main`, spec is `Status: draft`, the V6 verbatim
    `PUBLISH/KEEP-DRAFT/ABORT` prompt is presented, the user
    replies `KEEP-DRAFT`, and no transition occurs. Pre-merge
    reminder fires.
12. `smoke-publish-initial` — V8 / OQ-1 / OQ-5: user replies
    `PUBLISH 0.1.0`; spec front-matter flips to `Status: published`,
    `Version: 0.1.0`; CHANGELOG.md created with an aggregate
    `### Added` summary line.
13. `smoke-redraft-of-published` — V11: user edits a published spec;
    spec enters re-draft window with `<next>-draft`; published IDs
    remain frozen (OQ-6 strict); new IDs get next-available
    numbering; pre-merge reminder fires.

Together the cases cover all three `spec_kind` values (`product`,
`technical`, `mixed`) and the full draft → publish → re-draft
lifecycle.

## Tool naming alias

Inside `.agent.md` frontmatter the write capability is named `edit`
(GHCP CLI convention). Inside `evals/packs/spec-author/spec.yaml`
the same capability is named `write` (eval-engine canonical name).
These are two names for the same capability.

## License & provenance

Designed from scratch for GitHub Copilot CLI as the modern
replacement for the obsolete Roo `spec-creator` pack. No Roo content
(XML tool-call syntax, `.roomodes`, `.roo/` rule structure,
domain-specific section names) was ported.
