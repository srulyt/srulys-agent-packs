# Eval Authoring Guide

Hands-on reference for everything that lives under `evals/`. Read this once
before adding a new pack or a new case. For the underlying JSON schemas, see
the engine docs in [`../../eval_engine/docs/`](../../eval_engine/docs/) — this
guide is the operator-facing complement: *what each file is for, how to build
it, what mistakes to avoid.*

> **Conventions.** This guide assumes the pack-centric layout
> (`evals/packs/<pack>/...`) and the v2 design (`05-design-revisions-v2.md`).
> Where it disagrees with older engine docs, this guide wins.

---

## 1. Directory map

```
evals/
├── README.md                operator quick-start
├── docs/                    this guide + future how-tos
├── packs/<pack>/            EVERYTHING about one pack lives here
│   ├── spec.yaml            pack contract (one per pack)
│   ├── cases/<case-id>/     one directory per test scenario
│   │   ├── case.yaml
│   │   ├── prompt.md
│   │   ├── inputs/          staged into workspace (committed)
│   │   ├── golden/          reference outputs for the judge (committed)
│   │   └── hooks/           optional Python escape-hatches
│   ├── fixtures/<case-id>/  captured session JSON (committed)
│   ├── results/runs.jsonl   promoted run history (committed; source of truth)
│   ├── results-local/       local-only run history (gitignored)
│   ├── reports/             markdown verdicts (gitignored)
│   └── workspaces/          isolated per-run SUT workspaces (gitignored)
└── data/                    cross-pack scratch (all gitignored)
    ├── judge-manifests/     prompts to paste into @eval-judge
    ├── judge-responses/     judge JSON replies
    ├── golden-staging/      where golden/ is copied for the judge
    └── repo-cache/          pinned-SHA snapshots for repo_clone
```

Three rules of thumb:

1. **Anything pack-specific belongs under `packs/<pack>/`.** No exceptions.
2. **`data/` is for cross-pack scratch only.** Never commit anything here.
3. **`fixtures/` and `results/` are committed history.** Treat them like
   tests: a change here is meaningful evidence about the pack's behaviour.

---

## 2. Element-by-element spec

Each subsection covers: **what** the element is, **why** it exists, **how**
to author it, and **common mistakes**.

### 2.1 `packs/<pack>/spec.yaml`

**What.** The declarative contract for one pack. One YAML per pack. Drives
every assertion the harness makes when scoring a run of that pack. The
pack-spec captures the *promises* each agent's `.agent.md` makes — file-access
boundaries, tool allow-lists, prompt/output sections, ordering, etc. — in a
machine-checkable form.

**Why.** Without it the harness has no idea what "correct" looks like. With
it, every run can be scored against the same explicit standard.

**Skeleton.**

```yaml
schema_version: 1
pack: <pack-name>            # MUST equal directory name
orchestrator: <pack-name>    # the agent users address (usually same as pack)

models:                      # pinned models per agent (drift detection)
  <pack-name>: claude-sonnet-4.6
  <sub-agent-1>: claude-sonnet-4.6
  judge: claude-opus-4.7     # judge MUST be ≥ the strongest SUT agent

loops:
  max_orchestrator_turns: 60

flow:
  ordering:                  # DAG edges: [A, B] means A must precede B
    - [<sub-agent-1>, <sub-agent-2>]
  no_unexpected_agents: true # fail if any out-of-set agent shows up

agents:
  - name: <sub-agent-1>
    invocations: { min: 1, max: 3, must_complete: true }
    allowed_tools: [read, search, write, execute, agent, mcp]
    write_scope_allow:
      - "^path/regex/.*"
    read_scope_allow:
      - "^path/regex/.*"
    scope_deny:
      - "^_eval/"            # canary trap — ALWAYS deny this
      - "^\\.git/"
    prompt_contract:
      required_sections: ["Context"]
      required_fields: ["session-id"]
      forbidden_input: []
      forbidden_downstream: []
    output_contract:
      must_contain_sections: ["Result"]
    token_budget_max: 80000
    no_subagent_reinvocation: true

rubrics:
  - id: coherence
    apply_to: artifact:<artifact-id>   # or per_agent:<name>
    severity: info                     # info | warn | blocker
    # threshold: 0.7                   # required if severity != info
```

