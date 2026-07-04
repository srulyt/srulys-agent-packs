# Metric history (committed)

Each subdirectory here is one **metric series** and holds a `history.jsonl`
file — one JSON line per recorded run. These files are **committed on
purpose**: they are how evalpilot tracks numeric results over time and
detects regressions.

Declare a metric **inside the eval spec** — it is recorded automatically each
run, with no fixture wiring. In a `*.eval.md` `## Assert` block:

```yaml
metrics:
  - { name: summary_words, value: $stdout.words, direction: lower_is_better,
      tolerance_pct: 0.25 }
```

Or with the TypeScript builder:

```ts
.metric("summary_words", "$stdout.words", {
  direction: "lower_is_better",
  tolerance_pct: 0.25,
})
```

Inspect trends:

```bash
evalpilot metrics                 # all series, latest vs baseline
evalpilot metrics my-skill -v     # one series, recent rows
evalpilot metrics --check         # exit non-zero if the latest run regressed (CI)
```

Each `history.jsonl` record looks like:

```json
{"ts": "...", "run_id": "...", "git_sha": "abc1234", "eval_id": "...",
 "name": "summary_words", "value": 142, "unit": "", "direction": "lower_is_better",
 "baseline": 130, "baseline_strategy": "last", "delta": 12, "pct_delta": 0.09,
 "regressed": false, "tolerance": 0.0, "tolerance_pct": 0.25}
```
