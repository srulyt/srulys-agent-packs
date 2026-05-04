# `eval_engine/` — reusable evaluation framework for multi-agent Copilot CLI packs

This directory is **the engine**. It is repo-agnostic: copy
`eval_engine/` plus the `agent-packs/eval-framework/` pack into any repo
that ships multi-agent Copilot CLI packs and you have a working
evaluation framework. The per-repo configuration (which packs to test,
what cases to run, what evidence to keep) lives in a sibling
`evals/` directory — see [`../evals/README.md`](../evals/README.md).

## What's in here

```
eval_engine/
├── README.md      this file — engine docs + installation
├── docs/          design specs (start at 05-design-revisions-v2.md; it
│                  supersedes 01–04 on every conflict)
├── harness/       Python 3.11 harness — pure logic, fully unit-tested
├── rubrics/       generic, reusable judge rubrics (markdown + YAML
│                  front-matter): coherence, completeness,
│                  faithfulness-to-input, format-compliance
└── queries/       reusable session_store_sql templates
```

The custom Copilot CLI agent that participates in evaluations
(`@eval-judge`) ships as a regular agent pack under
[`../agent-packs/eval-framework/`](../agent-packs/eval-framework/).
That directory is also part of "the engine" for installation purposes.
Fixture capture is performed by the `capture-local` subcommand of
`eval_engine/harness/run.py` (which lifts evidence out of the local
Copilot CLI process log); earlier drafts described an `@eval-runner`
agent that was never built.

## Installation in a new repo

1. Copy `eval_engine/` and `agent-packs/eval-framework/` into the
   target repo, preserving paths.
2. Create an `evals/` directory at the repo root (the engine's default
   location for per-repo config; override with `--evals-root` or
   `EVALS_ROOT` if you'd rather put it elsewhere).
3. Append to the repo's `.gitignore`:

   ```gitignore
   evals/packs/<pack>/workspaces/
   evals/data/
   evals/packs/<pack>/reports/
   evals/packs/<pack>/results-local/
   __pycache__/
   *.pyc
   .pytest_cache/
   ```

4. Install the harness's runtime dependency:

   ```powershell
   pip install -r eval_engine/harness/requirements.txt
   ```

5. Verify the engine works in isolation:

   ```powershell
   python -m unittest discover -s eval_engine -t .
   # 18 tests, all should pass
   ```

6. Author at least one pack spec under `evals/packs/<pack>/spec.yaml` and one case
   under `evals/packs/<pack>/cases/<case>/` (see
   [`../evals/README.md`](../evals/README.md) for the authoring guide).

## CLI entry points

| Module | Purpose |
|---|---|
| `python -m eval_engine.harness.run plan` | stage workspace + emit operator instructions |
| `python -m eval_engine.harness.run judge-plan` | build judge manifest from a captured fixture (manual judge loop) |
| `python -m eval_engine.harness.run run-judge` | invoke the judge agent non-interactively over a manifest (no human paste) |
| `python -m eval_engine.harness.run run-case` | end-to-end single-case run: stage → drive SUT → capture → judge → score |
| `python -m eval_engine.harness.run run-pack` | aggregate every case in a pack; emit pack-summary JSON; exit 0/1/2 |
| `python -m eval_engine.harness.run score` | apply assertions + judge responses → JSONL + report |
| `python -m eval_engine.harness.run replay` | re-score an existing fixture without re-staging |
| `python -m eval_engine.harness.run promote` | move a local result line into committed results |
| `python -m eval_engine.harness.run resume` | list active workspaces |
| `python -m eval_engine.harness.run cleanup` | delete completed workspaces |
| `python -m eval_engine.harness.run abandon` | mark a stuck workspace abandoned |
| `python -m eval_engine.harness.trend` | trend reports across runs |
| `python -m eval_engine.harness.precommit` | git pre-commit guard |

Both `python -m eval_engine <subcommand>` and
`python -m eval_engine.harness.run <subcommand>` work — the former is a thin
delegation shim. The pack-summary JSON contract is documented in
[`docs/06-pack-summary-schema.md`](docs/06-pack-summary-schema.md).

Every subcommand of `run` accepts `--evals-root <path>` to override
the per-repo evals dir. The engine resolves it via:
flag → `$EVALS_ROOT` → `<repo>/evals`.

## Engine internals (read in this order if extending)

1. `harness/run.py` — CLI; the operator workflow lives here.
2. `harness/models.py` — every dataclass (specs, cases, fixtures,
   verdicts). Schema changes start here.
3. `harness/workspace.py` — per-run isolated workspaces, `_eval/`
   canary, `_runstate.json` manifest, six built-in step kinds
   (`copy_tree git_init file_template repo_clone shell hook`).
4. `harness/assertions/{l1,l2,l3}.py` — 17 assertions across the three
   layers from §2 of the multi-agent blueprint plus
   `L3-workspace-escape`. Add new ones with `@register("L?-name", …)`.
5. `harness/judge/orchestration.py` — manifest builder, mandatory
   anti-injection preamble, double-invoke for blocker rubrics
   (variance ≤ 0.1 or status=`error`).
6. `harness/report.py` — verdict aggregation. Pass = zero blocker
   assertion fails AND zero blocker rubric fails AND zero errors.
7. `harness/store.py` + `harness/trend.py` — JSONL persistence (local
   vs promoted) + trend reporting.
8. `harness/paths.py` + `harness/tools.py` — path normalization +
   tool taxonomy (runtime tool name → canonical category, including
   MCP wildcards).

## Authoring conventions

- All paths in fixtures and assertions are POSIX-normalized strings
  rooted at the workspace, never absolute.
- Generic rubrics belong here (`eval_engine/rubrics/`); per-pack
  rubrics belong in the per-repo `evals/rubrics/` (planned, not yet
  wired — open an issue if needed).
- Each rubric file is markdown with YAML front-matter: `id`,
  `severity` (info|warn|blocker), `threshold`, `applies_to` glob,
  `prompt_template`. Templates may interpolate `{{apply_to}}`,
  `{{artifact_paths}}`, `{{golden_paths}}`.
- Every assertion has a unit test in `harness/tests/test_assertions.py`
  using helpers from `tests/fixtures.py`.

## Updating the engine in a deployed repo

Engine releases are not yet versioned. To pick up a new version,
re-copy `eval_engine/` and `agent-packs/eval-framework/`. The
`harness/store.py` JSONL format is forward-compatible: unknown fields
on disk are preserved and ignored on read.
