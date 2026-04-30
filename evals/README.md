# `evals/` — this repo's evaluation configuration and history

This directory holds **the evals**: the declarative specs, test cases,
captured evidence, and historical run records for the multi-agent
Copilot CLI packs in this repository. The framework that runs them
lives under [`../eval_engine/`](../eval_engine/) and is repo-agnostic.

## Layout (pack-centric)

Every pack owns one directory; everything about that pack lives inside it.

```
evals/
├── README.md           operator quick-start (this file)
├── docs/               authoring guide and how-tos
├── packs/<pack>/       EVERYTHING about one pack
│   ├── README.md       what this pack's evals cover
│   ├── spec.yaml       pack contract — agents, scopes, contracts, rubrics
│   ├── cases/<case>/   case.yaml + prompt.md + inputs/ + golden/ + hooks/
│   ├── fixtures/<case>/<session>.json   captured runs (committed)
│   ├── results/runs.jsonl               promoted history (committed)
│   ├── results-local/                   local-only history (gitignored)
│   ├── reports/                         markdown verdicts (gitignored)
│   └── workspaces/                      per-run SUT sandboxes (gitignored)
└── data/               cross-pack scratch (all gitignored)
    ├── judge-manifests/, judge-responses/, golden-staging/, repo-cache/
```

For the full element-by-element spec and how to author each file, see
[`docs/authoring-guide.md`](docs/authoring-guide.md). For per-pack details
see each pack's `README.md`.

## Packs covered

| Pack | Spec | Cases | Pack notes |
|------|------|-------|------------|
| `copilot-factory` | [`packs/copilot-factory/spec.yaml`](packs/copilot-factory/spec.yaml) | [`smoke-create-issue-triage-pack`](packs/copilot-factory/cases/smoke-create-issue-triage-pack/) | [README](packs/copilot-factory/README.md) |
| `product-brief` | _spec pending_ | — | — |
| `story-telling-agent` | _spec pending_ | — | — |
| `code-intelligence-agent` | _spec pending_ | — | — |

## Operator workflow (this repo)

The framework supports two capture modes:

* **Local CLI** (recommended for fast iteration): launch the SUT with
  `copilot -p ... --name <run-id>` and let `capture-local` parse the
  resulting process log into a fixture. No cloud agents needed.
* **Cloud session** (for sessions launched in the Copilot Cloud Agent):
  invoke `@eval-runner` to query `session_store_sql` and write the
  fixture manually.

### A — Local CLI capture (fully scripted)

```powershell
$pack    = 'copilot-factory'
$case    = 'smoke-create-issue-triage-pack'
$runId   = (Get-Date -Format 'yyyy-MM-ddTHH-mm-ssZ') + '-' + ([guid]::NewGuid().ToString().Substring(0,6))
$caseDir = "evals/packs/$pack/cases/$case"

# 1) Stage workspace
python -m eval_engine.harness.run plan `
  --spec evals/packs/$pack/spec.yaml --case $caseDir/case.yaml --run-id $runId

# 2) Run the SUT non-interactively in the staged workspace
$ws       = "evals/packs/$pack/workspaces/$case/$runId"
$prompt   = Get-Content "$ws/_runstate.prompt.md" -Raw
Push-Location $ws
copilot -p $prompt --agent $pack --allow-all-tools --allow-all-paths `
        --no-ask-user --name $runId 2>&1 | Tee-Object _sut-stdout.log
Pop-Location

# 3) Capture local process log → fixture
python -m eval_engine.harness.run capture-local `
  --pack $pack --case $case --run-id $runId

# 4-6) Judge + score (same as cloud flow below)
```

### B — Cloud session capture (operator-driven)

```powershell
# 1) Stage workspace + emit operator instructions
python -m eval_engine.harness.run plan `
  --spec evals/packs/copilot-factory/spec.yaml `
  --case evals/packs/copilot-factory/cases/smoke-create-issue-triage-pack/case.yaml

# 2) cd <workspace>; open fresh Copilot CLI; paste _runstate.prompt.md;
#    note the session id

# 3) Capture evidence:
#    @eval-runner please dump session <id> for copilot-factory /
#    smoke-create-issue-triage-pack / <run-id> / <ws> to
#    evals/packs/copilot-factory/fixtures/smoke-create-issue-triage-pack/<id>.json

# 4) Build judge manifest
python -m eval_engine.harness.run judge-plan `
  --run-id <id> --spec ... --case ... --fixture ...

# 5) For each request listed: paste into a fresh @eval-judge session,
#    save its JSON response to the printed response_file path.

# 6) Score → JSONL + markdown report
python -m eval_engine.harness.run score `
  --run-id <id> --spec ... --case ... --fixture ... --manifest ...

