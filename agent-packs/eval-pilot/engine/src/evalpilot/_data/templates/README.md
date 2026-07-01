# evals/

This directory holds your evalpilot evals. Each eval is a single self-contained
file that reads top-to-bottom, so you can understand what it does at a glance.

## Layout

```
evals/
  examples/            # copy one of these to start; delete when you have real evals
    hello-agent.eval.md
    hello-skill.eval.py
  _metrics/            # committed JSONL metric history (trend tracking)
  _runs/               # generated reports (gitignored)
```

## Everyday commands

```bash
evalpilot new my-eval --target my-agent --kind agent   # scaffold a spec
evalpilot lint                                          # validate specs, no SUT
evalpilot run                                           # run everything
evalpilot run examples/hello-agent.eval.md              # run one file
evalpilot run -t smoke                                  # run by tag
evalpilot show --format html --open                     # re-open last report
evalpilot metrics --check                               # fail on regressions
```

Set `EVALPILOT_RUNNER=mock` to exercise the whole pipeline offline (no Copilot
CLI required) — handy for trying things out.

Every `run` writes `report.json` (and `report.html`) under `_runs/<run-id>/`,
and `_runs/latest.txt` always points at the most recent one.
