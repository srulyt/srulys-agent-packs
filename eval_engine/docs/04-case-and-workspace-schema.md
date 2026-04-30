# `case.yaml` Schema & Workspace Lifecycle

> **Read `05-design-revisions-v2.md` first.** v2 changes: golden refs are
> staged OUTSIDE the SUT workspace at `evals/data/golden-staging/<run_id>/`
> (the `_eval/` directory becomes a canary only); `prompt.md` is rendered as
> a template with `prompt_template_vars`; `expected.invocations`,
> `expected.allowed_agent_types`, `expected.artifacts[]`, and
> `expected.rubric_targets` are added; workspaces gain a `_runstate.json`
> manifest plus `run.py resume/cleanup/abandon` commands; failed runs keep
> the workspace by default. Where docs disagree, v2 wins.

A **case** is a single test scenario for a pack: a user prompt + the static
resources the run depends on + the rubrics/files the framework should expect
to see. Each case lives in its own directory under `evals/packs/<pack>/cases/<case>/`.

The harness uses `case.yaml` to drive workspace allocation, resource staging,
golden-reference placement, hook invocation, and teardown.

## Per-case directory layout

```
evals/packs/<pack>/cases/<case>/
├── case.yaml      # this file's schema lives below
├── prompt.md      # exact user message to paste into Copilot CLI
├── inputs/        # static files staged into the workspace (committed)
├── golden/        # reference outputs, staged to <workspace>/_eval/golden/
└── hooks/         # OPTIONAL Python escape-hatch modules
    ├── setup.py     # exposes a callable invoked by `kind: hook` steps
    └── teardown.py  # exposes a callable invoked by teardown.hooks
```

`prompt.md` is mandatory; `inputs/`, `golden/`, and `hooks/` are optional but
omitted directories must not be referenced from `case.yaml`.

## Top-level structure

```yaml
schema_version: 1
id: smoke-create-issue-triage-pack
description: |
  Ask copilot-factory to design and build a small 2-agent pack for issue
  triage with a single orchestrator + one classifier sub-agent.

prompt_file: prompt.md          # relative to this case directory

workspace:
  isolation: copy-tree          # copy-tree | empty | repo-clone
  inputs_dir: inputs/           # OPTIONAL; required when isolation == copy-tree
  golden_dir: golden/           # OPTIONAL; staged to <workspace>/_eval/golden/

  steps:                        # ordered; run after isolation, before operator
    - kind: git_init

    - kind: copy_tree
      src: inputs/
      dest: .

    - kind: file_template
      src: inputs/user-request.md
      dest: .copilot-factory/user-request.md
      vars:
        feature: "issue triage"

    - kind: repo_clone
      url: https://github.com/example/sample-app.git
      ref: abc123def4567890abc123def4567890abc123de   # MUST be a 40-char SHA
      sparse: ["src/", "README.md"]                    # OPTIONAL
      dest: target-repo/

    - kind: shell
      run: |
        python -c "print('preflight ok')"
      timeout_seconds: 30

    - kind: hook
      module: hooks/setup.py
      function: prepare
      args: { extra: "values" }

teardown:
  policy: delete                # delete | keep | move-to-archive
  hooks:
    - kind: hook
      module: hooks/teardown.py
      function: cleanup

expected:
  files_created_under:          # regex list; matched against fixture.session_files
    - "^agent-packs/[a-z0-9-]+/\\.github/agents/.+\\.agent\\.md$"
    - "^\\.copilot-factory/sessions/\\d{4}-\\d{2}-\\d{2}-[a-f0-9]{8}/.+$"
  rubrics:                       # subset of pack-spec rubrics; if omitted, all spec rubrics apply
    - coherence
    - completeness
    - format-compliance
  golden:                        # OPTIONAL: which rubric uses which golden reference
    - { rubric: completeness, ref: golden/architecture.md }
    - { rubric: coherence,    ref: golden/agents-list.md }
```

## Field reference

### Top-level

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `schema_version` | int | yes | Currently `1`. |
| `id` | string | yes | Must match the case directory name. |
| `description` | string | yes | Free text. |
| `prompt_file` | string | yes | Relative path to a markdown file with the exact user prompt. |
| `workspace` | object | yes | Workspace creation + setup. |
| `teardown` | object | no | Defaults to `{ policy: delete, hooks: [] }`. |
| `expected` | object | yes | What the harness asserts about the run beyond pack-spec defaults. |

### `workspace`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `isolation` | enum | yes | `copy-tree` (start from `inputs/`), `empty` (no files), `repo-clone` (start from a `repo_clone` step's output as root). |
| `inputs_dir` | string | conditional | Required when `isolation: copy-tree`. Relative path under the case directory. |
| `golden_dir` | string | no | If set, contents are staged to `<workspace>/_eval/golden/`. The harness creates `<workspace>/_eval/` and ensures pack specs do not allow `_eval/` access. |
| `steps` | list | yes | Ordered list of step objects (see below). |

### `workspace.steps[]` — built-in step kinds

All steps run with the workspace as cwd unless noted.

