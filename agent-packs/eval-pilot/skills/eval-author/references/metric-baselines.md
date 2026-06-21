# Metric Baselines and Tolerances

`metric(name, value, ...)` is the pytest fixture wrapper around `record_metric(...)`. It binds `eval_id` to the pytest node id, appends one JSON line, and returns a `MetricResult`.

## Directions

| Direction | Regression means |
|---|---|
| `higher_is_better` | Current value drops below baseline beyond tolerance. |
| `lower_is_better` | Current value rises above baseline beyond tolerance. |
| `neutral` | Never flags regression; records information only. |

## Baseline Strategies

| Strategy | Use when |
|---|---|
| `last` | Deterministic metrics where the previous committed value is the right comparison. This is the default. |
| `rolling_mean` | Noisy or LLM-derived metrics. Uses `window` prior values; default `window=5`. |
| `best` | You want to protect the best previous value for deterministic quality or performance. |
| `pinned` | You pass an explicit `baseline=` value. |

## Tolerances

- `tolerance` is absolute slack.
- `tolerance_pct` is fractional slack based on the baseline, e.g. `0.10` allows 10% movement.
- If both are set, evalpilot uses the larger allowed slack.
- The first recorded value has no prior baseline and cannot regress.

## MetricResult

Useful fields: `value`, `baseline`, `baseline_strategy`, `delta`, `pct_delta`, `regressed`, `history_path`.

Use `m.assert_no_regression(log_path=result.log_path)` to fail a pytest test when the latest value regressed.
