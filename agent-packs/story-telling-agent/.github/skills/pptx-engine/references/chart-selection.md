# Chart Selection by Relationship

> **Purpose**: Choose the chart **type** before authoring the chart. The
> python-pptx + matplotlib API tells you *how* to draw a chart;
> this reference tells you *which* chart to draw.
>
> **Source**: research §G (story-telling-theory.md lines 143–165),
> ported into the canonical `pptx-engine` home in session
> `2026-05-04-5707a9ef`.
>
> **Linked from**: [`pptx-engine/SKILL.md`](../SKILL.md),
> [`presentation-design/SKILL.md`](../../presentation-design/SKILL.md)
> (Layout Composition / Visual Hero sections).

## The Relationship → Chart-Type Matrix

Pick the row that matches the *relationship* the slide's assertion is making, then
pick the leftmost chart that fits the data scale.

| Relationship the assertion makes | Default chart | Acceptable alternatives | Avoid |
|---|---|---|---|
| **Trend over time** | Line | Area, slopegraph, small multiples | 3D line, stacked area when categories matter individually |
| **Comparison (across categories)** | Sorted bar | Dot plot, lollipop, simple table | Pie, donut |
| **Composition (parts of whole)** | Stacked bar | Treemap (only when many small parts), waterfall (when contribution-to-change matters) | Pie/donut except for very simple 2–3 part splits |
| **Distribution** | Histogram | Box plot, strip plot | Bar with arbitrary binning |
| **Correlation** | Scatter | Bubble (only if a third variable matters) | Bubble for decoration |
| **Flow / sequence** | Sankey or process arrows | Funnel, waterfall (value bridge) | Generic flow diagrams that don't show quantity |
| **Ranking** | Sorted bar | Dot plot | Unsorted bar |
| **Geospatial** | Map | — | Map when the spatial dimension is incidental — use a bar instead |

When two rows are plausible, the **assertion** decides. "Revenue grew Q1→Q4"
is a *trend* (line). "Q4 was our biggest quarter" is a *comparison* (sorted
bar with Q4 highlighted). The chart type encodes the claim.

## Hard Rules

1. **No 3D charts.** They distort proportions and add visual noise without
   carrying information.
2. **No pie / donut except for trivial part-to-whole** with 2–3 categories
   where each slice is clearly distinguishable. For anything else use a
   stacked bar.
3. **Bars start at zero** unless an axis break is explicitly drawn and
   labelled. Truncated bars are how charts lie.
4. **Direct labels over legends** wherever feasible. A legend forces the
   eye to leave the data, look up a colour, and come back. End-of-line
   labels, in-slice labels, or callout annotations are stronger.
5. **One dominant data point** per chart. De-emphasise everything else
   with grey / lower opacity. The chart should answer "where do I look?"
   in 3 seconds.
6. **Annotate the so-what.** Every chart gets at least one annotation
   (arrow + text) explaining the takeaway. If you can't write an
   annotation, the chart isn't carrying an insight.

## Title Discipline (Chart Title vs Slide Title)

A chart and the slide that contains it have **two titles** with **two
different jobs**:

| Element | Voice | Example |
|---|---|---|
| **Slide title** | Assertive — the takeaway | *"Revenue exploded 40% — and we're just getting started"* |
| **Chart title** (above axes) | Descriptive — what the data is | *"Quarterly revenue, FY24–FY25 ($M)"* |

If the chart title and the slide title repeat, drop one. Usually drop the
chart title and keep the slide title; if the slide is annotated heavily
the chart title can be the descriptive label and the slide title carries
the verdict.

## Sources, Units, Notes

Every chart that uses sourced or assumption-laden data MUST include:

- **Source line** (≤12 words, 9–10pt, light gray) below the chart, e.g.
  *"Source: internal billing data, FY25 Q1; excludes promo credits"*.
- **Unit indicator** in the axis label or chart title (`$M`, `%`,
  `users / day`).
- **Assumption note** when the data has been smoothed, normalized, or
  forecast — say so explicitly.

These map directly to the `pptx-structural-asserts` checks
`source_note_present` (per-element copy budget reference) and to the
visual rubric `chart_legibility` / `axis_units_present` heuristics.

## Common Chart Failures (and the Fix)

