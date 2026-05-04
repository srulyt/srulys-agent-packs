# Chart Recipes (matplotlib)

Five matplotlib-based chart recipes consumed by `render_chart.py`.
Every recipe inherits the **Tufte data-ink rcParams** (spines top /
right off, no gridlines, single accent for the focal data point).

## Tufte rcParams (applied by `_apply_tufte_rc`)

```python
plt.rcParams.update({
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": True,
    "axes.spines.bottom": True,
    "axes.grid": False,
    "figure.facecolor":  pal["bg_dark"],   # or bg_light when --on-light
    "axes.facecolor":    pal["bg_dark"],
    "savefig.facecolor": pal["bg_dark"],
    "text.color":        pal["text_dark"],
    "axes.labelcolor":   pal["text_secondary"],
    "xtick.color":       pal["text_secondary"],
    "ytick.color":       pal["text_secondary"],
    "axes.edgecolor":    pal["text_secondary"],
    "font.size": 14,
})
```

The focal data point uses `pal["secondary"]` (typically a brand
green); all other marks use `pal["primary"]` or `pal["text_secondary"]`.
Annotations use `pal["highlight"]` for the arrow.

## Recipes

### `bar_with_callouts`

Spec:

```json
{
  "labels": ["FY24", "FY25", "FY26", "FY27"],
  "values": [12, 18, 31, 47],
  "y_label": "Customers (k)",
  "title": "Customers grew 4× since FY24",
  "callouts": [
    {"x": "FY27", "y": 47, "text": "+51% YoY"}
  ]
}
```

The bar with `value == max(values)` is rendered in `secondary`;
others in `primary`. Each callout is an arrow + label pointing at
its data point.

### `donut`

Spec:

```json
{"pct": 0.73, "big_number": "73%", "label": "of users prefer the new flow"}
```

Renders a thin (22% radius) ring; foreground arc in `secondary`,
background arc in `text_secondary`. Big number centred at 72pt
bold.

### `sparkline`

Spec:

```json
{
  "series": [12, 14, 15, 19, 23, 31, 47],
  "x_labels": ["W1","W2","W3","W4","W5","W6","W7"],
  "title": "Weekly active sessions"
}
```

Thin line in `primary`; end-marker in `highlight`; the final value
is annotated to the right of the marker. Y-ticks suppressed (Tufte
data-ink).

### `dual_bar_diff`

Spec:

```json
{
  "labels": ["Latency", "Errors", "Cost"],
  "before": [820, 14, 100],
  "after":  [180,  3,  62],
  "before_label": "Pre-launch",
  "after_label":  "Post-launch",
  "title": "Three metrics improved together"
}
```

Paired bars: `before` in `text_secondary`, `after` in `secondary`.
Legend in the upper-right. No gridlines.

### `progress_strip`

Spec:

```json
{
  "steps": [
    {"label": "Discovery",  "subtext": "Weeks 1–2"},
    {"label": "Prototype",  "subtext": "Weeks 3–6"},
    {"label": "Pilot",      "subtext": "Weeks 7–10"},
    {"label": "Rollout",    "subtext": "Weeks 11–14"},
    {"label": "Full launch","subtext": "Week 15"}
  ]
}
```

Horizontal axhline + N numbered scatter markers in `primary`. Each
step gets a 20pt label above the line and a 14pt subtext below.
Used by the `progress_dots` styled `cta_steps` recipe.

## Open-Question bindings

- **OQ3** — call `render_chart.py --svg` to emit an SVG peer
  (`<out>.svg`) alongside the PNG. Matplotlib emits SVG natively
  via `savefig(format='svg')`; no rasterisation.

## Determinism notes

matplotlib's font cache builds on first import. The deck-builder
should pre-warm via `python -c "import matplotlib.font_manager"`
before the first chart render to avoid 5-15s first-call latency in
CI.

Random seeds: none of these recipes use randomness. Same `(spec,
tokens)` → same bytes (modulo OS-level font-rasteriser drift on
glyph hinting; cosmetic only, not test-failing).
