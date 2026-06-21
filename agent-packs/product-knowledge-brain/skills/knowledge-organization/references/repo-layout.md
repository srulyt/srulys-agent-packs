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
└── _skills/                            # generated index skills (stay in the KB; portable)
    ├── knowledge-index/SKILL.md             # top-level/root router (on request / repo-wide refresh; bare name; user-invocable: true)
    ├── <area-or-domain>-knowledge-index/SKILL.md  # per-area/per-domain (T2/T3; bare name; user-invocable: false)
    ├── install-skills.sh                # namespaces+installs THIS KB's skills into the harness dir, self-cleans (user runs)
    ├── install-skills.ps1               # PowerShell equivalent
    ├── removed-skills.json              # manifest of obsoleted skills (bare names; script maps to <kb-ns>-* and deletes)
    └── installed-skills.json            # install receipt (written by the script when the user runs it; drives uninstall-on-change)
```

Source dir names under `_skills/` are **bare** (`knowledge-index`,
`<slug>-knowledge-index`). The per-KB namespace
`<kb-ns> = slugify(basename(kb_root))` is applied **by the install script** when
it copies each dir into the shared harness skills dir (renaming to
`<kb-ns>-<bare-name>`), so two KBs in one workspace never collide there. The
**agent generates** the bare skills + scripts + `removed-skills.json` under
`_skills/`; the **user runs** the install script, which namespaces on copy,
writes `installed-skills.json`, and removes this KB's stale skills. See
`knowledge-indexing/references/harness-skills-dir.md` and
`removed-skills-manifest.md`.

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