| Failure | Detection | Fix |
|---|---|---|
| Pie with 6+ slices | visual rubric `chart_pie_slice_count > 4` | Convert to stacked bar |
| 3D bar | visual rubric `chart_3d_present: true` | Flatten to 2D |
| Truncated y-axis without label | structural — bar chart with `axis_min > 0` and no break marker | Set `axis_min=0` or add explicit axis break |
| Legend with one data series | visual rubric | Direct-label inline |
| No annotation | visual rubric `chart_annotation_present: false` | Add arrow + ≤20-word callout for the takeaway |
| Missing units | visual rubric | Append unit to axis label |
| Misleading dual-axis | visual rubric `chart_dual_axis: true` | Split into two charts or reframe as ratio |
| Small multiples without shared scale | visual rubric | Use shared y-axis across panels |

## Native editable charts vs rendered PNGs (C2)

Two ways to put a chart on a slide, with a deliberate split:

- **Native python-pptx charts** (`chart_part` via
  `slide.shapes.add_chart(XL_CHART_TYPE.*, x, y, cx, cy, CategoryChartData)`)
  — the chart stays **editable in PowerPoint**: the end user can retheme
  it, change the data, and restyle series. **Prefer native** for the
  *standard* relationships below. Source:
  <https://python-pptx.readthedocs.io/en/latest/user/charts.html>.
- **Rendered PNGs** (`render-visual` matplotlib → `add_picture`) —
  pixel-perfect, Tufte-grade control, but **not editable**. **Reserve**
  for non-native / bespoke types (slopegraph, waterfall, sparkline,
  small multiples, heatmap, Sankey).

| Relationship / chart | Native python-pptx | `XL_CHART_TYPE` | Else render PNG |
|---|---|---|---|
| Comparison — sorted bar | ✅ native | `BAR_CLUSTERED` / `COLUMN_CLUSTERED` | — |
| Trend over time — line | ✅ native | `LINE` / `LINE_MARKERS` | — |
| Composition — stacked bar | ✅ native | `COLUMN_STACKED` / `BAR_STACKED` | — |
| Part-of-whole (2–3 parts) — pie | ✅ native (trivial only) | `PIE` / `DOUGHNUT` | — |
| Slopegraph | ❌ | — | ✅ `render-visual` |
| Waterfall / value bridge | ❌ | — | ✅ `render-visual` (TODO recipe) |
| Sparkline | ❌ | — | ✅ `render-visual` `sparkline` |
| Distribution (histogram/box) | ❌ | — | ✅ `render-visual` |
| Correlation — scatter/bubble | ⚠️ native `XY_SCATTER` ok; bespoke → PNG | `XY_SCATTER` | for annotated/bubble |
| Risk heatmap / 2×2 | ❌ | — | ✅ `render-visual` (TODO) |
| Funnel / flywheel / Sankey | ❌ | — | ✅ `render-visual` (TODO) |

> **Decision record.** Native charts trade Tufte-grade pixel control for
> editability. For standard bar/line/pie this is the right default — an
> editable chart the user can retheme beats a locked PNG. Mark each chart
> in `deck-spec.json` with `"chart_render": "native"` or `"rendered"` so
> the builder dispatches correctly and the critic knows which is which.
> Count native charts in the builder-summary `visual-assets-native-charts`.

## Mapping to the Existing Renderer

The `render-visual` skill provides matplotlib recipes that already
implement most of the above:

| Chart type | Recipe (existing) | Native alt? | Status |
|---|---|---|---|
| Bar (with annotation callouts) | `bar_with_callouts` (`render_chart.py`) | ✅ `BAR_CLUSTERED` when no bespoke annotation | ✅ |
| Line / sparkline | `sparkline` (`render_chart.py`) | ✅ `LINE` (sparkline stays PNG) | ✅ |
| Stacked / dual bar | `dual_bar_diff` (`render_chart.py`) | ✅ `COLUMN_STACKED` | ✅ |
| Donut (trivial only) | `donut` (`render_chart.py`) | ✅ `DOUGHNUT`/`PIE` (≤3 parts) | ✅ — guard against ≥4 slices |
| Progress / step indicator | `progress_strip` (`render_chart.py`) | ❌ | ✅ |
| Waterfall / value bridge | — | ❌ | **TODO** — gated on layout-archetypes P3 |
| Risk heatmap / 2x2 matrix | — | ❌ | **TODO** — gated on layout-archetypes P3 |
| Funnel / flywheel / Sankey | — | ❌ | **TODO** — gated on layout-archetypes P3 |

When the chart is a *standard* bar/line/pie and carries no bespoke
annotation that only matplotlib can draw, prefer the **native**
python-pptx chart (editable); otherwise prefer the matplotlib recipe;
when neither exists, document the "chart-not-yet-renderable" gap in the
proposal and use the closest existing recipe (e.g. sorted bar in lieu of
waterfall).
