# context-pack-builder evals

These evals cover the `context-pack-builder` plugin: a structural conformance
smoke (`test_smoke_plugin_conformance.py`, no CLI — manifest, agents/skills
dirs, marketplace registration, frontmatter quoting + supported keys, and that
no bundled `SKILL.md` body exceeds the single-source token threshold), a
happy-path NEW context pack (`test_smoke_new_context_pack.py`, judge), a
progressive-disclosure split case (`test_progressive_disclosure_split.py`), and
an idempotent update-over-rewrite case (`test_update_over_rewrite.py`,
no-duplicate + Change Log + human-edit preservation). The CLI-driven tests skip
automatically when the `copilot` CLI is unavailable.

Run them with:

```
pytest evals/packs/context-pack-builder/
```
