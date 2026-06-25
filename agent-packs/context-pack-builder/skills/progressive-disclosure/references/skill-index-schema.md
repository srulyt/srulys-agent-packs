# Uniform SKILL.md Index Schema (reference)

Overflow reference for `progressive-disclosure/SKILL.md`. The **uniform** layout
of a generated context pack's `SKILL.md` in both forms. All packs look alike.

## Form A — FULL (under threshold)

The `SKILL.md` body carries all five areas inline:

```markdown
---
name: <slug>-context
description: "Context pack for the <feature name> feature: entry points, per-layer file locations, glossary, patterns & practices, and architecture/design. Load when working on <feature name>. Keywords: <feature>, <terms>, context pack, where is, code map."
user-invocable: true
---

# <Feature Name> — Context Pack

## Overview
<2-4 sentences: what the feature is, who uses it, why this pack exists.>

## Entry Points (confidence: N/5)
<area 1 content>

## File & Folder Locations (confidence: N/5)
<area 2 content, grouped by layer>

## Glossary (confidence: N/5)
<area 3 content>

## Patterns & Practices (confidence: N/5)
<area 4 content>

## Architecture & Design (confidence: N/5)
<area 5 content>

## Open Questions
<gaps, ambiguities, conflicts — each with a default assumption>

## Change Log    <!-- present after the first UPDATE -->
<dated entries: what changed + why>
```

## Form B — INDEX (split; body MUST stay under threshold)

The five areas move into `references/01..05`; `SKILL.md` becomes a lean index
with a routing table:

```markdown
---
name: <slug>-context
description: "Context pack for the <feature name> feature: ... Keywords: ..."
user-invocable: true
---

# <Feature Name> — Context Pack (index)

## Overview
<2-4 sentences.>

## Where to look / why it matters

| Area | Confidence | Load this file when you need… |
|------|-----------|-------------------------------|
| Entry points | N/5 | how execution/interaction enters the feature → [01-entry-points](references/01-entry-points.md) |
| File locations | N/5 | the key paths per layer → [02-file-locations](references/02-file-locations.md) |
| Glossary | N/5 | domain/code terms → [03-glossary](references/03-glossary.md) |
| Patterns & practices | N/5 | the conventions to follow → [04-patterns-and-practices](references/04-patterns-and-practices.md) |
| Architecture & design | N/5 | how it fits + change guidance → [05-architecture-and-design](references/05-architecture-and-design.md) |

## Open Questions
<gaps, ambiguities, conflicts.>

## Change Log    <!-- present after the first UPDATE -->
<dated entries.>
```

## Fixed reference filenames (uniform across ALL packs)

```
references/01-entry-points.md
references/02-file-locations.md
references/03-glossary.md
references/04-patterns-and-practices.md
references/05-architecture-and-design.md
```

Each reference file starts with an `# <Area> (confidence: N/5)` H1 and contains
that area's full content (the same content that was inline in Form A).

## Rules

- The **index body** (Form B, frontmatter excluded) MUST be under the threshold
  in `split-threshold.md`. Keep it to the Overview + routing table + Open
  Questions (+ Change Log).
- Human-authored blocks marked `<!-- human -->` are carried verbatim into
  whichever form is produced — never dropped on split/uncross.
- On **uncross** (a previously-split pack now fits), inline the references back
  into Form A and record the removed `references/*.md` for the install script's
  uninstall-on-change pass.
