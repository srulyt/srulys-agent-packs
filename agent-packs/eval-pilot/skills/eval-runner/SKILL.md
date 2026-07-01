---
name: eval-runner
description: "Run evalpilot evals and triage failures for Copilot agents and skills. Teaches evalpilot run/show/lint, repo wrappers, tag filters, the modeled JSON result, terminal/HTML renders, SUT logs, exit codes, and environment knobs. Trigger keywords: run evals, evalpilot run, failing eval, eval report, triage eval, agent log."
argument-hint: "[target] [-t tags]"
user-invocable: true
---

# Eval Runner

Use this skill after evals exist, or whenever the user asks to run or debug
evalpilot evals. The TypeScript engine discovers `*.eval.md` and `*.eval.ts`
specs, executes them, and writes a **modeled result** that every view renders
from.

## Commands

```bash
evalpilot lint                       # validate specs, no SUT launched
evalpilot run                        # run everything under the eval root
evalpilot run evals/packs/my-agent   # run a directory path
evalpilot run evals/skills/my-skill/test_smoke.eval.md   # run one file path
evalpilot run -t smoke               # only specs tagged 'smoke'
evalpilot run -t "smoke,-slow"       # include smoke, exclude slow
evalpilot run --parallel 4           # run specs concurrently
evalpilot run --runner mock          # offline deterministic runner
evalpilot run --format all --open    # write JSON + HTML and open the report
evalpilot show                       # re-render the latest run
evalpilot show <run-id> --format html --open
```

Repo-root conveniences resolve a pack/skill name to its eval directory and
forward to the engine:

```bash
node scripts/run-evals.mjs my-agent
node scripts/run-evals.mjs --all
node scripts/run-evals.mjs my-agent --list
node scripts/run-evals.mjs my-agent --mock
node scripts/run-evals.mjs my-agent -- -t "smoke,-slow"
npm run eval
npm run eval:all
npm run eval:mock
```

On Windows, `eval.cmd <pack>` offers the same workflow.

Flags for `run`:

- `target` — spec file or directory path (default: eval root).
- `-t/--tags EXPR` — comma list; a leading `-` or `~` excludes a tag.
- `--parallel N` — concurrent workers.
- `--format terminal,html,json,all` — which renders to emit.
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
`report.json` without re-running anything. `_runs/` is generated output and is
not committed.

## Triage loop

1. Read the failed check names in the terminal (or open the HTML for drill-down).
2. Open the SUT log referenced in the eval's result (`log_path`), under
   `_runs/<run-id>/<slug>/`.
3. Classify the failure as SUT unavailable, spec issue, or real regression.
4. For judge failures, read the judge rationale in `report.json` / HTML.
5. Re-run the single file (`evalpilot run <file>`) until the diagnosis is clear,
   then re-run the directory.

Tip: `EVALPILOT_RUNNER=mock evalpilot run <file>` or
`evalpilot run <file> --runner mock` exercises the pipeline offline.

## Environment knobs

- `COPILOT_BIN` — path to a specific `copilot` binary.
- `EVALPILOT_SUT_TIMEOUT` — clamp all SUT subprocess timeouts.
- `EVALPILOT_SKIP_SUT=1` — never launch the SUT; behavioural evals skip.
- `EVALPILOT_RUNNER` — select a registered runner (`copilot` default, `mock`).

## Done criteria

- Target passes with `evalpilot run <target>` or the corresponding repo wrapper.
- Metric-gated evals pass or have a deliberate baseline/tolerance change.
- The JSON/HTML report path is shared for future triage.