| `kind` | Required fields | Notes |
|--------|----------------|-------|
| `git_init` | (none) | Equivalent to `git init && git add -A && git commit -m "eval-baseline"`. |
| `copy_tree` | `src`, `dest` | `src` relative to case dir; `dest` relative to workspace. Recursively copies. |
| `file_template` | `src`, `dest`, `vars` | Reads `src` (case-relative), substitutes `{{ var }}` placeholders from `vars`, writes to `dest` (workspace-relative). Strict mode: missing var = error. |
| `repo_clone` | `url`, `ref`, `dest` | `ref` MUST be a 40-character SHA. `sparse` (list) is OPTIONAL. Cached by SHA under `evals/data/repo-cache/<sha>/` (gitignored). Fails if `ref` looks like a branch/tag. |
| `shell` | `run` | Cross-platform via `subprocess.run`. Default `timeout_seconds: 60`. Non-zero exit fails the case (status `error`, not `fail`). Env: `PYTHONIOENCODING=utf-8`. |
| `hook` | `module`, `function`, `args?` | Imports `<case>/<module>` via `importlib`, calls `function(workspace_path, **args)`. Hooks must be idempotent. Failures fail the case (`error`). |

### `teardown`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `policy` | enum | yes | `delete` (default), `keep`, `move-to-archive` (moves to `evals/data/archive/`). `--keep-workspace` CLI flag overrides to `keep`. |
| `hooks` | list | no | Same shape as `workspace.steps` `hook` entries; run before deletion/archival. |

### `expected`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `files_created_under` | list[regex] | yes | Used by L3-files together with the pack-spec `agents[*].file_scope_allow`. The case-level list is "files we *expect* to see"; the pack-level allow list is "files agents *may* touch". A run passes when every touched file matches at least one allow regex AND every `files_created_under` regex has at least one match (catches "agents skipped doing the work"). |
| `rubrics` | list[string] | no | Subset of pack-spec rubric ids. If omitted, all rubrics declared in the pack spec apply. |
| `golden` | list of `{rubric, ref}` | conditional | Required when any selected rubric has `inputs_required` containing `golden_ref`. `ref` is case-relative under `golden/`. |

## The reserved `_eval/` directory

The harness creates `<workspace>/_eval/` and stages golden references there.
Pack specs are validated to ensure no agent's `file_scope_allow` matches
anything under `_eval/`. The framework auto-prepends `^_eval/.*$` to every
agent's `file_scope_deny`. Result: any agent that reads or writes inside
`_eval/` triggers a blocker scope violation, which is exactly what we want
because the system under test must never see eval scaffolding.

The path is short and unambiguous; the leading underscore makes it stand out
in directory listings.

## Hook authoring contract

A hook module is a regular Python module under
`evals/packs/<pack>/cases/<case>/hooks/`. The function the harness calls receives:

```python
def prepare(workspace_path: pathlib.Path, **kwargs) -> None: ...
```

- The harness adds `evals/packs/<pack>/cases/<case>/` to `sys.path` while loading.
- Hooks must NOT exit, NOT call `os.chdir`, NOT spawn detached processes.
- Hooks should be idempotent — they may run multiple times during developer
  iteration with `--keep-workspace`.
- Standard hook helpers will be exposed in `eval_engine/harness/hooks_api.py` (e.g.,
  `read_case_file`, `make_workspace_path`).

## Validation rules (enforced at load time)

1. `id` matches the case directory name.
2. `prompt_file` exists and is non-empty.
3. `workspace.isolation` ∈ {copy-tree, empty, repo-clone}.
4. When `isolation: copy-tree`, `inputs_dir` exists.
5. When `isolation: repo-clone`, exactly one `workspace.steps[*]` is a
   `repo_clone` step and it runs first.
6. Every `workspace.steps[*].kind` is one of the built-ins; unknown kinds
   are an error (no silent skip).
7. Every `repo_clone.ref` is exactly 40 hex characters.
8. Every `file_template` has all placeholder variables in `vars`.
9. Every `expected.files_created_under` regex compiles.
10. Every rubric in `expected.rubrics` is a rubric id declared in the pack
    spec.
11. Every `expected.golden[*].rubric` is in `expected.rubrics` (or all spec
    rubrics if `expected.rubrics` is omitted) AND that rubric's
    `inputs_required` includes `golden_ref`.
12. Hook modules referenced by any step or teardown hook exist and import
    cleanly.

## Why this shape

- **Declarative-first, escape hatch second**: 90%+ of cases will be
  expressible as a list of built-in steps. Hooks exist for the long tail
  (e.g., generating large random datasets, calling an external service)
  without bloating the schema.
- **Reproducibility is in the schema**: `repo_clone` requires SHAs, not
  branches; templates are explicit; shell steps have explicit timeouts.
- **Negative scope by construction**: `_eval/` is reserved at the framework
  level so spec authors can't accidentally allow it.
- **Per-run isolation**: every run gets a fresh workspace; concurrent runs
  cannot interfere; failed runs leave their workspace behind for debugging
  via `--keep-workspace` even when `teardown.policy: delete`.
