# Product Knowledge Brain — Evals

These evals cover the `product-knowledge-brain` skills-only plugin. The
structural conformance smoke (`test_smoke_plugin_conformance.py`) runs in
plain CI with no `copilot` binary and guards the plugin packaging (manifest,
four skills with role-correct `user-invocable` flags, quoted descriptions,
skills-only layout, three install flows in the README). The six behavioural
pack evals shell out to the `copilot` CLI (tagged `slow`, some `judge`) and
exercise the knowledge-evolution cycle end to end: consolidation produces
curated *living* pages, the durable STM checkpoint survives a simulated
context compaction without duplicating pages, overlapping input updates an
existing page instead of creating a near-duplicate, pages carry evidence
provenance and typed relationship links, discovery/area indexes are
refreshed, and a past-threshold area triggers generation of a dynamic
specialized index skill. Run them with
`pytest evals/packs/product-knowledge-brain/`.

## Bounding the live-SUT loop (budget controls)

The six behavioural evals each drive the *live* Copilot CLI (one runs it
twice), so a single slow/non-responsive SUT call can otherwise consume the
whole eval-fix-loop wall-clock budget and starve the rest of the suite. Two
opt-in, backward-compatible env controls (implemented in
`evals/_lib/copilot.py`) keep the suite terminating deterministically:

- **`EVALS_SUT_TIMEOUT=<seconds>`** — clamps every SUT subprocess timeout to
  `min(requested, cap)`. A hung/slow SUT is force-killed at the cap
  (returncode 124, `result.timed_out`), and the behavioural tests then
  `pytest.skip` instead of hanging or hard-failing. Set this to fit the
  runner's per-loop budget (e.g. `EVALS_SUT_TIMEOUT=180`).
- **`EVALS_SKIP_SUT=1`** — does not launch the SUT at all; behavioural tests
  skip cleanly (`result.skipped`, returncode 125) with zero tokens. Use when
  the environment cannot run the live LLM SUT within budget. The structural
  conformance smoke still runs.

Neither var is set by default, so a normal `copilot`-present run behaves
exactly as before. The harness controls are pinned by the deterministic,
no-SUT regression guard `evals/static/test_sut_budget_controls.py`.

