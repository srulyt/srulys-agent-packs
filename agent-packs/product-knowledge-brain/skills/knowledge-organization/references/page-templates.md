# Page Templates — Living Articles per Knowledge Type

Overflow reference for `knowledge-organization/SKILL.md`. Every page is a
**curated living article** — current understanding, not a transcript. All
types share the same skeleton; the front-matter `type:` and the emphasis of
each section differ.

## Shared front-matter schema

```yaml
---
title: "<Concept title>"
type: product | customer | competitive | organizational | research | strategic
area: <area-slug | cross-cutting>
status: current | uncertain | superseded
updated: <YYYY-MM-DD>
relationships:
  - rel: supports            # typed edge (see relationships-provenance.md)
    target: strategic/<goal-slug>.md
  - rel: requested-by
    target: segments/<segment-slug>.md
evidence: [E-012, E-031]     # evidence descriptor ids (front-matter list)
---
```

`status` rules: `current` (believed fact), `uncertain` (contested — claim
lives under Open Questions), `superseded` (retired; keep content + pointer).

## Shared body skeleton

```markdown
# <Concept title>

## Current Understanding
<curated claims — what we believe NOW. Each important claim cites evidence
inline, e.g.> The activation rate target is 40% [^E-012].

## Why / Rationale
<why we believe it; the reasoning and the decisions behind it.>

## Open Questions / Uncertainties
<uncited, contested, or unresolved claims live HERE — never asserted as
fact in Current Understanding.>

## Related
<backlinks (inbound) + outbound links>
- supports → [[strategic/<goal-slug>]]
- requested-by ← [[segments/<segment-slug>]]

## Change Log
<ADR-style, newest first; preserves superseded beliefs>
- <YYYY-MM-DD> — changed <X>; superseded "<old belief>"; reason; [^E-031]

[^E-012]: see evidence/E-012.md
[^E-031]: see evidence/E-031.md
```

## Per-type emphasis

| `type` | Current Understanding emphasizes | Typical relationships |
|---|---|---|
| product | what the feature/requirement is, scope, status | `supports` (goal), `requested-by` (segment), `relates-to` (feature) |
| customer | who they are, pains, JTBD | `requested-by` → feature, `relates-to` → segment |
| competitive | positioning, gaps/strengths | `competes-with`, `affects` (strategy) |
| organizational | the decision + rationale | `affects` (pages), `supersedes` (ADR) |
| research | finding, method, outcome, confidence | `derived-from` (evidence), `supports` (claim) |
| strategic | goal/vision/theme + success measure | `supports` ← features, `relates-to` ← initiatives |

## Evidence descriptor template (`evidence/E-<nnn>.md`)

One descriptor **per source document**; per-claim inline citations point at
it. Stores a *descriptor*, **not** the raw source.

```markdown
---
id: E-031
source_type: interview | prd | research-report | exec-discussion | email | roadmap | release-notes | design-review | strategy-doc
date: <YYYY-MM-DD>
---

# E-031 — <one-line source title>

One-line summary of what this source establishes and which claims it
supports. Do NOT paste the raw transcript/document here — that stays with
upstream extraction tools.
```

## Quality bar (a page is "living", not "notes")

- [ ] Reads as a curated article answering believe / why / evidence /
      uncertain — **not** a chronological dump or pasted transcript.
- [ ] Every important claim in `## Current Understanding` cites an
      `[^E-nnn]`; uncited claims are in `## Open Questions`.
- [ ] `relationships:` + at least one `[[...]]` link connect it to the
      network; `## Related` shows backlinks.
- [ ] `## Change Log` preserves any superseded belief with rationale +
      evidence.
