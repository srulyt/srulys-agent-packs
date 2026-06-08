# Chart Recipes (matplotlib)

Six matplotlib-based chart recipes consumed by `render_chart.py`.
Every recipe inherits the **Tufte data-ink rcParams** (spines top /
right off, no gridlines, single accent for the focal data point).

## Chart palette tokens (C11)

Recipes resolve colour from the `chart_palette` token block (see
`slide-design-systems` Token Schema), NOT just brand `primary`/
`secondary`:

| Token | Role |
|-------|------|
| `chart_focal` | the single "look here" series / bar — a deliberate focal colour, separate from brand `secondary` (which is muddy/branded in some systems) |
| `chart_muted` | every non-focal mark |
| `chart_grid`  | gridlines / axes when shown |
| `ramp` | categorical cycle for multi-series / ≥4-category charts |

`render_chart._palette()` derives these from `tokens.chart_palette`
(falling back to `secondary` / `text_secondary` when a system omits
them), so editable **native** charts and **rendered** PNGs share one
categorical theme.

## Number formatting & bar discipline (C11)

- **`_fmt_num(v, unit, decimals=1)`** — thousands separators, ≤1
  decimal, integers print without a trailing `.0`, optional unit suffix.
  Used for every direct value label.
- **Direct value labels** at bar ends (`value_labels: true` default),
  focal bold, rest in `chart_muted`. Pass `"unit": "%"` / `" k"` etc.
- **Bar width 0.62 / gap 0.38** on all bar recipes (no fat default bars).
- Axis title carries the unit when `y_label` + `unit` are both present.

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

The focal data point uses `pal["chart_focal"]`; all other marks use
`pal["chart_muted"]`. Annotations use `pal["highlight"]` for the arrow.

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

The bar with `value == max(values)` is rendered in `chart_focal`;
others in `chart_muted`. Each callout is an arrow + label pointing at
its data point. Direct value labels (thousands-separated, `unit`
suffix) sit at each bar end; bar width 0.62.

### `categorical_bars`

Spec:

```json
{
  "labels": ["NA", "EMEA", "APAC", "LATAM", "MEA"],
  "values": [12500, 9800, 15200, 4300, 2100],
  "focal": "APAC",
  "unit": "",
  "y_label": "Revenue",
  "title": "Revenue by region"
}
```

For ≥4-category charts. Bars cycle the `chart_palette.ramp`; the
optional `focal` (label or index) is promoted to `chart_focal`. Direct
value labels are thousands-separated. This is the categorical theme that
keeps native (editable) and rendered charts visually identical (C11).

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

Paired bars: `before` in `chart_muted`, `after` in `chart_focal`.
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
