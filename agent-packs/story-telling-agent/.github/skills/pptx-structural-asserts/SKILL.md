---
name: pptx-structural-asserts
description: "Programmatic python-pptx structural assertions for deck QA. Detects text-frame overflow, contrast violations (luminance ratio), alignment-grid drift, repeated-layout-hash, title-underline spam, dark/light run length, missing speaker notes, and duplicate titles. Emits a JSON report consumed by @deck-critic. Keywords: structural QA, contrast, overflow, alignment grid, layout hash, python-pptx assertions."
---

# PPTX Structural Asserts

Deterministic, fast, no-render-required structural QA. Loads the deck
via python-pptx and runs ten checks against shape geometry, text frames,
runs, and notes. Output is a JSON report consumed by `@deck-critic`.

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
  "blocking_findings": [],
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