**Field reference.**

| Field | Type | Drives | Notes |
|---|---|---|---|
| `pack`, `orchestrator` | string | identification | Filename and directory must match |
| `models.*` | string | model-drift detection | Must include the orchestrator and every sub-agent. `judge` is required and must be a model **at least as strong** as any SUT agent |
| `loops.max_orchestrator_turns` | int | runaway-loop check | Reasonable default: 60 |
| `flow.ordering` | list of `[before, after]` | `L1-order` assertion | Express the DAG, not the full timeline. Multiple edges allowed |
| `flow.no_unexpected_agents` | bool | `L1-set` assertion | Almost always `true` |
| `agents[].invocations` | `{min, max, must_complete}` | `L1-count` | `must_complete` requires every call to terminate cleanly |
| `agents[].allowed_tools` | list of canonical categories | `L3-tools` | Canonical names from [`00-tool-taxonomy.md`](../../eval_engine/docs/00-tool-taxonomy.md): `read`, `search`, `write`, `execute`, `agent`, `mcp`, plus `mcp:<server>` for a specific MCP server |
| `write_scope_allow` / `read_scope_allow` | regex list | `L3-writes` / `L3-reads` | Anchor with `^`. Use double-escaped backslashes. Mirror the `.agent.md` File Access Boundaries section verbatim |
| `scope_deny` | regex list | global override | **Always include `^_eval/` and `^\\.git/`** |
| `prompt_contract.required_sections` | list | `L2-prompt-sections` | Markdown headings the orchestrator must include in the message it sends to this agent |
| `prompt_contract.required_fields` | list | `L2-prompt-required-fields` | Lower-cased identifiers (e.g. `session-id`) the orchestrator must populate in the prompt |
| `prompt_contract.forbidden_input` | list | warns | Substrings/patterns that shouldn't appear (PII, secrets) |
| `prompt_contract.forbidden_downstream` | list of agent names | `L3-no-fanout` plus | Sub-agents this one must NOT delegate to |
| `output_contract.must_contain_sections` | list | `L2-output-sections` | Sections the agent's response must contain |
| `token_budget_max` | int | `L3-budget` (warn) | Soft ceiling per single invocation |
| `no_subagent_reinvocation` | bool | `L3-no-fanout` | If true, this agent cannot call other agents (most sub-agents) |
| `rubrics[].id` | string | judge dispatch | Must exist in `eval_engine/rubrics/` |
| `rubrics[].apply_to` | `artifact:<id>` or `per_agent:<name>` | judge target | Combined with the case's `expected.rubric_targets` to pick the file/output to score |
| `rubrics[].severity` | `info` \| `warn` \| `blocker` | verdict gating | Start at `info`. Promote to `blocker` only after the metric stabilises across ≥3 runs |
| `rubrics[].threshold` | 0..1 | gating cutoff | Required when severity is `warn` or `blocker` |

**How to build a new spec.**

1. Copy `evals/packs/copilot-factory/spec.yaml` as a starting template.
2. Open every `agent-packs/<pack>/.github/agents/*.agent.md` and translate
   the `tools:` front-matter into `allowed_tools` and the **File Access
   Boundaries** section into the `write_scope_allow` / `read_scope_allow` /
   `scope_deny` regexes. Use anchored regexes — un-anchored patterns are a
   common source of false-positive scope violations.
3. Read the body of each agent prompt to extract the section headings it
   requires from the orchestrator (→ `prompt_contract.required_sections`)
   and the headings its own response uses (→ `output_contract`).
4. Diagram the agent flow on paper. Encode each *must-precede* edge as a
   pair under `flow.ordering`.
