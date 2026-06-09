# Knowledge Types — Taxonomy & Classification Rules

Overflow reference for `knowledge-consolidation/SKILL.md`. The six
first-class knowledge types the brain recognizes, with classification cues
and where each type lives on disk.

## The six types

### 1. Product
**Covers**: features, requirements, roadmaps, user stories, business rules,
acceptance criteria, release notes.
**Cues**: "the feature shall…", "the roadmap", "requirement", "user story".
**Lives**: `areas/<area>/knowledge/<concept>.md` (most product knowledge is
area-owned); roadmaps may be cross-cutting under `strategic/` if
theme-level.
**Front-matter `type:`** `product`.

### 2. Customer
**Covers**: personas, customer segments, customer requests, pain points,
jobs-to-be-done (JTBD).
**Cues**: "persona", "segment", "customers asked for", "pain point", "JTBD".
**Lives**: cross-cutting `personas/<slug>.md`, `segments/<slug>.md`; area
-specific feedback under `areas/<area>/customer-feedback/`.
**Front-matter `type:`** `customer`.

### 3. Competitive
**Covers**: competitors, market positioning, competitive gaps and
strengths, win/loss themes.
**Cues**: "competitor", "vs <name>", "market position", "they offer".
**Lives**: `competitive/<competitor-slug>.md`.
**Front-matter `type:`** `competitive`.

### 4. Organizational
**Covers**: decisions, decision rationale, historical context, team
conventions, ways of working.
**Cues**: "we decided", "the rationale was", "convention", "historically".
**Lives**: org-level decisions as `decisions/ADR-<nnn>-<slug>.md`; context
on the relevant concept page's `## Why / Rationale` and `## Change Log`.
**Front-matter `type:`** `organizational`.

### 5. Research
**Covers**: research findings, experiments, outcomes, learnings, usability
results, data analyses.
**Cues**: "we found", "the experiment showed", "study", "A/B test".
**Lives**: `areas/<area>/research/<slug>.md`; cross-cutting research may be
linked from the `research-index`.
**Front-matter `type:`** `research`.

### 6. Strategic
**Covers**: goals, vision, themes, initiatives, OKRs.
**Cues**: "our goal", "vision", "strategic theme", "initiative", "objective".
**Lives**: `strategic/<goal-slug>.md`.
**Front-matter `type:`** `strategic`.

## Multi-type claims

A single input frequently spans several types (e.g. "Segment Y asked for
Feature A to hit Strategic Goal Z"). Record **all** applicable types in
`classification.json` and create the typed **relationships** that connect
them (handled by `knowledge-organization` step 6). Do not force a
multi-type claim onto a single page — split it across the canonical pages
for each entity and link them.

## Classification ambiguity (residual risk)

When a claim could plausibly be two types, prefer the type of the **entity
it primarily describes** (a pain point is `customer` even if it motivates a
`product` feature; the feature link is a relationship, not a reclassification).
Record any genuinely ambiguous classification as an `open_questions` note so
filing stays consistent across runs.

## Entity extraction

For each claim, extract the named entities so step 3 can find their pages:
features, personas, segments, competitors, strategic goals, decisions,
research findings. Normalize to slugs (`kebab-case`) to match existing
page filenames and avoid near-duplicate pages.
