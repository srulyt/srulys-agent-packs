---
name: slide-critique
description: "Self-critique and design audit for generated slide decks. Evaluates visual composition, layout variety, text density, design taste, and identifies common AI-generated slide antipatterns. Implements a generate→evaluate→improve feedback loop. Keywords: critique, audit, review, design quality, visual QA, feedback loop, antipatterns."
---

# Slide Critique

Expert knowledge for evaluating and improving generated slide decks through structured self-critique. This skill implements the critical feedback loop that separates mediocre AI-generated decks from professionally designed ones.

## When to Use This Skill

Load this skill when:
- Reviewing a generated deck before delivery
- Running the mandatory critique step after initial slide generation
- Identifying and fixing common AI-generated slide antipatterns
- Evaluating whether a deck feels "designed" or "generated"

## Core Principle

> Quality comes from iteration, not first-pass generation.

Your first render is almost never correct. Approach critique as a **bug hunt**, not a confirmation step. If you found zero issues on first inspection, you weren't looking hard enough.

## The Critique Loop

```
Generate deck → Critique (this skill) → Fix issues → Re-critique → Deliver
```

Minimum: **one full critique-and-fix cycle** before delivery. Never deliver a first-pass deck.

## Three-Dimensional Evaluation

Evaluate every deck across three dimensions (inspired by PPTEval):

### 1. Content Quality
- Does each slide communicate exactly ONE message?
- Are headlines action-oriented statements, not topic labels?
- Is text aggressively compressed — no bullet exceeds 15 words?
- Do speaker notes exist for every slide?
- Does the headline sequence tell a coherent story when read alone?

### 2. Design Quality
- Is there layout variety — no two consecutive slides use the same layout pattern?
- Does visual hierarchy work — can you identify the key message in 3 seconds?
- Is there adequate whitespace — at least 30% of each slide is breathing room?
- Are accent elements purposeful, not decorative?
- Is the dark/light rhythm working — no 3+ consecutive same-background slides?

### 3. Coherence
- Does the emotional arc progress (curiosity → concern → hope → confidence → action)?
- Do transitions between slides feel natural?
- Is the visual system consistent — same fonts, sizes, and colors throughout?
- Does every slide earn its place — would cutting it break the story?

## AI-Generated Slide Antipatterns

These are telltale signs of AI-generated slides. **Check for and eliminate every one:**

### ❌ Antipattern 1: The Accent Line Under Every Title
Thin decorative lines under every headline are the #1 hallmark of AI-generated decks. They add no information and create visual monotony.

**Fix**: Use whitespace to separate title from content. Reserve accent lines for 1-2 emphasis slides only — or eliminate them entirely.

### ❌ Antipattern 2: Identical Layout Repetition
Every content slide uses the same headline-bullets-on-light-background template. The deck feels like a document.

**Fix**: Vary layouts across slides:
- Split layouts (text left, visual right)
- Big statement slides (one phrase, massive font, centered)
- Data metric grids (2-3 large numbers with labels)
- Full-bleed visual with text overlay
- Comparison columns

**Rule**: No two consecutive slides should use the same layout pattern.

### ❌ Antipattern 3: Text-Heavy Slides
More than 4 bullet points, or bullets exceeding 15 words. The audience reads ahead and ignores the presenter.

**Fix**: Split into multiple slides. Replace text with:
- A single bold statement
- A number or statistic at 60-72pt
- A comparison or contrast layout
- A question that creates tension

### ❌ Antipattern 4: Generic Color Palette
Default blue accent, white background. Could be any presentation about any topic.

**Fix**: Choose colors informed by the topic. Use section-specific accent colors to reinforce narrative structure.

### ❌ Antipattern 5: Uniform Visual Weight
Every element on the slide competes for attention equally. No clear focal point.

**Fix**: One element dominates (60% visual weight). Supporting elements are visually subordinate through size, color, or opacity.