5. Pick rubrics from `eval_engine/rubrics/`. Always start at
   `severity: info`. Promote individually after baseline runs exist.
6. Validate: `python -m eval_engine.harness.run plan --spec <new>.yaml --case ...`

**Common mistakes.**

- Un-anchored scope regexes (`agent-packs/.*` rather than `^agent-packs/.*`)
  — let the SUT write outside its sandbox without tripping any assertion.
- Forgetting `^_eval/` in `scope_deny` — the workspace canary stops working.
- Listing tools as their runtime names (`view`, `task`) instead of canonical
  categories — see `00-tool-taxonomy.md`.
- Setting any rubric to `blocker` before there's a baseline — every run fails
  on day one.

---

### 2.2 `packs/<pack>/cases/<case-id>/case.yaml`

**What.** A self-contained scenario — one user prompt + everything the
harness needs to stage, score, and tear down a run.

**Why.** The spec describes *what's allowed*; cases describe *what to ask*.
A pack with one case is barely tested; a pack with five cases that cover
happy-path + boundary + adversarial inputs has real coverage.

**Skeleton.**

```yaml
id: <case-id>                # MUST equal directory name; kebab-case
pack: <pack-name>
description: |
  One paragraph: what the case asks the pack to do, and what it
  proves if it passes.

prompt_file: prompt.md       # relative to the case directory

prompt_template_vars:        # substituted into prompt.md as {{var}}
  feature: "issue triage"

workspace:
  isolation: copy-tree       # copy-tree | repo-clone | empty
  inputs_dir: inputs/
  golden_dir: golden/
  steps:
    - kind: git_init
    - kind: copy_tree
      src: inputs/
      dest: .
    # Other kinds: file_template, repo_clone, shell, hook

teardown:
  policy: delete-on-pass     # delete-on-pass | keep | delete | move-to-archive
  # hooks: [hooks.teardown:cleanup_db]   # optional

expected:
  artifacts:
    - id: <artifact-id>
      path_pattern: "^path/regex/.*\\.md$"
      required: true
  invocations:
    <agent-name>: { min: 1, max: 2 }
  rubric_targets:
    "artifact:<artifact-id>": "^path/regex/.*\\.md$"
  # allowed_agent_types: [<sub-agent-1>, <sub-agent-2>]
```

**Field reference.**

