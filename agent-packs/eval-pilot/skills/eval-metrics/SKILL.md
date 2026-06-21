---
name: eval-metrics
description: "Use evalpilot numeric metrics over time: JSONL history, baseline strategies, regression gates, evalpilot metrics reports, and CI checks. Trigger keywords: eval metrics, metric regression, history.jsonl, baseline, rolling mean, tolerance, trend, evalpilot metrics."
argument-hint: "[metric slug] [--check]"
user-invocable: true
---

# Eval Metrics

Use this skill when the user wants numeric trend tracking, regression gates, or help interpreting `evalpilot metrics`.

## Recording Metrics in Tests

Use the `metric` pytest fixture:

```python
m = metric(
    "judge_score", verdict.score,
    direction="higher_is_better",
    baseline_strategy="rolling_mean",
    tolerance=0.1,
)
m.assert_no_regression(log_path=result.log_path)
```

`metric(name, value, ...)` records one JSON line to:

```text
evals/_metrics/<slug>/history.jsonl
```

The slug is derived from the pytest node id plus metric name. The returned `MetricResult` includes `value`, `baseline`, `delta`, `pct_delta`, `regressed`, and `history_path`.

Call `MetricResult.assert_no_regression(log_path=result.log_path)` when the metric should gate the test. Omit it when the number is informational only.

## Directions and Baselines

Directions:

- `higher_is_better` — lower than baseline beyond tolerance is a regression.
- `lower_is_better` — higher than baseline beyond tolerance is a regression.
- `neutral` — records only; never regresses.

Baseline strategies:

- `rolling_mean` for noisy or LLM-derived metrics such as judge scores.
- `last` for deterministic metrics where the previous committed run is the right comparison.
- `best` for deterministic quality/performance where you want to protect the best prior value.
- `pinned` when passing an explicit `baseline=` value.

Tolerances:

- `tolerance` absolute slack.
- `tolerance_pct` fractional slack, e.g. `0.20` for 20%.
- If both are supplied, evalpilot uses the larger slack.

## Metric History Record Schema

Each JSONL row contains:

```json
{
  "ts": "2026-06-21T00:00:00+00:00",
  "run_id": "20260621T000000-abcdef12",
  "git_sha": "abc1234",
  "eval_id": "skills.my-skill.test_smoke.test_happy_path",
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

Commit these histories with the evals when you want portable, git-diffable trend baselines.

## Reporting Trends

```bash
evalpilot metrics
evalpilot metrics judge_score
evalpilot metrics judge_score -v
evalpilot metrics --check
```

`evalpilot metrics [slug]` filters series by substring. It prints runs, latest value, baseline, min, max, and regression count. `-v` / `--verbose` prints the tail rows; `--tail N` changes how many verbose rows are shown. `--check` exits `1` if the latest row in any selected series has `regressed: true`; otherwise it exits `0`.

## CI Pattern

Run the eval target, then gate metric regressions:

```bash
evalpilot run evals -m metric
evalpilot metrics --check
```

Use sane tolerances before committing history. For LLM-derived metrics, prefer `rolling_mean` plus absolute slack (`tolerance=0.05` or `0.1`). For latency/cost/word-count style metrics, prefer `lower_is_better` with `last` or `best` and a percentage tolerance.
