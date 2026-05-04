# Pack-Summary JSON Schema

The autonomous-eval pipeline produces a single machine-readable summary per
`run-pack` invocation. This document is the contract; the consumer side is
[`@factory-eval-runner`](../../agent-packs/copilot-factory/.github/agents/factory-eval-runner.agent.md)
and the producer side is `eval_engine/harness/pack_runner.py` (`_build_pack_summary`).

## Where it's written

```bash
python -m eval_engine.harness.run run-pack \
  --pack <name> --out path/to/summary.json
```

`run-pack` writes the summary to `--out` (alias: `--results-out`) AND to stdout.
Stdout receives ONLY the JSON object — all progress logs go to stderr — so the
caller can `json.loads(stdout)` directly.

**The summary file is always written**, even on harness errors. Callers should
prefer reading the file over capturing stdout when both are available, because
on a harness error stdout may also contain the JSON but the test runner's
buffering can interleave stderr.

## Top-level shape

```json
{
  "schema_version": "1.0",
  "pack": "copilot-factory",
  "started_at": "2026-05-04T18:32:11Z",
  "completed_at": "2026-05-04T18:47:03Z",
  "exit_code": 0,
  "harness_error": null,
  "summary": { ... },
  "models": { ... },
  "resolved_budgets": { ... },
  "resolved_convergence": { ... },
  "judge_calls_used": 14,
  "wall_clock_seconds": 893,
  "cases": [ ... ]
}
```

| Field | Type | Notes |
|-------|------|-------|
| `schema_version` | string | Currently `"1.0"`. Bump on breaking changes. |
| `pack` | string | The pack name (also the dir under `evals/packs/`). |
| `started_at` / `completed_at` | ISO-8601 UTC | Always populated, even on early errors. |
| `exit_code` | 0 \| 1 \| 2 | Mirrors the process exit code. **0** = all required cases pass per `loop_convergence`; **1** = at least one required case failed; **2** = harness error (spec invalid, copilot-bin missing, budget exceeded, judge process error, etc.). |
| `harness_error` | string \| null | Set when `exit_code == 2` (and may also be set on individual cases — see below). Common values: `"copilot-bin-not-found"`, `"spec-not-found"`, `"spec-invalid: …"`, `"budget-exceeded: …"`, `"subset {…} not found in pack"`, `"no cases found in pack"`. |
| `summary` | object | See below. |
| `models` | object | See below. |
| `resolved_budgets` | object | The merged-down `budgets:` block actually enforced (CLI flags + spec). Each field matches `01-spec-schema.md`. |
| `resolved_convergence` | object | The `loop_convergence:` block actually enforced (or its defaults). |
| `judge_calls_used` | int | Cumulative judge subprocess invocations. |
| `wall_clock_seconds` | int | Total elapsed seconds for the run-pack call. |
| `cases[]` | list[obj] | Per-case results. See below. |

## `summary`

```json
{
  "cases_total": 4,
  "cases_passed": 3,
  "cases_failed": 1,
  "cases_errored": 0
}
```

`cases_passed + cases_failed + cases_errored == cases_total`. A case is
"errored" when its own `harness_error` is set; it is "failed" when the
verdict status was `fail` (per `loop_convergence`); otherwise "passed".

## `models`

```json
{
  "resolved": {
    "copilot-factory": "claude-sonnet-4.6",
    "factory-architect": "claude-sonnet-4.6",
    "judge": "claude-opus-4.7"
  },
  "sut": "claude-sonnet-4.6",
  "judge": "claude-opus-4.7"
}
```

* `resolved` snapshots the full `spec.models` map for reproducibility.
* `sut` is `spec.models[<pack>]` (the system-under-test's pinned model).
* `judge` is `spec.models["judge"]` (the rubric judge's pinned model).

## `cases[]`

Each entry:

```json
{
  "case_id": "two-agent-system",
  "run_id": "1-a3f9c2",
  "status": "fail",
  "harness_error": null,
  "fixture_path": "evals/local-results/copilot-factory/two-agent-system/fixtures/1-a3f9c2.json",
  "verdict_path": "evals/local-results/copilot-factory/two-agent-system/verdicts/1-a3f9c2.json",
  "judge_calls": 4,
  "wall_clock_seconds": 217,
  "failures": [
    {
      "kind": "rubric",
      "id": "agent-coherence",
      "severity": "blocker",
      "agent": "factory-architect",
      "message": "score 0.42 < threshold 0.7",
      "evidence_excerpt": "The architecture omits a coordinator…",
      "fixable_in": [],
      "repro_command": "python -m eval_engine.harness.run run-case --pack copilot-factory --case two-agent-system --fixture …/1-a3f9c2.json"
    }
  ]
}
```

| Field | Type | Notes |
|-------|------|-------|
| `case_id` | string | The `id:` from `case.yaml`. |
| `run_id` | string | `<seq>-<6-hex>`, unique per case per `run-pack` invocation (so re-runs don't collide on disk — fixes F10.4). |
| `status` | `pass` \| `fail` \| `error` | `error` ⇔ `harness_error != null`. Under `loop_convergence.required_status: strict-pass`, a verdict whose case-level status would be `pass` but whose warn rubrics failed is demoted to `fail`. |
| `harness_error` | string \| null | Per-case harness error (e.g. `"copilot-bin-not-found"`, `"budget-exceeded: …"`, `"scripted_user not supported via run-pack — use run-case --fixture"`). |
| `fixture_path` | string | Path to the local fixture this case produced (relative to repo root or absolute). Empty when the case errored before capture. |
| `verdict_path` | string | Path to the persisted CaseVerdict JSON. Empty when the case errored before judging. |
| `judge_calls` | int | Subprocess invocations charged against the budget. |
| `wall_clock_seconds` | int | Per-case elapsed seconds. |
| `failures[]` | list[obj] | Concrete things that went wrong. See below. |

### `failures[]` schema (F2)

| Field | Type | Notes |
|-------|------|-------|
| `kind` | `assertion` \| `rubric` | Source of the failure. |
| `id` | string | Assertion ID (e.g. `L1-set`) or rubric ID. |
| `severity` | `info` \| `warn` \| `blocker` | Inherited from the assertion / rubric. Under `strict-pass`, warn rubric failures still report severity `warn` here — promotion happens at the case-status level. |
| `agent` | string \| null | The agent the failure pertains to (assertions: derived from `apply_to`/`agent`; rubrics: `apply_to: per_agent:<name>` ⇒ `<name>`, else null). |
| `message` | string | Human-readable failure description. |
| `evidence_excerpt` | string | Up to 400 chars from the offending content (rationale for rubrics, message for assertions). |
| `fixable_in[]` | list[string] | Spec-derived path globs from `agents[<agent>].write_scope_allow` — what the engineer is permitted to edit to address the issue. **Empty for rubric failures** (the engineer infers the content target from the rubric's evidence). |
| `repro_command` | string | A shell-pasteable command to re-run just this case from the captured fixture. |

## Stdout discipline

`run-pack` emits **exactly one JSON object** to stdout — the pack summary.
All other text (progress, debug, warnings) goes to stderr. This contract
exists so that `@factory-eval-runner` can pipe stdout straight into
`json.loads` without preprocessing.

## Versioning

`schema_version` is the source of truth. New optional fields may be added
at the same `schema_version`; field removals or semantic changes require
a bump. Consumers should ignore unknown keys.
