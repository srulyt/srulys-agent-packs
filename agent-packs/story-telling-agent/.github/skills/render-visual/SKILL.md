---
name: render-visual
description: "Code-rendered static visuals for PowerPoint decks. Three deterministic JSON-spec → PNG/SVG pipelines: matplotlib charts (bar_with_callouts, donut, sparkline, dual_bar_diff, progress_strip), PIL composites (gradient_pattern, oversized_glyph_bg), and Graphviz diagrams (flow_diagram, system_diagram). Loaded by @deck-builder; pre-renders slides[].visual_assets[] before deck assembly. Keywords: matplotlib, PIL, Pillow, Graphviz, chart, diagram, gradient, render, visual_assets, deterministic."
---

# Render Visual

Deterministic, code-rendered static visuals for the story-telling
agent's PowerPoint pipeline. Each script reads a JSON spec on stdin
or via `--spec`, plus the `design_system_tokens` block via
`--tokens`, and emits a single PNG (and an SVG peer when the engine
natively produces one — see OQ3) at the specified path.

## When to Use This Skill

Load this skill when you are `@deck-builder` and the deck-spec lists
`slides[].visual_assets[]` entries with
`produced_by: "render-visual:<recipe>"`. Pre-render every entry
**before** invoking `generate_deck.py`; the styled builders embed
the resulting PNGs via `slide.shapes.add_picture`.

Do NOT load this skill from `@deck-critic` — the critic consumes the
already-rendered assets via `@deck-builder`'s `builder-summary` and
the rendered deck.pptx.

## Pipeline

```
deck-spec.json (slides[].visual_assets[])
       │
       ▼  per asset
render-visual:<recipe> → render_chart.py | render_composite.py | render_diagram.py
       │
       ▼  --spec spec.json --tokens tokens.json --out PATH.png [--size WxH] [--svg]
PNG (1920x1080 default) [+ SVG peer when --svg AND engine supports vector]
       │
       ▼  generate_deck.py reads visual_assets[].path → add_picture
deck.pptx
```

## Files in This Skill

| File | Purpose |
|------|---------|
| `SKILL.md` | This file |
| `references/chart-recipes.md` | matplotlib recipes; Tufte data-ink rcParams |
| `references/composite-recipes.md` | PIL composite recipes |
| `references/diagram-recipes.md` | Graphviz recipes; OQ2 graceful-degrade behaviour |
| `references/recipe-mapping.md` | slide-class → recipe mapping table |
| `scripts/render_chart.py` | matplotlib CLI (5 recipes) |
| `scripts/render_composite.py` | PIL CLI (2 recipes) |
| `scripts/render_diagram.py` | Graphviz CLI (2 recipes) |
| `assets/font_locator.py` | Single source for DejaVuSans.ttf path (see C3) |
| `assets/DejaVuSans.LICENSE.md` | DejaVu Bitstream license |
| `assets/README.md` | How the canonical font location works |

## Recipe Inventory

| Recipe | Script | Lib | Slide-class default |
|--------|--------|-----|---------------------|
| `bar_with_callouts` | render_chart.py | matplotlib | `data_callout` |
| `donut` | render_chart.py | matplotlib | `metric_spotlight` w/ ratio |
| `sparkline` | render_chart.py | matplotlib | `metric_spotlight` w/ series |
| `dual_bar_diff` | render_chart.py | matplotlib | `comparison_columns` |
| `progress_strip` | render_chart.py | matplotlib | `cta_steps` styled |
| `gradient_pattern` | render_composite.py | PIL | `section_divider` styled (hero_full_bleed bg) |
| `oversized_glyph_bg` | render_composite.py | PIL | `quote` styled |
| `flow_diagram` | render_diagram.py | Graphviz | `visual_hero` (nodes/edges) |
| `system_diagram` | render_diagram.py | Graphviz | `visual_hero` (boxes) |

## Contract

- **Input**: `--spec spec.json --tokens tokens.json --out OUT.png
  [--size WIDTHxHEIGHT] [--svg]`
- **Output**: PNG file at `OUT`. When `--svg` is passed AND the
  engine emits SVG natively (matplotlib `savefig(format='svg')`,
  Graphviz `dot -Tsvg`), an SVG peer is written next to the PNG with
  the same basename (`OUT.svg`). PIL composites are PNG-only — SVG
  is *not* rasterised back from PNG (per OQ3 / decisions.md
  2026-05-04T14:50Z).
- **Determinism**: same `(spec, tokens)` → same bytes (modulo
  matplotlib's font-cache first-run jitter; pre-warm with
  `python -c "import matplotlib.font_manager"`).
- **Exit codes**: `0` success, `2` bad spec, `3` engine missing
  (Graphviz only — the script writes a clear stderr install hint and
  exits 0 with a `--skip-on-missing` flag passed by deck-builder so
  the deck doesn't block on a missing dot binary).
- **Output path**: by convention,
  `<stm-run>/agents/deck-builder/renders/slide-<idx>-<recipe>.png`.

## Open-Question bindings

This skill bakes in the user's binding answers from `decisions.md`
(session 2026-05-04-7d3f9a2b):

- **OQ1** — No aspose-slides anywhere. The render-visual scripts use
  matplotlib (BSD), Pillow (HPND/MIT), and Graphviz (CPL). All
  permissively licensed for commercial use.
- **OQ2** — `render_diagram.py` attempts `pip install graphviz`
  (Python binding) and probes for `dot` on PATH. If `dot` is missing,
  emits OS-specific install instructions and **degrades gracefully**:
  the script exits 0 (with a non-zero status field in stdout JSON)
  and the deck-builder marks the asset as `skipped: true` in
  `qa-report.json` rather than blocking the deck. Diagram-class
  visuals are non-essential in v1.
- **OQ3** — SVG is emitted as a peer to PNG when `--svg` is passed
  AND the engine produces vector natively. Never rasterise back from
  PNG.
- **OQ4** — title slides default to `style: simple`; only
  `section_divider` defaults to `styled / hero_full_bleed`.

## Tufte / Reynolds canon

The matplotlib recipes inherit a Tufte-aligned rcParams snippet
(spines off, gridlines off, single accent for focal point). See
`references/chart-recipes.md`.

## Composition with `@deck-builder`

```bash
# Pre-render phase (before generate_deck.py)
python .github/skills/render-visual/scripts/render_chart.py \
    --kind bar_with_callouts \
    --spec  <stm-run>/agents/deck-builder/_specs/slide-9-trend.json \
    --tokens <stm-run>/agents/deck-builder/_specs/tokens.json \
    --out   <stm-run>/agents/deck-builder/renders/slide-9-trend.png \
    --size  1920x1080 \
    --svg

# Then deck assembly (generate_deck.py picks up the PNG via
# slide.visual_assets[].path)
python .github/skills/pptx-engine/scripts/generate_deck.py \
    --spec   <stm-run>/agents/deck-builder/deck-spec.json \
    --output <stm-run>/agents/deck-builder/output.pptx
```

## See Also

- [`chart-recipes.md`](references/chart-recipes.md)
- [`composite-recipes.md`](references/composite-recipes.md)
- [`diagram-recipes.md`](references/diagram-recipes.md)
- [`recipe-mapping.md`](references/recipe-mapping.md)
- [`pptx-engine/references/styled-recipes.md`](../pptx-engine/references/styled-recipes.md) — how the produced PNGs are embedded in styled slides.