### ❌ Antipattern 6: Decorative Over Functional Shapes
Shapes (circles, bars, stripes) that add no information — they're just "making it look designed."

**Fix**: Every non-text element must carry meaning:
- A colored stripe can signal section identity (using section colors)
- A progress indicator shows deck position
- A shape frames a data callout

If a shape doesn't serve content, remove it.

### ❌ Antipattern 7: Missing Narrative Rhythm
The deck is a flat sequence of equally-weighted slides. No peaks, no valleys, no breathing room.

**Fix**: Use section dividers as pacing devices. Alternate between high-density evidence slides and low-density statement/question slides. Insert "pause" slides (big statements, questions) before major transitions.

## Critique Checklist

Run this checklist against every generated deck. Each item must pass.

### Layout Variety (CRITICAL)
- [ ] No two consecutive slides share the same layout pattern
- [ ] At least 3 different layout types are used across the deck
- [ ] Big statement or question slides appear at narrative turning points
- [ ] Split layouts are used for at least one comparison or evidence slide
- [ ] Data/metric slides use large standalone numbers, not charts

### Visual Composition
- [ ] Each slide has a clear focal point — one element dominates visually
- [ ] Whitespace exceeds 30% on every content slide
- [ ] Elements are aligned consistently (left edges, baselines, centers)
- [ ] No overlapping text or elements
- [ ] Margins are consistent (minimum 0.75" from edges)

### Text Compression
- [ ] No slide has more than 4 bullet points
- [ ] No bullet exceeds ~15 words
- [ ] Headlines are 4-10 words — action statements, not labels
- [ ] At least 2 slides in the deck have NO body text (headline only)
- [ ] Body text left-aligned (never center-align paragraphs)

### Color & Contrast
- [ ] Text is easily readable against its background
- [ ] Dark/light slide ratio follows roughly 30/60/10 (dark/light/accent)
- [ ] Section colors reinforce narrative structure
- [ ] No slide is entirely monochrome (at least one accent element)

### Storytelling Coherence
- [ ] Reading only the headlines tells a coherent story
- [ ] The emotional arc progresses — no two adjacent slides target the same emotion
- [ ] The opening hook creates curiosity (no agenda slides)
- [ ] The closing has a specific, concrete call to action

### AI Antipattern Sweep
- [ ] No decorative accent lines under every title (0-2 slides max)
- [ ] No 3+ consecutive slides with identical layout
- [ ] No generic "Agenda" or "Overview" slides
- [ ] No text-only slides without any visual element
- [ ] Shapes and accents serve function, not decoration

## Critique Output Format

When running a critique, produce this structured report:

```markdown
## Slide Deck Critique Report

### Overall Assessment
**Content**: {score: Strong/Adequate/Weak} — {one-line summary}
**Design**: {score: Strong/Adequate/Weak} — {one-line summary}
**Coherence**: {score: Strong/Adequate/Weak} — {one-line summary}

### Critical Issues (must fix)
1. **Slide {N}**: {issue description} → **Fix**: {specific fix}
2. ...

### Design Improvements (should fix)
1. **Slide {N}**: {issue description} → **Fix**: {specific fix}
2. ...

### Layout Variety Assessment
Current layout sequence: {e.g., "bullets → bullets → bullets → data → bullets"}
Recommended: {e.g., "statement → split → data → big-statement → bullets → comparison"}

### AI Antipattern Findings
- {antipattern found} → {fix}
- ...

### Verdict
{PASS — ready for delivery | REVISE — fix critical issues and re-critique}
```

## When Critique Passes

A deck passes critique when:
1. Zero critical issues remain
2. Layout variety score is 3+ distinct patterns
3. No AI antipatterns detected
4. Headline sequence reads as a coherent story
5. At least one fix-and-verify cycle completed

## References

- [AI Slide Antipatterns](references/ai-antipatterns.md) — Expanded catalog of AI-generated slide patterns to avoid
