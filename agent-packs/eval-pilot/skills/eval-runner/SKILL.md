---
name: eval-runner
description: "Run evalpilot evals and triage failures for Copilot agents and skills. Teaches evalpilot run targets, pytest selectors, report-log summaries, log inspection, exit codes, and SUT environment knobs. Trigger keywords: run evals, evalpilot run, failing eval, rerun nodeid, triage eval, agent log."
argument-hint: "[target] [-k expr] [-m markers]"
user-invocable: true
---

# Eval Runner

Use this skill after evals exist, or whenever the user asks to run or debug evalpilot tests.

## Commands

```bash
evalpilot run
evalpilot run evals/packs/my-agent
evalpilot run evals/skills/my-skill/test_smoke.py
evalpilot run evals/skills/my-skill/test_smoke.py::test_happy_path
evalpilot run evals -k happy_path
evalpilot run evals -m "not slow"
evalpilot run evals --parallel 4
```

`evalpilot run [target]` wraps pytest and always writes a report log to `evals/_runs/latest-report.jsonl`. It passes these flags through accurately:

- `target` optional path or pytest nodeid; default is the eval root.
- `-k EXPR` pytest keyword expression.
- `-m MARKERS` / `--markers MARKERS` pytest marker expression.
- `--parallel N` xdist workers when `N > 1`.
- trailing extra args are passed to pytest.

Exit code is pytest's exit code: `0` for pass, `1` for test failure.

## Reading the Summary

After pytest exits, evalpilot parses `evals/_runs/latest-report.jsonl` and prints:

```text
Results: <passed> passed, <failed> failed, <skipped> skipped
Report: <repo>/evals/_runs/latest-report.jsonl
```

If a test fails, copy its full pytest nodeid and rerun only that nodeid:

```bash
evalpilot run evals/packs/my-agent/test_plan.py::test_agent_migration_plan -vv
```

## Triage Loop

1. Read the pytest failure first; rubric failures list the failed check names.
2. Open the SUT log from the assertion message (`result.log_path`). Logs are written under the test workspace's configured `_logs/` directory and contain:
   - command line
   - `[cwd]`
   - `[exit]`
   - `[duration_s]`
   - `--- PROMPT (stdin) ---`
   - `--- STDOUT ---`
   - `--- STDERR ---`
3. Decide whether the failure is:
   - SUT unavailable or skipped (`EVALPILOT_SKIP_SUT`, missing `copilot`, timeout)
   - prompt/eval issue (expected answer leaked, criteria too vague, brittle structural assert)
   - real agent/skill regression
4. If judge output is involved, inspect the judge error and its log path. Judge criteria should be strict and artifact-grounded.
5. Re-run the smallest nodeid until the diagnosis is clear, then rerun the target directory.

## Environment Knobs

- `COPILOT_BIN` points the runner at a specific `copilot` binary.
- `EVALPILOT_SUT_TIMEOUT` clamps all SUT subprocess timeouts.
- `EVALPILOT_SKIP_SUT=1` prevents launching the SUT; behavioural tests should skip via `result.usable` / `result.unavailable_reason()`.
- `EVALPILOT_RUNNER` selects a registered SUT runner; default is `copilot`.

## Done Criteria

- Relevant target passes with `evalpilot run <target>`.
- Any metric-gated tests either pass or have a deliberate baseline/tolerance update.
- Failure summaries include the SUT log path for future triage.
