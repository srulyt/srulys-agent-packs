# Visual Rubric (Per-Slide)

> The rubric `@deck-critic` applies to each rendered `slide-{N}.png`.
> Output goes into `qa-report.json` at `.visual.per_slide[]`.

## Table of Contents

1. [Rubric Axes](#rubric-axes)
2. [Scoring Per Axis](#scoring-per-axis)
3. [Antipattern Detection (Visual Cues)](#antipattern-detection-visual-cues)
4. [Per-Slide JSON Schema](#per-slide-json-schema)
5. [Worked Example](#worked-example)

## Rubric Axes

For each rendered PNG, record:

| Axis | Question | Output |
|------|----------|--------|
| **Hierarchy** | Can you identify ONE focal point in 3 seconds? | `focal_point_present: bool`, `focal_element: str` |
| **Density** | How much of the slide is covered with content? | `text_density: low\|medium\|high` (rough text-area-to-slide ratio: <25% / 25–50% / >50%) |
| **Contrast** | Is all text legible against its background? | `contrast_pass: bool` (eyeball; structural-asserts has the precise ratio) |
| **Alignment** | Are elements visually aligned? | `alignment_label: aligned\|mostly\|misaligned` |
| **Accent Usage** | Are accents purposeful (not decorative)? | `accent_purposeful: bool` |
| **Image Use** | If image present, does it carry meaning? | `image_meaningful: bool\|null` |
| **Type Scale** | Does typography follow a coherent scale? | `type_scale_coherent: bool` |
| **Layout Label** | Which layout-type best describes this slide? | `layout_label: <vocab from presentation-design>` |
| **Antipatterns** | Which `slide-critique` antipatterns apply? | `antipatterns: int[]` (IDs 1–10) |

## Scoring Per Axis

Use the rubric to flag, not to numerically score. A slide passes the
visual section when:

- `focal_point_present == true`
- `text_density != "high"`
- `contrast_pass == true`
- `alignment_label in ["aligned", "mostly-aligned"]`
- `accent_purposeful == true`
- `type_scale_coherent == true`
- `len(antipatterns) <= 1`

A slide fails the visual section when any of:

- `focal_point_present == false` → antipattern 5 (uniform visual weight)
- `text_density == "high"` → antipattern 3 (text-heavy)
- `contrast_pass == false` → antipattern 10 (low contrast)
- `alignment_label == "misaligned"` → flag for builder
- `accent_purposeful == false` → antipattern 6 (decorative shapes)
- `len(antipatterns) >= 2` → flag

## Antipattern Detection (Visual Cues)

| ID | Antipattern | Visual Cue in PNG |
|----|-------------|------------------|
| 1 | Accent line under every title | Thin colored bar 2–6px below title; check if appears on >2 slides |
| 2 | Identical layout repetition | This slide's geometry visually identical to previous |
| 3 | Text-heavy | Body region fills >50% of slide |
| 4 | Generic palette | Only default blue + white, no audience-tuned color |
| 5 | Uniform visual weight | No one element clearly dominant |
| 6 | Decorative shapes | Geometric shapes with no labels / no data |
| 7 | Missing rhythm | (cross-deck — not per-slide) |
| 8 | Missing speaker notes | (structural — not visual) |
| 9 | Duplicate titles | (structural) |
| 10 | Low-contrast text | Body text washed out / hard to read |

## Per-Slide JSON Schema

Each entry in `qa-report.json` at `.visual.per_slide[]`:

```json
{
  "index": 3,
  "png_path": "renders/slide-3.png",
  "layout_label": "Headline + bullets",
  "focal_point_present": true,
  "focal_element": "title",
  "text_density": "medium",
  "contrast_pass": true,
  "alignment_label": "aligned",
  "accent_purposeful": true,
  "image_meaningful": null,
  "type_scale_coherent": true,
  "antipatterns": [],
  "notes": "Bullets parallel and concise; left stripe anchors well."
}
```

## Worked Example

> Slide 5 from a generated buy-in deck. The PNG shows a headline
> "Three reasons we're winning Q4" at 40pt navy on off-white, a left
> navy stripe, and 4 bullets at 22pt with parallel structure. No
> accent line under the title.

```json
{
  "index": 5,
  "png_path": "renders/slide-5.png",
  "layout_label": "Headline + bullets",
  "focal_point_present": true,
  "focal_element": "title",
  "text_density": "medium",
  "contrast_pass": true,
  "alignment_label": "aligned",
  "accent_purposeful": true,
  "image_meaningful": null,
  "type_scale_coherent": true,
  "antipatterns": [],
  "notes": "Clean headline+bullets pattern; no antipatterns."
}
```

> Same deck, slide 7 shows the same layout with 6 bullets, body region
> filling ~60% of slide, and a thin teal underline below the title.

```json
{
  "index": 7,
  "png_path": "renders/slide-7.png",
  "layout_label": "Headline + bullets",
  "focal_point_present": false,
  "focal_element": null,
  "text_density": "high",
  "contrast_pass": true,
  "alignment_label": "mostly-aligned",
  "accent_purposeful": false,
  "image_meaningful": null,
  "type_scale_coherent": true,
  "antipatterns": [1, 3, 5],
  "notes": "Title underline + 6 bullets > 4 max + no clear focal point."
}
```
