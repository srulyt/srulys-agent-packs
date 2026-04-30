# Rubric Schema & Run-Record (JSONL) Schema

> **Read `05-design-revisions-v2.md` first.** v2 adds: mandatory judge
> preamble + double-invoke for blocker rubrics; `status: error` allowed in
> JSONL; new fields `run_kind`, `repeat_group_id/index`, `prompt_hash`,
> `spec_hash`, `rubric_hashes`, `agent_file_hashes`, `cli_version`, `os`,
> `judge_model`, `temperature_recorded`, `supersedes_run_id`; local-vs-promoted
> run split (default writes go to gitignored `evals/packs/<pack>/results-local/`,
> `--record` promotes to committed `evals/packs/<pack>/results/`). Where docs disagree, v2
> wins.

Two schemas live here because they are tightly coupled: a rubric defines what
the judge measures, and the run-record stores the score the judge produced.

## Part 1 — Rubric file schema

A **rubric** is a markdown file under `eval_engine/rubrics/<rubric-id>.md` that the
`@eval-judge` agent loads as part of its task prompt. Pack specs reference a
rubric by `id` (filename stem). Rubrics are reusable across packs.

### File layout

The file is a markdown document with a YAML frontmatter block:

```markdown
---
id: completeness
schema_version: 1
description: |
  Measures whether the pack's final artifacts cover all the items the user's
  request implied, with no significant omissions.
output_schema:
  score: { type: number, minimum: 0.0, maximum: 1.0 }
  rationale: { type: string, max_length: 800 }
  evidence:
    type: array
    items:
      kind: { enum: [file, section, quote] }
      ref:  { type: string }      # path, heading, or short quote
      note: { type: string }
scoring_guide:
  - { score: 0.0,  label: "missing", description: "Major requested items absent." }
  - { score: 0.25, label: "partial", description: "Some requested items present, several major ones missing." }
  - { score: 0.5,  label: "mixed",   description: "Most requested items present; one or two material omissions." }
  - { score: 0.75, label: "good",    description: "All requested items present; minor omissions or shallow coverage." }
  - { score: 1.0,  label: "complete","description": "Every requested item covered with appropriate depth." }
inputs_required:
  - case_prompt           # the prompt the user sent
  - golden_ref?           # OPTIONAL golden reference path
  - sut_artifacts         # paths or content the system under test produced
  - apply_to_target       # "pack_output" or "per_agent:<name>"
---

# Completeness — judge instructions

You are evaluating the **completeness** of the system-under-test's output...

[Full judging instructions follow as markdown below the frontmatter.]
```

### Frontmatter fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | string | yes | Must equal the filename stem. |
| `schema_version` | int | yes | Currently `1`. |
| `description` | string | yes | One-paragraph human description. |
| `output_schema` | object | yes | JSON-Schema-like sketch of the judge's output. |
| `scoring_guide` | list | yes | Anchored 0..1 levels. At least 3 anchors; values must be ascending; first is 0.0; last is 1.0. |
| `inputs_required` | list[string] | yes | What the harness must provide in the judge's task prompt. Allowed: `case_prompt`, `golden_ref`, `sut_artifacts`, `apply_to_target`. Unknown values rejected. A trailing `?` marks an input as optional. |

### Body

Free-form markdown that the harness includes verbatim in the `@eval-judge`
task prompt. Should contain:

- A clear single-sentence definition of the dimension being scored.
- The full scoring rubric with examples.
- An explicit reminder that the judge MUST emit the `output_schema` block as
  fenced JSON and nothing else after the fenced block.

### Validation rules

