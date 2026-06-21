# Product Knowledge Brain — Evals

These evals cover the `product-knowledge-brain` skills-only plugin. The
structural conformance smoke (`test_smoke_plugin_conformance.py`) runs in
plain CI with no `copilot` binary and guards the plugin packaging (manifest,
four skills with role-correct `user-invocable` flags, quoted descriptions,
skills-only layout, three install flows in the README). A second structural
test (`test_install_script_namespacing.py`, also no CLI) guards the 2026-06-11
**design pivot** at the spec layer: it asserts the install-script reference doc
encodes **namespace-at-install** (bare source dirs renamed to `<kb-ns>-<bare>`
on copy, with the copied `SKILL.md` `name:` rewritten), the
`installed-skills.json` **receipt**, and **uninstall-on-change** scoped to the
KB namespace — in both the `.sh` and `.ps1` skeletons. The behavioural pack
evals shell out to the `copilot` CLI (tagged `slow`, some `judge`) and
exercise the knowledge-evolution cycle end to end: consolidation produces
curated *living* pages, the durable STM checkpoint survives a simulated
context compaction without duplicating pages, overlapping input updates an
existing page instead of creating a near-duplicate, pages carry evidence
provenance and typed relationship links, discovery/area indexes are
refreshed, and — under the **install-script model** — generated index skills
stay in the KB at `<kb-root>/_skills/` with **bare** names (namespacing is
applied at install time) while the agent emits an **install script**
(`install-skills.sh`/`.ps1`) and a **`removed-skills.json`** manifest for the
user to run. The index-skill set scales with KB size and caller intent:
`test_top_level_index_skill_and_install.py` checks the top-level router on an
**explicit repo-wide request** (a small KB that explicitly asks for the
top-level / repo-wide index skill gets the bare `knowledge-index`,
`user-invocable: true`, plus the install artifacts), and
`test_dynamic_index_skill_generation.py` checks the per-area skill on an
**explicit request + crowded area** (a past-threshold area with an explicit
feature-a request produces a bare per-area skill `feature-a-knowledge-index`,
and asserts the source dirs are NOT namespace-prefixed). Run them with
`pytest evals/packs/product-knowledge-brain/`.

## Bounding the live-SUT loop (budget controls)

The seven behavioural evals each drive the *live* Copilot CLI (one runs it
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

