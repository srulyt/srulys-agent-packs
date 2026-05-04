---
name: slide-critique
description: "Negative-space catalog and checklist execution for slide-deck QA. Catalogs AI-generated slide antipatterns, defines the critique output format, and orchestrates execution through the @deck-critic visual-QA pipeline (render + structural-asserts + multimodal rubric). Keywords: critique, audit, review, design quality, visual QA, feedback loop, antipatterns."
---

# Slide Critique

> **Content placement** — This skill is the canonical home for the **negative-space catalog** (AI-generated slide antipatterns) and **checklist execution** (critique output format, verdict logic).
> The positive design rules ("what good looks like") live in `presentation-design`.
> The execution pipeline (render + structural assertions + per-slide multimodal rubric) lives in `pptx-visual-qa` and `pptx-structural-asserts` and is run by `@deck-critic`.

## Table of Contents

1. [When to Use This Skill](#when-to-use-this-skill)
2. [Core Principle](#core-principle)
3. [Execution Model — How Critique Actually Runs](#execution-model--how-critique-actually-runs)
4. [AI-Generated Slide Antipatterns](#ai-generated-slide-antipatterns)
5. [Critique Checklist](#critique-checklist)
6. [Critique Output Format](#critique-output-format)
7. [Verdict Logic](#verdict-logic)
8. [References](#references)

## When to Use This Skill

Load this skill when:

- You are `@deck-critic` and need the antipattern catalog + critique output format
- You are `@deck-builder` applying pre-flight checks before handoff
- You need to interpret a `qa-report.json` produced by the QA pipeline

## Core Principle

> Quality comes from iteration, not first-pass generation.

The first render is almost never correct. Treat critique as a **bug
hunt**, not a confirmation step. If you found zero issues on first
inspection, you weren't looking hard enough.

## Execution Model — How Critique Actually Runs

This skill is **not** a "mentally walk through the code" exercise. The
actual critique is executed by `@deck-critic` via three concrete tools:

1. **Headless render** — `pptx-visual-qa/scripts/render_pptx.py`
   converts `output.pptx → output.pdf → slide-{N}.png` via
   `soffice --headless` (LibreOffice). Each PNG is then viewed by the
   critic agent and graded against the per-slide rubric in
   `pptx-visual-qa/references/visual-rubric.md`.
2. **Structural assertions** — `pptx-structural-asserts/scripts/check_pptx.py`
   loads the deck via python-pptx and runs deterministic checks
   (overflow, contrast, alignment grid, layout-hash repeats, underline
   spam, dark/light run length, speaker-notes presence, duplicate titles).
3. **Antipattern sweep** — the `@deck-critic` agent applies the catalog
   below to the per-slide PNGs.

The verdict (`pass | revise`) and `top-fixes-json` are produced by
`@deck-critic` and consumed by `@story-orchestrator`. Builders fix on
retry.

## AI-Generated Slide Antipatterns

> **The catalog below is the canonical home for AI-slide antipatterns.**
> Do not duplicate this list in agent prompts or other skills.

### ❌ Antipattern 1: The Accent Line Under Every Title

Thin decorative lines under every headline are the #1 hallmark of
AI-generated decks. They add no information and create visual monotony.

**Detection**: `pptx-structural-asserts/check_pptx.py.title_underline_count > 2`
across the deck.

**Fix**: Use whitespace to separate title from content. Reserve accent
lines for 1–2 emphasis slides only — or eliminate entirely.

### ❌ Antipattern 2: Identical Layout Repetition

Every content slide uses the same headline-bullets-on-light-background
template. The deck feels like a document.

**Detection**: `repeated_layout_hash` flags any consecutive pair of
slides with matching shape-position + text-frame-count signature.

**Fix**: Vary layouts — split layouts (text+visual), big statement
slides (one phrase, massive font), data metric grids (2–3 large
numbers), full-bleed visual with text overlay, comparison columns.

**Rule**: No two consecutive slides share the same layout pattern.

### ❌ Antipattern 3: Text-Heavy Slides

More than 4 bullet points, or bullets exceeding 15 words.

**Detection**: `overflow_violations` or per-slide `text_density: high`.

**Fix**: Split into multiple slides. Replace text with a single bold
statement, a 60–72pt number, a comparison, or a tension question.

### ❌ Antipattern 4: Generic Color Palette

Default blue accent, white background. Could be any presentation about
any topic.

**Detection**: visual rubric — uniform palette across all slides with
no section-color signaling.

**Fix**: Choose colors informed by topic; use section-specific accent
colors to reinforce narrative structure (see `slide-design-systems` and
`presentation-design` Section Colors).

### ❌ Antipattern 5: Uniform Visual Weight

Every element competes for attention equally. No clear focal point.

**Detection**: visual rubric `focal_point_present: false`.

**Fix**: One element dominates (60% visual weight). Subordinate the rest
through size, color, or opacity.

### ❌ Antipattern 6: Decorative Over Functional Shapes

Shapes (circles, bars, stripes) that add no information — "making it
look designed."

**Detection**: visual rubric flags decorative-only elements; structural
hash often unchanged when removed.

**Fix**: Every non-text element must carry meaning — section identity,
progress indication, data emphasis. If it doesn't, remove it.

### ❌ Antipattern 7: Missing Narrative Rhythm

Flat sequence of equally-weighted slides. No peaks, no valleys.

**Detection**: `max_same_bg_run >= 3` or no Big-Statement / Question /
Section-Divider slides at narrative turning points.

**Fix**: Use section dividers as pacing devices. Alternate between
high-density evidence slides and low-density statement/question slides.
Insert "pause" slides before major transitions.

### ❌ Antipattern 8: Missing Speaker Notes

A deck without speaker notes is a half-built deliverable.

**Detection**: `speaker_notes_missing` non-empty.

**Fix**: Add 2–3 sentences per slide with concrete data points and a
transition cue.

### ❌ Antipattern 9: Duplicate Titles

Two slides with the same headline indicate either a layout dupe or
incomplete authoring.

**Detection**: `duplicate_titles` non-empty.

**Fix**: Differentiate by adding the slide's specific takeaway, or
merge slides if redundant.

### ❌ Antipattern 10: Low-Contrast Text

Text not readable against its background — common when accent colors
are used for body text on similar-luminance backgrounds.

**Detection**: `contrast_violations` (luminance ratio <4.5:1).

**Fix**: Adjust text color or background to meet 4.5:1 minimum (WCAG AA).

## Critique Checklist

Run these against every generated deck. Each item maps to a structural
or visual check.

### Layout Variety (CRITICAL)
- [ ] No two consecutive slides share the same layout pattern (`repeated_layout_hash` empty)
- [ ] At least 3 different layout types across the deck
- [ ] Big-statement / question slides at narrative turning points
- [ ] Split layouts used for at least one comparison or evidence slide

### Visual Composition
- [ ] Each slide has a clear focal point (visual rubric)
- [ ] Whitespace exceeds 30% on every content slide
- [ ] Elements aligned consistently (alignment grid)
- [ ] No overlapping text or elements
- [ ] Margins ≥0.75" from edges

### Text Compression
- [ ] No slide has more than 4 bullet points
- [ ] No bullet exceeds ~15 words
- [ ] Headlines 4–10 words, action statements
- [ ] At least 2 slides have NO body text

### Color & Contrast
- [ ] All body text passes 4.5:1 contrast ratio
- [ ] Dark/light slide ratio roughly 30/60/10
- [ ] No `max_same_bg_run >= 3`

### Storytelling Coherence
- [ ] Headlines alone tell a coherent story
- [ ] Emotional arc progresses (no two adjacent slides target the same emotion)
- [ ] Opening creates curiosity (no agenda openers)
- [ ] Closing has specific, concrete CTA

### AI Antipattern Sweep
- [ ] Title underlines on ≤2 slides
- [ ] No identical layouts on consecutive slides
- [ ] No generic Agenda/Overview slides
- [ ] No text-only slides without visual element
- [ ] Shapes serve function, not decoration
- [ ] Every slide has speaker notes
- [ ] No duplicate titles

## Critique Output Format

`@deck-critic` produces `qa-report.json` (schema:
`.story-telling-stm/schemas/qa-report.schema.json`) and, when verdict
is `revise`, a `top-fixes.json` with ≤5 ordered actionable fixes.
Both formats are normative — the orchestrator parses them.

The legacy markdown form is deprecated; only the JSON form is consumed.

## Verdict Logic

`pass` requires **all**:
- All structural checks pass.
- ≤2 non-blocking findings.
- No critical antipatterns (1, 2, 7, 8, 9, 10).
- ≥3 distinct layouts present.
- Headline sequence reads as a coherent story (see Slide-Sorter Test below).
- At least one fix-and-verify cycle has occurred this session OR the
  first-pass deck cleanly cleared every check.

Any failure → `revise` with ordered `top-fixes`. The orchestrator
applies retry policy (max `qa_iteration = 2` before user surfacing).

> **Numeric score does NOT auto-flip the verdict.** Per Q3 decision
> in session `2026-05-04-5707a9ef`, the boolean `pass` / `revise` /
> `error` remains the canonical gate. The 0–100 weighted score (next
> section) is a prioritization signal only.

## Slide-Sorter Test (Deck-Level)

> *Source: research §A lines 44–45 + `narrative-craft/SKILL.md`
> "Throughline" section. Promoted to a deterministic critic check in
> session `2026-05-04-5707a9ef`.*

The slide-sorter test reads slide titles in deck order, ignoring
section dividers, and asks one question: *"Does this parse as a
coherent executive summary of the proposal's throughline?"*

**Procedure** (deterministic):

1. Load `proposal.md`; extract `## Throughline` (one sentence).
2. Load `deck-spec.json`; extract `slides[].title` in order, skipping
   slides whose `type ∈ {section-divider, title}`.
3. Concatenate the titles into a paragraph.
4. Apply the Punch Test (`narrative-craft/references/headline-craft.md`)
   per title: every title that is a topic label (not a claim /
   question / stat) is a finding.
5. Apply the throughline test: does the paragraph's argument map
   onto the throughline's
   *current-state → tension → resolution → action*
   structure? If a beat is missing or out-of-order, that's a finding.
6. Record findings as antipattern `slide_sorter_failure` (per-title
   failure → `severity: warn`; whole-deck failure → `severity: fail`).

A whole-deck slide-sorter failure is a `revise` trigger. Per-title
failures rank in `top_fixes` ordered by their per-slide score (see
next section).

## Numeric Quality Score (0–100, prioritization-only)

> *Source: research §8 lines 367–376; ported in session
> `2026-05-04-5707a9ef`. Per Q3 decision the score is a
> **prioritization signal**, never a gate. Boolean `verdict` still
> wins.*

For each slide and for the deck as a whole, the critic emits a
weighted 0–100 score. Use it to:

- **Rank `top_fixes`** — the orchestrator surfaces fixes for the
  lowest-scoring non-appendix slides first, capped at 5.
- **Track convergence** — across `qa_iteration`s, deck-level score
  should rise. A flat or falling score across two iterations means
  the retries aren't converging; surface to the user.

### The Weighted Rubric

| Dimension | Max points | What it measures |
|---|---:|---|
| **Narrative clarity** | 20 | Slide carries one assertion that fits the throughline; AEI triad complete |
| **Assertion title quality** | 15 | Punch Test pass; ≤14 words; specific + quantified when possible |
| **Evidence strength** | 15 | Evidence type matches assertion's relationship; sourced; visual over textual |
| **Layout & hierarchy** | 20 | One focal point; visual hierarchy clear in 3s; layout doesn't repeat the prior slide |
| **Visual polish & brand consistency** | 15 | Design-system tokens applied consistently; no decorative-only shapes; whitespace ≥30% |
| **Chart / image quality** | 10 | Chart relationship → chart type per `pptx-engine/references/chart-selection.md`; image earned its place per `presentation-design/references/image-direction.md` |
| **Accessibility & technical correctness** | 5 | Contrast ≥4.5:1; alt text on meaningful images; speaker notes present; no overflow |
| **Total** | **100** | |

Deck-level `score` = average of non-appendix `per_slide_scores[].total`.

### Reference Targets (Diagnostic, Not Gates)

- **Deck score ≥90**: deck is healthy; surface as positive.
- **Deck score 80–89**: ship-able; recommend a follow-up polish pass.
- **Deck score <80**: investigate even if `verdict == pass` — likely
  one or two outlier slides dragging the average.
- **Per-slide score <85** *for non-appendix slides*: the slide is
  weakest in the deck and goes into `top_fixes` first.

These are **diagnostic targets**, not auto-revise triggers. A deck
with `verdict: pass` and `score: 78` ships if structural + visual
checks pass; the score is reported to the user in `qa-summary` so
they can decide whether to ask for another iteration.

### Recording the Score

The critic records the score under the `score` and `per_slide_scores`
fields of `qa-report.json` (schema v2.1.0, see
`.story-telling-stm/schemas/qa-report.schema.json`). When the score
is omitted (e.g. on `error` verdict or when the critic has not
implemented the rubric), absence is allowed and the orchestrator
falls back to verdict-only behaviour.

## References

- [AI Slide Antipatterns](references/ai-antipatterns.md) — Expanded
  catalog with concrete examples
- `pptx-visual-qa` — Render pipeline + per-slide visual rubric
- `pptx-structural-asserts` — Programmatic python-pptx checks
- `presentation-design` — Positive design rules (the "what good looks like" companion)
