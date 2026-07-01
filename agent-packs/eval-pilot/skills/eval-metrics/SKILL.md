---
name: eval-metrics
description: "Use evalpilot numeric metrics over time: JSONL history, baseline strategies, regression gates, evalpilot metrics reports, HTML trend charts, and CI checks. Trigger keywords: eval metrics, metric regression, history.jsonl, baseline, rolling mean, tolerance, trend, evalpilot metrics."
argument-hint: "[metric slug] [--check]"
user-invocable: true
---

# Eval Metrics

Use this skill when the user wants numeric trend tracking, regression gates, or
help interpreting `evalpilot metrics`. Metrics are declared **inside the eval
spec** and recorded automatically each run — no fixture wiring.

## Declaring a metric

In a `*.eval.md` `## Assert` block:

```yaml
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better,
      baseline: rolling_mean, tolerance: 0.1 }
  - { name: response_words, value: $stdout.words, direction: lower_is_better,
      baseline: last, tolerance_pct: 0.25 }
```

Or with the Python builder:

```python
.metric("judge_score", "$judge.score",
        direction="higher_is_better", baseline="rolling_mean", tolerance=0.1)
```

Each run appends one JSON line to committed history:

```text
<eval-root>/_metrics/<slug>/history.jsonl
```

The slug is derived from the eval id plus the metric name.

## Value references

`value:` is a literal number or a `$`-reference resolved at run time:

- `$judge.score` / `$judge.<name>.score` — a judge verdict's score.
- `$duration` — wall-clock seconds for the eval.
- `$stdout.words` / `$stdout.chars` / `$stdout.lines`.
- `$assertions.pass_rate` / `$checks.pass_rate`.

## Directions and baselines

Directions:

- `higher_is_better` — dropping below baseline beyond tolerance is a regression.
- `lower_is_better` — rising above baseline beyond tolerance is a regression.
- `neutral` — records only; never regresses.

Baseline (`baseline:` accepts a strategy name or a number):

- `rolling_mean` — noisy/LLM-derived metrics such as judge scores.
- `last` — deterministic metrics compared to the previous committed run.
- `best` — protect the best prior value.
- a **number** — pinned baseline (equivalently `baseline_value:`).

Tolerances: `tolerance` (absolute) and `tolerance_pct` (fractional, e.g. `0.20`).
If both are supplied, the larger slack wins. Set `gate: true` to make a metric
regression fail the eval; otherwise it is informational.

## History record schema

```json
{
  "ts": "2026-06-21T00:00:00+00:00",
  "run_id": "20260621T000000-abcdef12",
  "git_sha": "abc1234",
  "eval_id": "skills.my-skill.test_smoke",
  "name": "judge_score",
  "value": 0.86,
  "unit": "score",
  "direction": "higher_is_better",
  "baseline": 0.82,
  "baseline_strategy": "rolling_mean",
  "delta": 0.04,
  "pct_delta": 0.0488,
  "regressed": false,
  "tolerance": 0.1,
  "tolerance_pct": 0.0
}
```

Commit these histories with the evals for portable, git-diffable baselines.

## Reporting trends

```bash
evalpilot metrics                 # every series: runs, latest, baseline, min/max
evalpilot metrics judge_score     # filter series by substring
evalpilot metrics judge_score -v  # print tail rows (--tail N to change count)
evalpilot metrics --check         # exit 1 if the latest run regressed
```

The HTML report (`evalpilot run --format html` / `evalpilot show --format html`)
renders inline sparkline trend charts per metric, so trends are visible without
the CLI.

## CI pattern

```bash
evalpilot run -t metric      # run the metric-bearing evals
evalpilot metrics --check    # gate on regressions in the latest run
```

For LLM-derived metrics prefer `rolling_mean` plus absolute slack
(`tolerance: 0.05`–`0.1`). For latency/cost/word-count, prefer `lower_is_better`
with `last` or `best` and a percentage tolerance.
