# Eval migration notes

This document records legacy eval cases that were **NOT** ported one-for-one
when the YAML+`eval_engine` harness was retired in favour of pytest-based
evals under `evals/packs/`.

A case was skipped (or significantly reframed) when its assertion machinery
depended on a harness capability that the new framework deliberately does
not provide. Where useful, the spirit of the case has been folded into a
sibling pytest test or covered by the static `lint_pack` checks instead.

## Capabilities the new framework intentionally drops

The pytest-based runner exists so that a maintainer can read a single test
file end-to-end and understand what it validates. To preserve that property
we did **not** rebuild the following parts of the legacy harness:

- **Forced fault injection.** Legacy cases like `negative-iteration-cap-breach`
  monkey-patched the composer to fail; the runner has no equivalent and it
  would obscure the test's intent.
- **Per-tool invocation counters / read-trace inspection.** Cases such as
  `negative-orchestrator-direct-source-read`, `negative-orchestrator-paraphrase`
  (the trace half), and the `invocations:` `min/max` blocks in nearly every
  case relied on the harness instrumenting every tool call. The new runner
  treats `copilot -p` as a black box.
- **Forced response corruption.** `negative-missing-fence` patched the
  agent's response in flight to drop a fenced block; the new runner cannot
  do this.
- **Model-pin tracing across `task()` calls.** `negative-model-drift`
  asserted the orchestrator passed `model="…"` on every sub-agent dispatch;
  this was a harness-only observation point.
- **Layered L1/L2/L3 rubric overrides.** Replaced by ordinary `assert` lines
  in the test bodies plus the `scripts/lint_pack.py` static checker.

## Cases skipped or significantly reframed

| Pack | Legacy case id | Disposition | Why |
|------|----------------|-------------|-----|
| product-brief | `negative-orchestrator-direct-source-read` | Skipped | Required a per-tool read trace to prove the orchestrator never opened a source URL directly. |
| product-brief | `negative-model-drift` | Skipped | Required intercepting every `task(model=…)` call. |
| product-brief | `negative-missing-fence` | Skipped | Required corrupting the agent's response mid-flight to drop a fenced block. |
| product-brief | `negative-iteration-cap-breach` | Skipped | Required forcing the composer to fail N+1 times to provoke the iteration cap. |

## Cases reframed (kept, but with narrower assertions)

| Pack | Legacy case id | Reframing |
|------|----------------|-----------|
| story-telling-agent | `smoke-archetype-*` (8 cases) | Collapsed into a single parametrised pytest in `test_archetype_recipes.py`; the per-archetype structural assertion is now "deck-spec.json mentions the recipe name and the deck/QA artefacts exist". The legacy `archetype_check` informational expectations are no longer encoded — the pack's own `check_archetypes.py` script is the structural authority. |
| story-telling-agent | `smoke-template-mode` | Generates the placeholder `corporate-2026.pptx` via `python-pptx` inside the test; the legacy fixture asked the user to drop a real corporate template. The assertion stays focused on path round-trip (no theme verification). |
| story-telling-agent | `smoke-revision-then-approve`, `smoke-visual-qa-loop` | The legacy harness scripted multi-turn user replies via `scripted_user`. The pytest harness is single-turn; the prompt folds the simulated turn-state into a single user instruction and the test asserts on the final state.json counters (`proposal_iteration`, `qa_iteration`). |
| spec-author | `smoke-stop-a-disambiguation` | Same single-turn collapse: the prompt asks the agent to simulate the multi-turn disambiguation accounting in `state.json`. The test only asserts on the visible artefact contract. |
| All packs | All `invocations: { agent: { min, max } }` blocks | Dropped. The static linter validates the pack's tool/agent contract; per-eval invocation counts were noise, not signal. |

## What the static linter covers

The `scripts/lint_pack.py` checker runs once per pack (wired into pytest via
`evals/static/`) and validates the structural contract that L1/L2/L3
assertions used to repeat across every case:

- Every `.agent.md` has well-formed YAML front-matter with `name`, `description`, `tools`.
- Allowed/forbidden tool lists are enforced.
- Write scopes match the pack's documented STM root.
- Required README sections are present.
- Output-contract fenced-block names declared in the agent prompt are unique.

