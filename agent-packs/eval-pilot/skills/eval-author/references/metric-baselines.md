# Assertions, Metrics, Baselines, and Tolerances

## Assertion kinds

Declared in the `## Assert` YAML block. All are optional; combine as needed.

| Key | Meaning |
|---|---|
| `files.exists` | glob paths that must exist (list). |
| `files.absent` | glob paths that must **not** exist (list). |
| `glob_count` | `[{ pattern, min?, max?, equals? }]` — match count in range. |
| `contains` | `[{ text, ignore_case?, path? }]` — substring in stdout (or a file). |
| `not_contains` | substring that must be absent. |
| `prose_contains` | substring match with whitespace normalised. |
| `stdout_contains` | substring in stdout specifically. |
| `matches` | `[{ pattern, path?, flags? }]` — regex match. |
| `json_path` | `[{ path, query, equals?, exists? }]` — value at a dotted JSON query. |
| `json_empty` | `[{ path, query }]` — JSON value is missing, null, `[]`, `{}`, or `""`. |
| `section_contains` | `[{ path?, section, text\|any\|all, ignore_case?, max_chars? }]` — match scoped to a `## Heading` body. |
| `section_not_contains` | `[{ path?, section, text\|any, ignore_case?, max_chars? }]` — text must NOT leak into a section body. |
| `tools` | `{ called?, not_called?, count?, args_contain? }` — assert over tool calls from run telemetry. |
| `files_accessed` | `{ read?, not_read?, written?, not_written? }` — glob lists over files accessed by tool. |
| `tokens` | `{ max_total?, max_input?, max_output?, models? }` — token budget + allowed model globs. |
| `judge` | one mapping or a list: `{ criteria, threshold?, artifact?, name? }`. |
| `asserts` | generic escape hatch: `[{ kind, ...args }]` for any registered kind. |

The `tools`, `files_accessed`, and `tokens` families read run telemetry captured
from Copilot's OpenTelemetry file exporter (enabled automatically by the
`copilot` runner). When telemetry is unavailable (`mock` runner,
`EVALPILOT_TELEMETRY=off`, or an exporter-less build) they **skip** — neutral,
never failing and excluded from the pass-rate.

Register new kinds with the `@assertion` decorator in `evalpilot.assertions`;
the Python builder's `.check(name, predicate)` is a per-eval escape hatch.

## Metrics

Declared under `metrics:` as `[{ name, value, ... }]`. `value` is a number or a
`$`-reference (see the staging reference). Each run appends one JSON line to
`<eval-root>/_metrics/<slug>/history.jsonl` and compares against a baseline.

## Directions

| Direction | Regression means |
|---|---|
| `higher_is_better` | Current value drops below baseline beyond tolerance. |
| `lower_is_better` | Current value rises above baseline beyond tolerance. |
| `neutral` | Never flags regression; records information only. |

## Baselines

`baseline:` accepts a strategy name, or a number (pinned).

| Strategy | Use when |
|---|---|
| `last` | Deterministic metrics compared to the previous committed value (default). |
| `rolling_mean` | Noisy or LLM-derived metrics. Uses `window` prior values (default 5). |
| `best` | Protect the best previous value for deterministic quality/performance. |
| a number | Pinned baseline (equivalently `baseline_value:`). |

## Tolerances and gating

- `tolerance` — absolute slack.
- `tolerance_pct` — fractional slack based on the baseline, e.g. `0.10` = 10%.
- If both are set, evalpilot uses the larger allowed slack.
- The first recorded value has no prior baseline and cannot regress.
- `gate: true` makes a metric regression **fail** the eval; otherwise the metric
  is informational and only surfaces in `evalpilot metrics --check`.

## Metric record fields

Each JSONL row includes `value`, `baseline`, `baseline_strategy`, `delta`,
`pct_delta`, `regressed`, `tolerance`, `tolerance_pct`, plus run provenance
(`ts`, `run_id`, `git_sha`, `eval_id`, `name`, `unit`, `direction`).
