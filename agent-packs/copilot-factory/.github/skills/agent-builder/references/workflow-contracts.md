# Factory Workflow Contracts

This file is the canonical machine-readable handoff contract for the
Copilot Factory. Producers, orchestrators, consumers, templates, and tests
MUST use the same version and field names. Unknown additive fields may be
ignored; changing or removing a required field requires a new major version.

The normative JSON Schema for eval results is
[`factory-eval-result-v1.schema.json`](factory-eval-result-v1.schema.json).

## Eval result contract `factory.eval-result/v1`

The eval runner owns exactly one `edit` write:
`.copilot-factory/sessions/{session-id}/artifacts/eval-run-{n}.json`.
Its guarded wrapper runs Eval Pilot with `EVALPILOT_EVAL_ROOT` and
`EVALPILOT_METRICS_ROOT` under an OS-temporary directory, fingerprints the
whole repository working tree (excluding `.git`) before and after the child,
and fails with the changed-path list if anything was created, changed, or
deleted. Only after a clean comparison does it promote exactly one fresh
`evals/_runs/<run-id>/` subtree. Prompt-only write verification is forbidden.

> **Unresolved confinement blocker:** the current wrapper detects repository
> mutations but does not restore them. These command-resolution instructions
> do not fix or waive that blocker. Do not claim that guarded execution fully
> confines writes until the wrapper is separately repaired and reviewed.

### Canonical guarded-wrapper invocation

This section is the single source of truth for Factory eval command
construction. Never use `<agent-builder>` or another executable/path
placeholder, and never execute an `.mjs` file directly.

Before execution, the runner MUST:

1. Locate the repository root deterministically by walking from the current
   directory to the nearest ancestor containing `.git`, resolve it to an
   absolute path, and set the shell working directory to that root.
2. Resolve `node` with the shell's application lookup and retain its existing
   absolute executable path.
3. Resolve the first existing wrapper candidate, in this order:
   `.github/skills/agent-builder/scripts/run-evals-guarded.mjs` (installed
   pack) then
   `agent-packs/copilot-factory/.github/skills/agent-builder/scripts/run-evals-guarded.mjs`
   (source checkout). Retain the existing absolute path.
4. Require the sibling `validate-factory-paths.mjs`, the selected
   `evals/packs/{pack}/` directory, and the repository Eval Pilot entry point
   `agent-packs/eval-pilot/engine-ts/dist/cli.js` to exist. Validate `target`
   by hosting the validator through the same resolved Node executable.
5. Reject the run before shell execution if the root, Node, wrapper,
   validator, Eval Pilot entry point, tests, or target preflight fails, or if
   any command/path/argument still contains an unresolved template
   placeholder such as `<...>` or `{...}`.

Use these stable failed-preflight identifiers in telemetry:
`repository-root`, `node-executable`, `guarded-wrapper`, `path-validator`,
`eval-pilot-entrypoint`, `tests`, `target`, and `unresolved-placeholder`.

The wrapper accepts key/value pairs only. Required arguments are `--pack
<kebab-case-pack>` and canonical `--target <all|validated
evals/packs/{pack}/...>`. Optional arguments are `--runner <copilot|mock>`
(default `copilot`), `--tags <tag-expression>`, and `--sut-timeout
`--wall-clock-timeout <positive-integer-seconds>` (default `1800`) bounds the
whole eval process. `--sut-timeout <positive-integer-seconds>` is optional and
must be omitted unless the orchestrator explicitly intends to override every
spec's own timeout. No other argument or selector, including `tests_subset`,
is supported. `--parallel <1-8>` is optional and defaults to `1`.

On PowerShell, invoke the fully resolved paths explicitly:

```powershell
& $nodePath $absoluteWrapperPath `
  --pack $pack `
  --target $target `
  --runner $runner `
  --wall-clock-timeout $seconds `
  --parallel $parallel
```

Here every variable MUST already contain its final validated value; the
literal command is not a template to pass through. Set the cwd to the resolved
repository root first. Do not use `node <agent-builder>/...`, a relative
wrapper path, `evalpilot`, `npx evalpilot`, or direct `.mjs` execution.

