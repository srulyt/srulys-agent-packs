# Output location protocol

Where the three deliverables are written. One rule decides it, and it is
decided **once**.

## Precedence

1. An explicit `Output dir:` key in the invocation prompt wins outright.
2. Otherwise the analyst's `location-proposal` block is the candidate.
3. The candidate is **always confirmed with the user** before any deliverable
   is written (see "Confirmation is mandatory").

## The analyst's `location-proposal` block

```location-proposal
proposed_path: docs/eis/access-governance
confidence: high
rationale: repo already has docs/eis/ with two sibling specs; slug derived from the feature name "Access Governance"
alternatives:
  - path: docs/specs/access-governance
    why: docs/specs/ exists but holds API specs, not experience specs
  - path: eis/access-governance
    why: no precedent in this repo
supplied_path_consistent: n/a
supplied_path_note: none
```

`proposed_path`, `confidence` and `rationale` are required and are **never
empty**. `confidence` is one of `high`, `medium`, `low`. `rationale` names the
observed evidence — an existing sibling directory, a repository convention, a
stated house style — in **one line**. "Seems sensible" is not a rationale.

`alternatives` lists up to two paths that were considered and why they lost, so
the user's confirmation is a real choice. It may be empty for a greenfield
workspace, in which case say so in the `rationale`.

`supplied_path_consistent` is `true` / `false` when the invoking prompt supplied
an `Output dir:` and the analyst validated it against the observed convention,
and `n/a` when no path was supplied. `supplied_path_note` carries the one-line
reason, or `none`. A supplied path is **validated, never overridden**.

There is no "no proposal" outcome. When no documentation convention is
detectable, propose a concrete path — `docs/eis/<feature-slug>/` is a
reasonable `confidence: low` proposal — with the rationale *"no existing
documentation convention detected"*. The orchestrator must always have
something concrete to put to the user, and in non-interactive runs the
proposal is what gets used.

### After gate 1 the block is an echo, not a proposal

On any re-invocation the task prompt carries `Location already confirmed:
<path>`. The analyst then emits **that exact path** with `confidence: high` and
`rationale: "location already confirmed for this session"`. It does not
re-infer. The block is still emitted, for schema uniformity, and because an
echo makes a later divergence detectable rather than ambiguous.

### How the location is inferred

Look, in this order, for:

1. An existing directory holding comparable specs (`docs/eis/`, `docs/specs/`,
   `docs/design/`, `specs/`). Match on *what the sibling files are*, not on
   the directory name alone.
2. The repository's documentation root and its sub-structure.
3. Where the supplied input files live — a PRD in `docs/product/` suggests
   `docs/` is the documentation root.

The leaf is a kebab-case slug of the feature name. `Access Governance` →
`access-governance`. Strip articles, keep the distinguishing words.

## Confirmation is mandatory

The location is confirmed with the user **even when `confidence` is `high`**.
It is question **#0 of gate 1**, it is asked first, and it does **not** count
against the question ceiling for that gate — it is a delivery contract, not a
discovery question.

The confirmation offers the proposed path, the top alternative if there is
one, and a free-text option.

## Write-once

`output_dir` is set exactly once, when the user confirms it (or, in
non-interactive runs, when it is assumed). After that it is **immutable for
the run**.

Any location proposal that arrives after gate 1 — from a later analyst
re-request, from a specialist, from a review round — is recorded at
`state.output_dir_proposal` and otherwise ignored. Two cases, handled
differently:

- The late proposal **echoes** the confirmed path → record it and stay silent.
  There is nothing to tell the user.
- The late proposal **diverges** from the confirmed path → record it *and*
  append a **CONCERN-level** note to `state.errors[]` naming both paths, so
  the divergence surfaces in the delivery report without moving any file.

Deliverables are never moved, copied, or re-written to a second location.

## Non-interactive runs

When `interaction_mode` is `non-interactive` the location is taken from the
prompt's `Output dir:` if present, else from the analyst's `location-proposal`
`proposed_path`. `state.output_dir_confirmed` is set to the literal string
`assumed-non-interactive`.

The delivery report then **leads** with the location — first line, before the
summary — so an unattended run's most-likely-wrong assumption is the first
thing a reader sees.

## What lands there

| File | Content |
|---|---|
| `{out}/eis.md` | Document 1 — the 22-section EIS |
| `{out}/ux-pattern-research.md` | Document 2 — the 10-section research doc |
| `{out}/decision-log.md` | Document 3 — the 6-section decision log |

Nothing else is written to `{out}`. Working state goes to
`.ux-interaction-spec-stm/runs/{session-id}/`.
