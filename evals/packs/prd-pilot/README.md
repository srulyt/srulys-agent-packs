# PRD Pilot — pack-level evals

These evals cover the **packaging** of the conformant agent plugin
(`agent-packs/prd-pilot/`). `test_smoke_plugin_conformance.py` is a
deterministic, structural smoke (no Copilot CLI / LLM judge): it asserts
`plugin.json` is conformant (valid kebab-case `name`, resolvable `skills/`
path), that all four skill subdirs hold a `SKILL.md` whose `name` equals
its directory name, that the entry skill `ears-prd-workflow` is
`user-invocable: true`, that the legacy `.github/` tree is gone, and that
the README documents the install flow for all three hosts (VS Code,
Copilot CLI, `gh skill`).

The **behavioural** skill evals (the workflow, EARS shape, grill-me
discipline, outline-rejection loop) live under `evals/skills/<skill>/` and
require the `copilot` CLI; the eval harness `stage_skill()` resolves the
plugin-root `skills/<skill>` layout automatically.

Run them with:

```
pytest evals/packs/prd-pilot/
```
