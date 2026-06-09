# Repo Layout — Product-Centric Knowledge Base

Overflow reference for `knowledge-organization/SKILL.md`. The on-disk
layout of the knowledge base. Knowledge is organized around **product
areas**, not a personal second brain. Knowledge lives close to the
feature/team/domain that owns it; cross-cutting concepts live at the root
and are linked from area pages.

## Full tree

```
<kb-root>/                            # default knowledge-base/, caller-overridable
├── README.md                         # what this brain is; how to read it
├── index.md                          # repo-wide master index (entry point)
├── indexes/                          # discovery indexes (routing layer)
│   ├── product-index.md
│   ├── customer-index.md
│   ├── competitive-index.md
│   ├── research-index.md
│   ├── strategic-index.md
│   └── team-index.md
├── personas/                         # cross-cutting concept pages
│   └── <persona-slug>.md
├── segments/
│   └── <segment-slug>.md
├── strategic/                        # goals, vision, themes, initiatives
│   └── <goal-slug>.md
├── competitive/
│   └── <competitor-slug>.md
├── decisions/                        # org decision records (ADR-style)
│   └── ADR-<nnn>-<slug>.md
├── evidence/                         # evidence descriptors (NOT raw sources)
│   └── E-<nnn>.md
├── areas/                            # product areas own their knowledge
│   └── <area-slug>/                  # e.g. feature-a, platform
│       ├── area-index.md             # area's own routing index
│       ├── specifications/
│       ├── research/
│       ├── customer-feedback/
│       ├── designs/
│       └── knowledge/                # curated concept pages
│           └── <concept-slug>.md
└── _skills/                          # generated dynamic index skills
    └── <area-or-domain>-knowledge-index/SKILL.md
```

## Scaffolding rules

- **Baseline** (first cycle, or `<kb-root>/` missing): create `README.md`,
  `index.md`, `indexes/` (with the six discovery indexes as stubs),
  `evidence/`, and `areas/`. Do not pre-create empty area dirs.
- **New area**: when a claim belongs to a product area with no directory,
  create `areas/<area-slug>/` with `area-index.md` and the five sub-dirs
  (`specifications`, `research`, `customer-feedback`, `designs`,
  `knowledge`). Add the area to the repo-wide `index.md`.
- **Placement decision**:
  - Area-specific concept → `areas/<area>/knowledge/<slug>.md`.
  - Specs / research / feedback / designs tied to an area → the matching
    area sub-dir.
  - Cross-cutting concept (persona, segment, strategic goal, competitor) →
    the matching root dir, linked from each area that references it.
  - Org-level decision → `decisions/ADR-<nnn>-<slug>.md`.
  - Evidence descriptor → `evidence/E-<nnn>.md`.

## Naming conventions

- Slugs are `kebab-case`, lowercase, derived from the canonical entity name
  — match existing filenames to avoid near-duplicate pages.
- ADRs: `ADR-<nnn>-<slug>.md`, `<nnn>` zero-padded sequential.
- Evidence: `E-<nnn>.md`, `<nnn>` zero-padded sequential, one per source
  document.

## Why product-centric (not a giant wiki)

A centralized wiki forces every reader to load the whole repo. Area-owned
knowledge plus discovery indexes lets a future agent load only the area(s)
it needs — which is why `_skills/` dynamic index skills exist (see
`knowledge-indexing`). Cross-area knowledge is captured as **relationships**
between area pages and root concept pages, not by duplicating content.