# 7) (optional) Promote the result to committed history
python -m eval_engine.harness.run promote --pack copilot-factory --run-id <id>

# Trend reports any time
python -m eval_engine.harness.trend --pack copilot-factory
python -m eval_engine.harness.trend --pack copilot-factory --metric subagent_invocations
python -m eval_engine.harness.trend --pack copilot-factory --rubric coherence
```

The harness defaults the per-repo evals root to `<repo>/evals/`
(this directory). Override with `--evals-root <path>` or
`$EVALS_ROOT` if you keep evals elsewhere.

## Authoring a new case

A case lives at `evals/packs/<pack>/cases/<case-id>/`. See
[`docs/authoring-guide.md`](docs/authoring-guide.md) §2.2–§2.6 for the
full element-by-element spec. Quick summary:

- `case.yaml` — declarative case definition.
- `prompt.md` — the user message the operator pastes; supports
  `{{ template_vars }}` rendered against `case.yaml.prompt_template_vars`
  plus harness-provided `workspace_root`, `run_id`, `case_dir`.
- `inputs/` — static files staged into the workspace via `copy_tree`.
- `golden/` — reference materials staged to
  `evals/data/golden-staging/<run_id>/` for the judge. **Never** into
  the SUT workspace.
- `hooks/` — optional `setup.py` / `teardown.py` (only when no
  built-in step kind suffices).

Built-in workspace step kinds (declared under `case.yaml`'s
`workspace.steps`):

| kind | purpose |
|------|---------|
| `git_init` | initialise a git repo in the workspace |
| `copy_tree` | recursively copy from `inputs/` into the workspace |
| `file_template` | render a template (`{{var}}`) from `inputs/` |
| `repo_clone` | fetch a pinned-SHA snapshot of an external repo |
| `shell` | run a portable command via `subprocess` |
| `hook` | call a function from a case-local Python module |

`repo_clone` requires `ref` to be a 40-char SHA — branches are
rejected for reproducibility. Snapshots cache to
`evals/data/repo-cache/<sha>` so repeat runs are fast.

## Authoring a new pack spec

See [`docs/authoring-guide.md`](docs/authoring-guide.md) §2.1 for the full
field reference and step-by-step. Use
[`packs/copilot-factory/spec.yaml`](packs/copilot-factory/spec.yaml) as the
template. It encodes:

- the orchestrator + sub-agents and their negative-scope (allowed
  tools, write/read paths, allowed downstream agents)
- per-agent prompt and output contracts (required/forbidden sections
  and fields)
- ordering constraints across sub-agent calls
- which rubrics to apply (each starts at `severity: info` until it
  stabilizes; promote to `warn` or `blocker` with a `threshold`).

Every failure mode in `.local/multi-agent-instructions.md` §2.7 is
covered by ≥1 assertion or rubric — see the table in
[`../eval_engine/README.md`](../eval_engine/README.md) and the matrix
in `../eval_engine/docs/05-design-revisions-v2.md`.

## Verdict semantics

A case is binary **pass/fail** at the top level, gated by:

1. all `severity: blocker` assertions pass, AND
2. all rubrics with `severity: blocker` meet their `threshold`.

Warns/infos and ungated rubrics shape metrics (and the trend report)
but do not affect status. Every JSONL line carries the full per-assertion
verdicts, rubric scores (0..1), structural metrics
(`subagent_invocations`, `tool_calls_total`, files written/read,
blocker failure count), and reproducibility hashes for the prompt,
spec, rubrics, and agent files used.

## Workspace lifecycle

By default the harness deletes a workspace **only on pass**
(`teardown.policy: delete-on-pass`). Failed runs keep the workspace
so you can inspect what the SUT saw and produced. Other policies a
case may declare: `keep`, `delete`, `move-to-archive`.

```powershell
python -m eval_engine.harness.run resume        # list active workspaces
python -m eval_engine.harness.run cleanup        # dry-run: show what would be deleted
python -m eval_engine.harness.run cleanup --apply
python -m eval_engine.harness.run abandon --workspace evals/packs/<pack>/workspaces/.../<run_id>
```

## Pre-commit hook

Avoid noisy result/fixture commits with:

```powershell
python -m eval_engine.harness.precommit
```

Wire it from `.git/hooks/pre-commit`. Override with
`EVAL_PRECOMMIT_FORCE=1`.
