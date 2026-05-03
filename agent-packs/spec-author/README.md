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
   user ──▶     │  spec-author           │ ◀── only user-facing agent
                │  (orchestrator)        │
                └────────┬───────────────┘
                         │ task tool
        ┌────────────────┼────────────────┬────────────────┐
        ▼                ▼                ▼                ▼
 context-detective  prd-interviewer  prd-drafter      prd-critic
```

Four sub-agents, one orchestrator. Sub-agents never call each other
or themselves. `prd-interviewer` only runs on the context-missing
path.

## Two hard user-feedback stops

The orchestrator enforces two stops in code paths (state-machine
gates), not just in prose:

- **Stop A — Structure approval.** Before the drafter runs, the user
  is shown the proposed mode (`creation` | `update`), the chosen
  section set (mandatory + complexity-gated include/omit), open
  questions, and (in update mode) the proposed version bump. The
  orchestrator only advances when the user replies `APPROVE` or
  `EDIT: <changes>`. Ambiguous replies are re-prompted with a binary
  template until matched.
- **Stop B — Interview.** When `context-detective` reports unfilled
  P0 gaps, the orchestrator delegates a structured interview to
  `prd-interviewer`, presents the questions to the user, and parks
  state at `awaiting-interview-answers` until the user answers. If
  any P0 remains unanswered after one targeted retry, the drafter
  proceeds with `[TBD]` placeholders and surfaces the gaps in the
  spec's "Open Questions" section.

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
docs/personas.md.
```

Flow:

1. Orchestrator opens a session under `.spec-author/sessions/<id>/`.
2. `context-detective` synthesises a context pack and proposes the
   section set + detected mode.
3. If gaps exist → **Stop B** interview. Otherwise → **Stop A**.
4. After `APPROVE`, `prd-drafter` writes
   `artifacts/specification.md`.
5. `prd-critic` scores the draft; up to 2 revise loops, then the
   final spec path is returned.

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

Per-run state lives under `.spec-author/`:

```
.spec-author/
├── current-session.json
├── sessions/
│   └── {YYYY-MM-DD}-{8hex}/
│       ├── state.json
│       ├── context/
│       │   ├── user-request.md
│       │   ├── interview-answers.md   (Stop B path only)
│       │   └── attachments/
│       └── artifacts/
│           ├── discovery.json
│           ├── context-pack.md
│           ├── interview-questions.md (Stop B path only)
│           ├── specification.md       ← FINAL SPEC
│           ├── CHANGELOG.md           (update mode only)
│           └── spec-review.md
└── history/
```

### `state.json` schema

The full field reference and JSON Schema for the per-session state
file live in
[`.github/skills/prd-template/references/state-schema.md`](.github/skills/prd-template/references/state-schema.md).
That page is the single source of truth; this README intentionally
does not restate the field list to avoid drift.

## Evals

The companion eval pack lives at `evals/packs/spec-author/`. Six
smoke cases ship at the first cut:

1. `smoke-greenfield-context-complete` — Stop A path only.
2. `smoke-greenfield-context-missing-interview` — Stop B → Stop A.
3. `smoke-update-existing-spec` — full update-mode round trip.
4. `smoke-simple-spec-section-reduction` — adaptive sectioning.
5. `smoke-mcp-cli-graceful-degradation` — degrades cleanly when
   zero MCPs are detected.
6. `smoke-stop-a-disambiguation` — exercises the C4 binary-disambiguation
   loop at Stop A and the C5 partial-answer fallback at Stop B in a
   single end-to-end run.

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
