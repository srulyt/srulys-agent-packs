---
name: pptx-structural-asserts
description: "Programmatic python-pptx structural assertions for deck QA. Runs thirteen checks: text-frame overflow, contrast violations (luminance ratio), alignment-grid drift, repeated-layout-hash, title-underline spam, dark/light run length, missing speaker notes, duplicate titles, body-word density, plus three archetype-spec checks (waterfall zero-baseline algebra, decision_options column-width sum, risk_heatmap WCAG-AA contrast). Single entry point: check_pptx.py emits a merged JSON report consumed by @deck-critic. Keywords: structural QA, contrast, overflow, alignment grid, layout hash, archetype asserts, python-pptx assertions."
---

# PPTX Structural Asserts

Deterministic, fast, no-render-required structural QA. Loads the deck
via python-pptx and runs thirteen checks against shape geometry, text
frames, runs, notes, and (when a `--spec` is supplied) deck-spec
archetype invariants. Output is a single JSON report consumed by
`@deck-critic`.

## Pipeline / How to Invoke

`check_pptx.py` is the **only entry point** the production QA
pipeline (`@deck-critic` Step 2) calls. When invoked with `--spec`
it imports `check_archetypes.run()` from this same skill and merges
the archetype findings into the same report under
`archetype_violations`. Archetype `fail` statuses surface as
blocking findings (tagged `archetype.<check-id>`); `warn` statuses
surface as warning findings. Calling `check_archetypes.py` directly
is still supported for local debugging but is NOT part of the
production pipeline (no separate report file).

## When to Use This Skill

Load this skill when you are `@deck-critic` and need:

- A deterministic verdict on the deck's structure (independent of any
  render engine being installed)
- Pass/fail signals for: aspect-ratio, overflow, contrast, alignment,
  layout repetition, underline spam, dark/light rhythm, speaker notes,
  duplicate titles

## Files in This Skill

| File | Purpose |
|------|---------|
| [SKILL.md](SKILL.md) | This file |
| [scripts/check_pptx.py](scripts/check_pptx.py) | The check runner — loads pptx + deck-spec, emits JSON report |
| [scripts/check_archetypes.py](scripts/check_archetypes.py) | Cheap spec-level invariants for the 7 archetype recipes added in session 2026-05-04-c8d3b2a1 (waterfall zero-baseline algebra, decision_options column-width sum, risk_heatmap WCAG-AA contrast). Operates on `deck-spec.json` only — no .pptx parsing required. **Imported and run by `check_pptx.py` when `--spec` is supplied** (wired in fix iteration 1 of the same session). |

## Quick Use

```bash
python .github/skills/pptx-structural-asserts/scripts/check_pptx.py \
  --pptx <session>/agents/deck-builder/output.pptx \
  --spec <session>/agents/deck-builder/deck-spec.json \
  --out  <session>/agents/deck-critic/structural-report.json
```

Exit codes: `0` on script success (regardless of pass/fail of checks);
`1` on script error (file not found, malformed pptx, etc.).

## Checks (Severities)