1. Filename stem matches `id`.
2. `scoring_guide` has ≥3 entries, ascending, first 0.0, last 1.0.
3. `inputs_required` contains only the allowed values.
4. The body markdown contains the literal string ```` ```json ```` somewhere
   (sanity check that the rubric instructs the judge to emit fenced JSON).

### Why markdown body + YAML frontmatter

- The judge needs prose instructions; the harness needs structured metadata.
- Frontmatter keeps the parser trivial (PyYAML) and the human-edit path
  natural (you write the rubric like you'd write a doc).

---

## Part 2 — Run-record JSONL schema

Each `python eval_engine/harness/run.py` invocation that completes a case appends
**exactly one line** to `evals/packs/<pack>/results/runs.jsonl`. This is the
persistent trend store, committed to git.

### File location

`evals/packs/<pack>/results/runs.jsonl` — one file per pack, append-only. Lines are
newline-delimited JSON. The harness uses an atomic append (`open(path, 'a')`
+ `os.fsync` + a flock) to make concurrent runs safe.

### Per-line record

```json
{
  "schema_version": 1,
  "run_id": "2026-04-28T18-22-01Z-ab12cd34",
  "pack": "copilot-factory",
  "case_id": "smoke-create-issue-triage-pack",
  "session_id": "2026-04-28-ab12cd34",
  "timestamp": "2026-04-28T18:22:01Z",
  "git_sha": "3f1c9e0a8b2d4e6f1c3a5b7e9d0f2c4a6b8e1d3f",
  "git_dirty": false,
  "harness_version": "0.1.0",
  "models": {
    "orchestrator": "claude-sonnet-4.6",
    "factory-architect": "claude-sonnet-4.6",
    "factory-critic": "claude-sonnet-4.6",
    "factory-engineer": "claude-sonnet-4.6",
    "judge": "claude-opus-4.7"
  },
  "status": "fail",
  "blocker_failures": 1,
  "warn_failures": 0,
  "counts": {
    "assertions_total": 24,
    "assertions_pass": 22,
    "assertions_fail": 2,
    "assertions_skip": 0,
    "assertions_error": 0
  },
  "metrics": {
    "subagent_invocations": 7,
    "total_input_tokens": 41023,
    "total_output_tokens": 9821,
    "total_cost_usd": 0.42,
    "files_touched": 3,
    "scope_violations": 0,
    "unexpected_agents": []
  },
  "rubric_scores": {
    "coherence":    { "score": 0.82, "severity": "info",    "threshold": null, "passed": true,  "rationale": "...", "evidence": [...] },
    "completeness": { "score": 0.71, "severity": "info",    "threshold": null, "passed": true,  "rationale": "...", "evidence": [...] },
    "format-compliance": { "score": 0.85, "severity": "blocker", "threshold": 0.9, "passed": false, "rationale": "...", "evidence": [...] }
  },
  "assertions": [
    {
      "assertion_id": "L3-files",
      "agent": "factory-engineer",
      "status": "fail",
      "severity": "blocker",
      "message": "Touched _eval/golden/architecture.md",
      "evidence": [{ "kind": "session_file", "path": "_eval/golden/architecture.md" }]
    },
    "..."
  ],
  "links": {
    "fixture": "evals/packs/copilot-factory/fixtures/smoke-create-issue-triage-pack/2026-04-28-ab12cd34.json",
    "report":  "evals/packs/<pack>/reports/2026-04-28T18-22-01Z-ab12cd34.md",
    "workspace": null
  }
}
```

### Field reference

| Field | Type | Notes |
|-------|------|-------|
| `schema_version` | int | Bump on breaking changes. Trend-reader handles old + new. |
| `run_id` | string | UTC timestamp + short hex of session_id. Unique per run. |
| `pack`, `case_id`, `session_id` | string | Identity. |
| `timestamp` | RFC3339 UTC | When the run finished. |
| `git_sha`, `git_dirty` | string, bool | For grouping trends by commit. |
| `harness_version` | string | Bump alongside the harness package. |
| `models` | object | Every agent → model used. Used to slice trends. |
| `status` | enum | `pass` \| `fail` (only — `error` runs are not appended; they go to `evals/packs/<pack>/reports/` only). |
| `blocker_failures` | int | Pre-computed for fast trend queries. |
| `warn_failures` | int | Same. |
| `counts` | object | Per-status assertion totals. |
| `metrics` | object | All numeric metrics tracked over time. |
| `rubric_scores` | object | One entry per rubric the spec declared. `passed` is computed (`severity != blocker` or `score >= threshold`). |
| `assertions` | list | Full per-assertion verdicts. Truncated to `evidence[*].ref` pointers (no full payloads) to keep lines parseable. |
| `links` | object | Relative paths to the fixture, the human report, and the workspace if kept. |

### Why JSONL committed to git

- **Diff-friendly**: a new run is a single appended line; reviewers see exactly
  what changed.
- **Mergeable**: appending parallel branches is conflict-free as long as both
  fsync before the merge.
- **Queryable**: the harness reads with a streaming JSON parser; for ad-hoc
  exploration `store.py rebuild` produces a SQLite index in `evals/data/`
  (gitignored, derived).
- **Source-of-truth in source-of-truth**: trend baselines live with the code
  they evaluate; rolling back the framework rolls back its observed history
  in lockstep.

### Concurrency model

- One writer per pack at a time, enforced by an OS file lock on
  `evals/packs/<pack>/results/runs.jsonl`.
- Multiple writers across different packs are safe (different files).
- Readers are lock-free; partial last lines are detected and ignored
  (defense-in-depth).

### Schema evolution

- New fields are additive; readers must tolerate unknown fields.
- Removing a field is a breaking change → bump `schema_version`.
- The reader keeps a registry of (version → migrator) so old records remain
  readable after migrations.
