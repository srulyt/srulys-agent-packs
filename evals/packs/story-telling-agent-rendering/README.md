# story-telling-agent — rendering & verify-or-block evals

Render-path and verify-or-block smoke evals for the `story-telling-agent`
pack (the deck-build → QA loop). These complement the narrative/build
smoke cases in `evals/packs/story-telling-agent/`.

Coverage:

- **Render path** — styled-recipe render, low-contrast, overflow, palette
  preflight rollback.
- **pypdfium2 render path (B1)** — `test_smoke_pypdfium2_render_path.py`:
  hang-safe, no-LLM tooling test that drives `generate_deck.py` →
  `render_pptx.py` directly and asserts pypdfium2 is the preferred
  pdf→png engine (poppler fallback only; no AGPL PyMuPDF) and that the
  full pipeline produces per-slide PNGs at 150 DPI.
- **New systems + archetypes (C4/C6)** —
  `test_smoke_new_system_archetype_structural.py`: builds a deck with a
  new premium system (`ink-editorial`) and the editorial archetypes and
  asserts no overflow / safe-area / archetype-shape violations.
- **Aesthetic craft + charts (C5/C11)** —
  `test_smoke_aesthetic_craft_and_charts.py`: asserts the `aesthetic_craft`
  rubric axis + critic wiring + 150-DPI default, and that
  `categorical_bars` consumes `chart_palette` with thousands-separated
  number formatting.
- **Verify-or-block (B3)** — `test_smoke_render_skipped_on_styled.py`
  (styled deck + no engine → blocking `render_unverified`) and
  `test_smoke_no_engine_user_gate.py` (simple-only deck + no engine →
  explicit `unverified-needs-user` user-decision gate, never a silent
  pass).
- **Output modes (B1/B2)** — `test_smoke_marp_mode.py`
  (`output_mode=marp` routes to the marp-engine path and renders-or-blocks
  gracefully) and `test_smoke_both_mode.py` (`output_mode=both` builds a
  native python-pptx deck AND a Marp source-of-record).

Run them:

```bash
pytest evals/packs/story-telling-agent-rendering/
```

The `@pytest.mark.pack` + `@pytest.mark.slow` cases invoke the real
`copilot` CLI and need it on PATH (or `COPILOT_BIN` set). The three new
tooling smoke tests (pypdfium2 / new-system-archetype / aesthetic-craft)
are hang-safe and need no CLI — they drive the pack scripts directly via
bounded subprocess and run in any CI with `python-pptx` + `pypdfium2`.