| Field | Drives | Notes |
|---|---|---|
| `id`, `pack` | identification | `id` MUST equal the directory name. `pack` MUST equal the parent pack's directory name |
| `description` | reports / docs | Used in the markdown verdict; write it for a future maintainer |
| `prompt_file` | operator step 2 | Always `prompt.md` unless you have a strong reason otherwise |
| `prompt_template_vars` | template substitution | Available in `prompt.md` as `{{var}}`. The harness automatically also injects `workspace_root`, `run_id`, `case_dir` |
| `workspace.isolation` | workspace allocation | `copy-tree` (default), `repo-clone`, or `empty` |
| `workspace.steps` | pre-run staging | Run in declared order. See [§3 below](#3-built-in-workspace-step-kinds) for kinds |
| `teardown.policy` | post-run cleanup | Default `delete-on-pass` keeps the workspace for failed runs so you can inspect what the SUT saw |
| `expected.artifacts[]` | artifact-presence assertions | Files the SUT MUST produce; `required: true` makes their absence a blocker |
| `expected.invocations.<agent>` | tighter-than-spec `L1-count` | Optional per-case override of the spec's `agents[].invocations` |
| `expected.allowed_agent_types` | per-case `L1-set` override | Restrict the agent set further than the spec allows |
| `expected.rubric_targets` | judge dispatch | Maps each `artifact:<id>` referenced by spec rubrics to the actual file regex for this case |

**How to build a new case.**

1. `mkdir evals/packs/<pack>/cases/<case-id>/{inputs,golden}` (note both
   subdirs must exist even if empty — keep a `README.md` placeholder so
   git tracks them).
2. Write `prompt.md` first — it's the user message you'd actually paste.
3. Decide what the SUT must produce. Each output goes in
   `expected.artifacts[]` with an anchored regex. Loose regexes here mean
   the harness can be fooled by a file in the wrong place.
4. Stage anything the SUT needs to read into `inputs/`. Stage anything the
   judge will compare against into `golden/`. **Never put golden material
   in `inputs/`** — that leaks the answer.
5. Pick teardown policy. `delete-on-pass` is the right default.
6. `python -m eval_engine.harness.run plan --spec ... --case <new>` and walk
   through the printed instructions before running for real.

**Common mistakes.**

- Writing the prompt last and back-fitting `expected.*` to the SUT's
  whatever-it-produced output. Define the expectations *first*; if the SUT
  doesn't meet them, that's a failure.
- Confusing `inputs/` (visible to the SUT) with `golden/` (judge-only).
- Forgetting to mirror per-case bounds into `expected.invocations` — the
  spec's wide bounds (1–5) are usually too loose for a specific scenario.

---

### 2.3 `packs/<pack>/cases/<case-id>/prompt.md`

**What.** The exact user message an operator pastes into a fresh Copilot
CLI session to start the SUT run.

**Why.** Reproducibility. The harness hashes this file and stores the hash
in every result row, so any change to the prompt is detectable in trend
reports.

**How to author.**

- Write it as a real user would write it — full sentences, no test-y prose.
- Use `{{var}}` for any value you might want to vary across cases or
  parameter sweeps. Variables come from `case.yaml.prompt_template_vars`
  plus three harness-provided injectables: `workspace_root`, `run_id`,
  `case_dir`.
- Keep it self-contained: do not reference files in `inputs/` by absolute
  path; the SUT's CWD is always the workspace root.
- If a rubric checks that a phrase appears verbatim in an artifact, embed
  that phrase in the prompt and reference it in the golden file (see
  faithfulness-to-input below).

---

### 2.4 `packs/<pack>/cases/<case-id>/inputs/`

**What.** Static files the harness copies into the workspace as the SUT's
starting state. Think of it as the SUT's repo before it runs.

**Why.** Some cases need a pre-existing repo skeleton, sample data, or a
config file to act on. Others (like a green-field "build me X" prompt) need
nothing.

**How to author.**

- Stage exactly what the SUT must see. Never include the answer.
- If you have nothing to stage, keep a `README.md` placeholder so git
  tracks the empty directory.
- Files here are committed and hashed; treat changes as test-input changes.

---

### 2.5 `packs/<pack>/cases/<case-id>/golden/`

**What.** Reference material the judge consults when scoring. Staged to
`evals/data/golden-staging/<run-id>/`, **outside** the SUT workspace —
the SUT cannot read it.

**Why.** Rubrics like `completeness` and `faithfulness-to-input` need
something to compare against. Putting it in `golden/` keeps the comparison
hidden from the SUT (so it can't game the judge by parroting).

**How to author.**

- Each golden file should describe a *standard*, not a verbatim expected
  output. The judge is looking for "does the SUT's artifact contain these
  elements?", not "does it byte-match this string?".
- Use a numbered list of required elements. The judge prompt instructs the
  judge to score against each item.
- Reference `prompt_template_vars` literally if any rubric tests
  faithfulness — e.g. if the prompt says `{{feature}} = "issue triage"`,
  the golden file should say *the literal phrase "issue triage" must appear
  in the artifact*.

**Common mistake.** Putting golden material in `inputs/` — the SUT then
reads it and trivially passes the rubric. The harness flags this with a
warning, but author discipline matters more.

---

### 2.6 `packs/<pack>/cases/<case-id>/hooks/` *(optional)*

**What.** Python escape-hatch modules called from `case.yaml.workspace.steps`
(`kind: hook`) or `teardown.hooks`.

**Why.** When the built-in step kinds don't suffice — e.g. you need to
launch a fixture database or wait for an external service.

**How to author.**

- One file per phase: `setup.py`, `teardown.py`.
- Each file exposes a callable named in the case YAML
  (`hooks/setup.py:prepare_db`).
- Call signature: `def prepare_db(workspace: Path, case_dir: Path,
  run_id: str) -> None`. Raise on failure.
- Hooks run in the harness's process, not the SUT's. They cannot reach
  into the running Copilot CLI session.

Hooks are a power-tool. Prefer the built-in step kinds whenever possible.

---

### 2.7 `packs/<pack>/fixtures/<case-id>/<session-id>.json`

**What.** Captured evidence from one Copilot CLI session: the orchestrator
turn list, every sub-agent invocation, every tool call, and every artifact
hash. Produced by the `@eval-runner` agent and committed.

**Why.** The score-pipeline is fixture-driven. The harness reads this JSON,
not a live session. Committing it gives us replayable, auditable runs and
enables `python -m eval_engine.harness.run replay` for offline scoring.

**How to author.** You don't author fixtures by hand — let `@eval-runner`
emit them. Schema lives in
[`../../eval_engine/docs/02-fixture-schema.md`](../../eval_engine/docs/02-fixture-schema.md).
Manual edits are reserved for redaction.

---

### 2.8 `packs/<pack>/results/runs.jsonl`

**What.** The committed history of promoted runs for this pack. One JSON
object per line. Each line carries: run id, pack, case, timestamp, verdict,
per-assertion verdicts, rubric scores, structural metrics, and hashes of
prompt/spec/rubrics/agent files used.

**Why.** Source of truth for trend reports. A diff on this file is
meaningful evidence about how the pack's behaviour is changing.

**How to manage.**

- The harness appends here only via `python -m eval_engine.harness.run
  promote --pack <pack> --run-id <id>`.
- Promotion requires a clean working tree by default; pass `--allow-dirty`
  to override (rare).
- Local-only experiments land in `results-local/` (gitignored).
- Never edit by hand.

---

### 2.9 `packs/<pack>/results-local/`, `reports/`, `workspaces/`

All gitignored.

- **`results-local/runs.jsonl`** — same schema as `results/runs.jsonl`,
  written by `score` before promotion. Lets you experiment without
  polluting committed history.
- **`reports/<run-id>.md`** — human-readable verdict markdown. Generated
  alongside each scored run.
- **`workspaces/<case-id>/<run-id>/`** — the isolated SUT workspace for
  one run. Contains the SUT's CWD plus a top-level `_eval/` directory
  (canary). Survives failed runs by default.

You generally don't open these unless debugging.

---

### 2.10 `data/` (cross-pack scratch, all gitignored)

- **`judge-manifests/<run-id>/<rubric>-A.md`, `-B.md`** — the prompts the
  operator pastes into `@eval-judge`. Two per blocker rubric (double-invoke
  for variance check); one per non-blocker rubric.
- **`judge-responses/<run-id>/<rubric>-A.json`, `-B.json`** — the JSON the
  judge agent emits. Operator saves them to the path printed by
  `judge-plan`.
- **`golden-staging/<run-id>/`** — the case's `golden/` directory copied
  here so the judge can read it without the SUT seeing it.
- **`repo-cache/<sha>/`** — pinned-SHA snapshots fetched by `repo_clone`
  steps. Lets repeat runs reuse the same source tree.

---

## 3. Built-in workspace step kinds

Used in `case.yaml.workspace.steps`. Run in declared order.

| `kind` | Required fields | Purpose |
|---|---|---|
| `git_init` | — | `git init` in the workspace |
| `copy_tree` | `src`, `dest` | Recursively copy from `src` (relative to case dir) into `dest` (relative to workspace) |
| `file_template` | `src`, `dest`, `vars` | Render a `{{var}}` template from `src` into `dest` |
| `repo_clone` | `repo`, `ref`, `dest` | Clone an external repo at a pinned SHA into `dest`. **`ref` MUST be a 40-char SHA.** Branches are rejected for reproducibility. Cached under `evals/data/repo-cache/<sha>` |
| `shell` | `cmd` | Run a portable command via `subprocess`. Avoid when possible |
| `hook` | `module`, `callable` | Call a function from `hooks/<module>.py` |

---

## 4. Operator workflow (end-to-end)

```powershell
# 1) Stage workspace + emit operator instructions
python -m eval_engine.harness.run plan `
  --spec evals/packs/<pack>/spec.yaml `
  --case evals/packs/<pack>/cases/<case-id>/case.yaml

# 2) cd into the printed workspace path. Open a fresh Copilot CLI session.
#    Paste the contents of _runstate.prompt.md. Note the Copilot session id
#    that gets created.

# 3) Capture evidence with @eval-runner:
#    "@eval-runner please dump session <id> for <pack> / <case-id> /
#     <run-id> / <ws> to evals/packs/<pack>/fixtures/<case-id>/<id>.json"

# 4) Build the judge manifest:
python -m eval_engine.harness.run judge-plan `
  --run-id <id> --spec ... --case ... --fixture ...

# 5) For each manifest entry: paste the manifest .md into a fresh
#    @eval-judge session, save the response JSON to the path it prints.

# 6) Score:
python -m eval_engine.harness.run score `
  --run-id <id> --spec ... --case ... --fixture ... --manifest ...

# 7) (optional) Promote into committed history:
python -m eval_engine.harness.run promote --pack <pack> --run-id <id>

# Trend reports any time:
python -m eval_engine.harness.trend --pack <pack>
python -m eval_engine.harness.trend --pack <pack> --metric subagent_invocations
python -m eval_engine.harness.trend --pack <pack> --rubric coherence
```

The harness defaults the per-repo evals root to `<repo>/evals/`. Override
with `--evals-root <path>` or `$EVALS_ROOT` if you keep evals elsewhere.

Workspace lifecycle helpers:

```powershell
python -m eval_engine.harness.run resume          # list active workspaces
python -m eval_engine.harness.run cleanup         # dry-run
python -m eval_engine.harness.run cleanup --apply
python -m eval_engine.harness.run abandon --workspace evals/packs/<pack>/workspaces/.../<run-id>
```

Pre-commit guard against noisy fixture/result commits:

```powershell
python -m eval_engine.harness.precommit
```

---

## 5. Verdict semantics (recap)

A run is binary **pass/fail** at the top level, gated by:

1. all `severity: blocker` assertions pass, AND
2. all rubrics with `severity: blocker` meet their `threshold`, AND
3. zero harness errors.

`warn` and `info` outcomes shape metrics and the trend report but do not
affect status. Every JSONL line carries the full per-assertion verdicts,
rubric scores (0..1), structural metrics (`subagent_invocations`,
`tool_calls_total`, files written/read, blocker failure count), and
reproducibility hashes for the prompt, spec, rubrics, and agent files used.

---

## 6. Where to learn more

- [`../README.md`](../README.md) — operator quick-start.
- [`../../eval_engine/README.md`](../../eval_engine/README.md) — engine
  installation and `.local/multi-agent-instructions.md` §2.7 coverage table.
- [`../../eval_engine/docs/`](../../eval_engine/docs/) — full JSON schemas:
  - `00-tool-taxonomy.md` — canonical tool categories.
  - `01-spec-schema.md` — pack-spec JSON Schema.
  - `02-fixture-schema.md` — fixture JSON Schema.
  - `03-rubric-and-results-schema.md` — rubric and result-row schemas.
  - `04-case-and-workspace-schema.md` — case and workspace lifecycle.
  - `05-design-revisions-v2.md` — the v2 design (authoritative on conflicts).
- Per-pack READMEs at `packs/<pack>/README.md` — explain what each
  pack's evals cover and what each case proves.