Every `harness-error`, including preflight failure, MUST be persisted in the
versioned result and returned in `eval-verdict` as additive
`harness_diagnostics`: exact expanded command/argv with secrets redacted,
cwd, resolved Node executable, wrapper, validator and Eval Pilot entry-point
paths, exit code (or `null` before launch), bounded stdout/stderr excerpts,
and the exact failed preflight name (or `null`). Redaction must preserve
argument names and command shape. If no process launched, record the command
that would have run after expansion and the unresolved or missing value.

```json
{
  "schema_version": "factory.eval-result/v1",
  "session_id": "2026-01-01-deadbeef",
  "pack": "example-pack",
  "eval_run_index": 1,
  "selector": {"target": "all"},
  "report_path": "evals/_runs/<run-id>/report.json",
  "resolved_model": null,
  "exit_code": 1,
  "totals": {
    "collected": 2, "passed": 1, "failed": 1,
    "errored": 0, "skipped": 0
  },
  "wall_clock_seconds": 10,
  "failures": [{
    "failure_id": "case-id/check-name",
    "case_id": "case-id",
    "kind": "assertion",
    "message_excerpt": "expected section was absent",
    "log_path": "evals/_runs/<run-id>/cases/case-id.log",
    "test_path": "evals/packs/example-pack/case.eval.md",
    "fixable_in": ["agent-packs/example-pack/.github/agents/main.agent.md"]
  }]
}
```

Required failure fields are `failure_id`, `case_id`, `kind`,
`message_excerpt`, `log_path`, `test_path`, and `fixable_in`.
`log_path` and `test_path` may be `null`. `fixable_in` is always an array.

### Safe `fixable_in` derivation

The runner copies `fixable_in` only from explicit eval-spec/report metadata.
Both runner and engineer MUST use
`scripts/validate-factory-paths.mjs fixable <pack> <path>...`; this script is
the canonical runtime validator. Every accepted entry is:

- a forward-slash repository-relative path under the exact
  `agent-packs/{pack}/.github/` root;
- free of absolute, drive-qualified, UNC, URI, backslash, wildcard, repeated
  separator, empty, `.` or `..` segments;
- resolved inside that same target pack; cross-pack paths fail.

The runner MUST NOT infer writable paths from failure prose, logs, model
output, or `test_path`. Missing/invalid metadata produces `fixable_in: []`,
which the engineer treats as unfixable.

### Canonical rerun selector

The only selector field is `target`:

```yaml
target: all | evals/packs/{pack}/<relative-file-or-directory>
```

It may select only `all` or an existing normalized path under the exact
`evals/packs/{pack}/` root. Validation occurs before normalization: reject
absolute, drive-qualified, UNC, URI, backslash, wildcard, repeated-separator,
empty-segment, and `.`/`..` segment paths. Then resolve the path and require
that it remains a descendant of the selected pack root and that normalization
did not change the input. Paths for another pack are invalid. `tests_subset`
is retired and MUST NOT be emitted or accepted.

## Improvement analysis contract `factory.improvement-analysis/v1`

The critic writes `artifacts/improvement-analysis.md` and emits these fences
in order:

1. `verdict`
2. `recommendation`
3. `findings-json`
4. `improvement-plan`
5. `ready-for-orchestrator`

```yaml
# verdict
schema_version: factory.improvement-analysis/v1
review_type: improvement-analysis
status: PASS | BLOCKING
iteration_count: 0
```

```yaml
# recommendation
strategy: incremental | rebuild | stop
rationale: <one paragraph>
findings_total: 0
blocking: 0
major: 0
minor: 0
```

```json
[
  {
    "id": "F1",
    "severity": "blocking",
    "category": "contract",
    "file": "agent-packs/example/file.md",
    "section": "Output Contract",
    "action": "rewrite",
    "fix": "Concrete implementation-ready change",
    "validation": "Specific acceptance check"
  }
]
```

`severity` is `blocking`, `major`, or `minor`; `action` is `add`,
`remove`, `rewrite`, `consolidate`, or `retain`. Zero findings is `[]`.
`improvement-plan` groups finding IDs in implementation order and states
dependencies. `ready-for-orchestrator` is exactly `true` or `false`.

For architecture and implementation reviews, the existing
`blocking-issues-json` and `concerns-json` fences remain unchanged.