| Check | Severity | Detection |
|-------|----------|-----------|
| `aspect_ratio_pass` | blocking | `prs.slide_width / prs.slide_height` ≈ 16:9 (±0.5%) |
| `overflow_violations` | blocking | Body text-frame text-length × est-line-height > frame height |
| `contrast_violations` | blocking | WCAG luminance ratio of run color vs slide bg <4.5:1 |
| `alignment_violations` | warn | Shape `left`/`top` not on 0.05" snap grid |
| `repeated_layout_hash` | blocking | Hash of (sorted shape positions, text-frame counts) repeats on consecutive slides |
| `title_underline_count` | blocking if >2 | Count of slides with a thin (≤0.05" tall) rectangle directly below title |
| `max_same_bg_run` | blocking if ≥3 | Longest run of consecutive slides with same fill color |
| `speaker_notes_missing` | blocking | Slides with empty `notes_text_frame.text` |
| `duplicate_titles` | blocking | Slides whose first text-frame matches another's |
| `body_word_max_violations` | warn | Slides with body text >70 words total |
| `archetype.waterfall.zero_baseline` | blocking | Spec-level: waterfall start + Σdeltas == end (±0.5%). Requires `--spec`. |
| `archetype.decision_options.columns_sum_to_slide_width` | warn | Spec-level: derived option-column widths sum to slide-content width within 0.05". Requires `--spec`. |
| `archetype.risk_heatmap.contrast_aa` | blocking | Spec-level: WHITE labels on green/amber/red heatmap cells clear WCAG AA normal-text 4.5:1. Requires `--spec`. |

## Report Schema

`structural-report.json` produced by `check_pptx.py`:

```json
{
  "session_id": null,
  "pptx_path": "...",
  "spec_path": "...",
  "slide_count": 12,
  "aspect_ratio": 1.7777,
  "aspect_ratio_pass": true,
  "overflow_violations": [{"slide": 7, "estimated_overflow_em": 1.4}],
  "contrast_violations": [{"slide": 4, "fg": "#A0A4B0", "bg": "#F4F5F7", "ratio": 2.1}],
  "alignment_violations": [{"slide": 3, "shape": "Body", "off_snap_axis": "left", "off_by_emu": 4571}],
  "repeated_layout_hash": [{"slides": [4, 5], "hash": "h:abc123"}],
  "title_underline_count": 1,
  "underline_slides": [2],
  "max_same_bg_run": 2,
  "background_sequence": ["dark", "light", "light", "dark", "light", "..."],
  "speaker_notes_missing": [],
  "duplicate_titles": [],
  "body_word_max_violations": [],
  "archetype_violations": [
    {"id": "waterfall.zero_baseline", "slide_index": 5,
     "status": "fail",
     "message": "waterfall algebra broken: start(100) + Σdeltas(+8) = 108, but end=120 (tol=0.6)..."}
  ],
  "archetype_runner_available": true,
  "blocking_findings": ["archetype.waterfall.zero_baseline"],
  "warning_findings": []
}
```

## Implementation Notes

- The script imports `python-pptx`. If unavailable, it auto-installs
  via `pip install python-pptx` (matching the deck-builder's behavior)
  before failing.
- Color comparisons traverse run → font → color → rgb. When color is
  inherited from the master/layout, the script falls back to the slide
  background and assumes default theme (note: this is a known false-
  negative; recorded in `report.notes`).
- Alignment snap is 0.05" = 45720 EMU (914400 EMU per inch × 0.05).
- Layout-hash combines: shape count, sorted (left, top, width, height)
  tuples rounded to 0.1", and text-frame count per slide.
- Background detection: read slide background fill if solid; else
  derive from the largest filled rectangle covering ≥90% of slide area
  (heuristic for blank-layout decks where background is implemented
  via an underlying full-bleed shape).

## Why Both Visual + Structural?

Visual QA catches "feels wrong" issues (focal point, density,
decorative shapes). Structural QA catches "is wrong" issues
(overflow, contrast, missing notes). Either alone is insufficient:
- Visual-only fails when render engine is missing.
- Structural-only misses purely visual antipatterns (5, 6).

`@deck-critic` runs both passes and combines findings.

## Rendering Subsystem Rebuild (2026-05-04)

scripts/check_pptx.py was rewritten in session
2026-05-04-7d3f9a2b. New / changed report fields:

- **overflow_violations** (F1) — now uses real Pillow text
  metrics per shape, with no slack tolerance, honouring
  `margin_left/right/top/bottom`, `space_before/after`, and
  paragraph `level` indentation. The font is resolved via the
  canonical `render-visual/assets/font_locator.find_dejavu_sans()`
  helper (C3).
- **contrast_violations** + **contrast_unresolved** (F4) —
  contrast pairs are now theme-resolved (background fill walks
  shape ↔ slide-background ↔ theme; text resolves through
  `a:solidFill` then theme `schemeClr`). Pairs that cannot
  resolve to a concrete RGB land in `contrast_unresolved`
  (separate from `contrast_violations`). The deck-critic
  treats `contrast_unresolved >= 5` as a BLOCKING revise.
- **g_label_threshold** (F7) — saturation-aware. Hard-coded
  thresholds: `sat > 0.45` → accent regardless of luminance;
  `lum < 0.18` → dark; `lum > 0.72` → light; else accent
  (C4). The previous luminance-only heuristic mis-classified
  saturated brand backgrounds as `light` / `dark`.
- **dark_light_run** (F8) — thresholds: `>= 3` warn;
  `>= 7` BLOCKING; `>= 5 with no accent break` BLOCKING.
- **ody_word_max** (F11) — canonical limit lowered from
  70 to **30** words per body. Flagged in
  `body_density_violations`.
- **ont_fallback** — when the canonical DejaVu Sans bundle
  is unavailable and PIL bitmap-default is used as a last
  resort, this field surfaces so the critic can warn that
  overflow metrics are approximate.
