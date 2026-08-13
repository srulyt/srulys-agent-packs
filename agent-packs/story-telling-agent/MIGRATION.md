# Migration to v3

The plugin root is now canonical. `@story-orchestrator`, `output.pptx`, `output.md`, `deck-spec.json`, and `qa-report.json` remain stable. Old `@story-strategist` maps to Narrative Strategist and `@deck-builder` maps to Deck Composer, but specialists are no longer directly user-invocable.

Legacy skills mapped as follows: `slide-design-systems` → `design-systems`; the old proposal/schema handoff guidance → `deck-contracts`; old research/citation guidance → `evidence-provenance`; `render-visual` chart guidance → `data-storytelling` plus renderer code; `slide-critique` → `pptx-visual-qa`. Preserved names are `narrative-craft`, `presentation-design`, `pptx-engine`, `marp-engine`, `pptx-structural-asserts`, and `pptx-visual-qa`. Newly separated: `executive-communication`, `data-storytelling`, and `imagery-accessibility`.

Do not copy the former `.story-telling-stm` state. Run `migrate_v2_to_v3.py`; it exports recognized context/proposals/assets and emits `restart-required`, because v2 lacked independent receipts and immutable publication lineage. Use `install-legacy-layout.py` only when a consumer requires `.github/agents` and `.github/skills`.
