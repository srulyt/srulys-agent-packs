# Confidence Scoring Rubric (1-5) — reference

Overflow reference for `context-pack-schema/SKILL.md`. The 1-5 rubric carried
from the legacy context-packs pack. Applied per content area by the analyzer
and aggregated by the synthesizer.

## The scale

| Score | Meaning | Evidence basis |
|-------|---------|----------------|
| **5** | **Certain** | Directly read in code; multiple corroborating sources; no ambiguity. |
| **4** | **High** | Read in code with minor inference; single strong source. |
| **3** | **Moderate** | Partly inferred from naming/structure; some corroboration; plausible gaps. |
| **2** | **Low** | Mostly inferred; weak or indirect evidence; likely incomplete. |
| **1** | **Speculative** | Guessed from context; little/no direct evidence — flag in Open Questions. |
| **0 / none** | **No coverage** | The layer/area yielded nothing; record explicitly, do not omit. |

## How the analyzer assigns a score

1. Score each note by the strongest evidence backing it (code read > naming
   inference > doc mention).
2. Score the **area** as the evidence-weighted level of its notes, **capped** by
   coverage breadth: if a whole layer is missing for an area that needs it, the
   area cannot exceed 3.
3. Anything scored ≤ 2 MUST also appear in the area's notes as a caveat and, if
   ≤ 1, in the run's Open Questions.

## How the synthesizer aggregates

- Per area: take the analyzer's area score; if multiple analyzer batches scored
  the same area, use the **lower** of the median and the breadth-capped value
  (be conservative — a context pack must never over-claim).
- Record the final per-area score in `section_confidence` in
  `context-pack.json` and in the SKILL.md area heading (e.g.
  `## Entry Points (confidence: 4/5)`).

## Why confidence matters

"Find ALL related code" is inherently best-effort. Confidence scores +
Open Questions are how the pack stays **honest** about coverage instead of
silently asserting completeness. This is a hard requirement, not a nicety.