If a behaviour you used to validate in a per-eval `must_match` regex would
fit better as a pack-wide contract, add it to the linter rather than to a
new pytest case.

## Smoke-run findings (one test per pack)

After the migration the framework was smoke-tested with a single representative
test from each of the 5 packs. Two framework bugs and one Copilot CLI
behaviour quirk were uncovered and fixed; the remaining failures are real
content/agent issues to triage per pack.

### Framework fixes applied

- **`evals/_lib/copilot.py`** — `subprocess.run` was using Python's default
  Windows codec (cp1252) and crashing on the up/down-arrow glyphs in
  Copilot's "Tokens ↑ … ↓ …" footer, losing all stdout. Pinned to
  `encoding="utf-8", errors="replace"`.
- **`evals/_lib/copilot.py`** — `--allow-all-tools --allow-all-paths
  --no-ask-user` does **not** reliably grant write/shell perms in
  non-interactive mode; mid-session shell calls were being denied with
  `Permission denied and could not request permission from user`. Switched
  to `--allow-all --no-ask-user`. (`--allow-all` is the documented
  one-shot equivalent.)
- **`evals/_lib/copilot.py`** — On Windows, `subprocess.run([..., "-p",
  multi_line_prompt, ...])` routes through `copilot.CMD`, which **silently
  truncates the prompt at the first newline**. Every multi-line prompt in
  the suite was being delivered as just its first line, which is why so
  many tests reported "agent ignored the prompt" or "agent re-asked for
  information already in the prompt". Fixed by feeding the prompt via
  stdin (`subprocess.run(..., input=prompt)`) instead of `-p`. Stdin is
  preserved verbatim by both `copilot.CMD` and `copilot` on POSIX.
- **`evals/_lib/workspace.py`** — `stage_pack` previously auto-copied any
  top-level dot-prefixed directory from the source pack (e.g.
  `.story-telling-stm/`). Several packs ship a baked-in **demo session**
  inside their STM root (`runs/<session-id>/state.json` with
  `user_approved: true` and a complete deck), which polluted every test's
  workspace with a pre-populated session. Auto-staging removed; tests that
  need a seed STM stage it explicitly via `stage_files`.

### Smoke-test outcomes (post-fixes)

| Pack | Test | Result | Cause |
|------|------|--------|-------|
| copilot-factory | `test_smoke_issue_triage` | FAIL | `architecture.md` not produced — needs per-test triage. |
| product-brief | `test_smoke_late_stage_decision_ask` | FAIL | Copilot CLI denies many shell ops mid-session **even with `--allow-all`**, blocking the orchestrator from creating its STM tree. Reproducible only on this pack so far; likely a Copilot CLI quirk with multi-command shell strings under `--no-ask-user`. |
| spec-author | `test_smoke_publish_initial` | FAIL | The agent treats the prompt's explicit `**PUBLISH 0.1.0**` directive as ambiguous and re-asks the user to pick a target. Either the prompt needs to pre-supply the version selection (port issue) or the agent should accept inline `PUBLISH X.Y.Z` (agent issue). |
| story-telling-agent | `test_smoke_critical_gaps` | FAIL | Agent ran successfully but never wrote `state.json` to STM. Likely the agent's "needs-clarification" early-return path skips state initialisation; test should be rewritten to assert on visible chat output, or the agent should always emit a state stub. |
| story-telling-agent-rendering | `test_smoke_styled_recipe_render` | FAIL | Agent reports `story-orchestrator` not in available agents list (intermittent; succeeded on one of two runs). Possible flake in agent discovery or a test-ordering interaction. |

### Recommended follow-ups (out of scope for the smoke pass)

1. Investigate the product-brief shell-permission quirk (file a Copilot CLI
   bug if reproducible; otherwise add `--allow-tool='shell'` explicitly).
2. Tighten the spec-author test prompt to pre-supply `PUBLISH 0.1.0` as a
   "Pre-supplied answer" alongside Stop A.
3. Add a state.json stub requirement to the story-orchestrator
   "needs-clarification" branch, or rewrite `test_smoke_critical_gaps` to
   assert on stdout content rather than STM state.
4. Re-run all 60 tests in CI and triage the long tail; the baseline framework
   is now stable enough to do so.
