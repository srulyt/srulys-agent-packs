---
name: eval-runner
description: "Run evalpilot evals and triage failures for Copilot agents and skills. Teaches evalpilot run/show/lint, tag filters, the modeled JSON result, terminal/HTML renders, SUT logs, exit codes, and environment knobs. Trigger keywords: run evals, evalpilot run, failing eval, eval report, triage eval, agent log."
argument-hint: "[target] [-t tags]"
user-invocable: true
---

# Eval Runner

Use this skill after evals exist, or whenever the user asks to run or debug
evalpilot evals. The runner is standalone (no pytest): it discovers `*.eval.md`
and `*.eval.py` specs, executes them, and writes a **modeled result** that every
view renders from.

## Commands

```bash
evalpilot lint                       # validate specs, no SUT launched
evalpilot run                        # run everything under the eval root
evalpilot run evals/packs/my-agent   # run a directory
evalpilot run evals/skills/my-skill/test_smoke.eval.md   # run one file
evalpilot run -t smoke               # only specs tagged 'smoke'
evalpilot run -t "smoke,-slow"       # include smoke, exclude slow
evalpilot run --parallel 4           # run specs concurrently
evalpilot run --runner mock          # offline deterministic runner
evalpilot run --format all --open    # write JSON + HTML and open the report
evalpilot show                       # re-render the latest run
evalpilot show <run-id> --format html --open
```

Flags for `run`:

- `target` — spec file or directory (default: eval root).
- `-t/--tags EXPR` — comma list; a leading `-` or `~` excludes a tag.
- `--parallel N` — concurrent workers.
- `--format terminal,html,json,all` — which renders to emit (default `all`).
- `--runner NAME` — override the SUT runner (e.g. `mock`).
- `--open` — open the HTML report in a browser.
- `--no-gate` — always exit 0 (don't fail on eval failures).

Exit code: `0` if every eval passed (or was skipped), `1` otherwise.

## Where results go

Every run writes a canonical result so the location is never a mystery:

```text
<eval-root>/_runs/<run-id>/report.json    # modeled result (source of truth)
<eval-root>/_runs/<run-id>/report.html    # self-contained shareable report
<eval-root>/_runs/latest.txt              # pointer to the newest report.json
```

The terminal summary prints those paths. `evalpilot show` re-renders from
`report.json` without re-running anything.

## Reading the summary

```text
[PASS] my-agent-migration-plan  (3/3 checks)  12.4s
[FAIL] other-eval  (2/3 checks)  8.1s
       - mentions tests: expected substring 'test'
================================================================
Results: 1 passed, 1 failed, 0 skipped  (20.5s)
JSON:   .../_runs/<run-id>/report.json
HTML:   .../_runs/<run-id>/report.html
```

Statuses: `PASS`, `FAIL` (a check/judge failed), `SKIP` (SUT unavailable), and
`ERR` (the eval could not run, e.g. an unknown target to stage).

## Triage loop

1. Read the failed check names in the terminal (or open the HTML for drill-down).
2. Open the SUT log referenced in the eval's result (`log_path`), under
   `_runs/<run-id>/<slug>/`. Logs contain the command line, `[cwd]`, `[exit]`,
   `[duration_s]`, and the PROMPT / STDOUT / STDERR sections.
3. Classify the failure:
   - **SUT unavailable / skipped** — missing `copilot`, `EVALPILOT_SKIP_SUT`,
     timeout (status `SKIP`).
   - **Spec issue** — expected answer leaked, vague criteria, brittle assert.
   - **Real regression** — the agent/skill genuinely got worse.
4. For judge failures, read the judge rationale in `report.json` / HTML. Judge
   criteria should be strict and artifact-grounded.
5. Re-run the single file (`evalpilot run <file>`) until the diagnosis is clear,
   then re-run the directory.

Tip: `EVALPILOT_RUNNER=mock evalpilot run <file>` exercises the whole pipeline
offline — useful to confirm the spec parses, asserts, judges, and renders
before spending tokens.

## Environment knobs

- `COPILOT_BIN` — path to a specific `copilot` binary.
- `EVALPILOT_SUT_TIMEOUT` — clamp all SUT subprocess timeouts.
- `EVALPILOT_SKIP_SUT=1` — never launch the SUT; behavioural evals skip.
- `EVALPILOT_RUNNER` — select a registered runner (`copilot` default, `mock`).

## Done criteria

- Target passes with `evalpilot run <target>` (exit 0).
- Metric-gated evals pass or have a deliberate baseline/tolerance change.
- The JSON/HTML report path is shared for future triage.
