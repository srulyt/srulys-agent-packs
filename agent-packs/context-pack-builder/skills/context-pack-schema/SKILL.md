---
name: context-pack-schema
description: "Schema for codebase context packs: the 5 mandated content areas (with the legacy 12-section map), the confidence-scoring rubric, generated SKILL.md frontmatter, and the context-pack.json provenance schema. Keywords: context pack, content areas, confidence score, context-pack.json, schema."
---

# Context Pack Schema

The single source of truth for **what a context pack contains** and **how it is
structured**. Loaded by the analyzer, synthesizer, writer, indexer (and the
orchestrator for routing only).

## When to Use This Skill

Load this skill when:
- Extracting per-area notes (analyzer) or merging them (synthesizer).
- Materialising the generated `SKILL.md` / `context-pack.json` (writer).
- Mapping content areas to `references/01..05` (indexer).

## The five content areas (required)

Every context pack maps exactly these five areas. The `references/` filenames
are fixed so all packs are uniform.

| # | Content area | `references/` file | What it captures |
|---|---|---|---|
| 1 | **Feature entry points** | `01-entry-points.md` | Controllers, APIs, events, CLI commands, context roots — where execution/interaction enters the feature. |
| 2 | **Important file & folder locations per layer** | `02-file-locations.md` | The key paths per layer (code, data, tests, docs, config, dependencies) and what each holds. |
| 3 | **Glossary of terms** | `03-glossary.md` | Domain + code terms a newcomer must know, derived from code/docs. |
| 4 | **Patterns & practices** | `04-patterns-and-practices.md` | Recurring conventions the agents discovered (error handling, DI, naming, testing style). |
| 5 | **Architecture & code design** | `05-architecture-and-design.md` | How the pieces fit: modules, contracts/public interfaces, data flow, change-guidance. |

`SKILL.md` also carries: an **Overview/Purpose** header, per-area **confidence
scores** (1-5), and an **Open Questions** block. In the split (index) form it
adds a "Where to look / why it matters" routing table — see
`progressive-disclosure/references/skill-index-schema.md`.

## Legacy 12-section → 5-area map

The areas condense the legacy 12-section structure
(`agent-packs/context-packs/` Roo pack, `docs/context-packs.md`):

| 5-area | Legacy 12-section source |
|---|---|
| 1 Entry points | §3 Entry Points & Triggers |
| 2 File locations | §4 Code Inventory + §6 Dependencies |
| 3 Glossary | §7 Domain Concepts |
| 4 Patterns & practices | §8 Patterns & Practices |
| 5 Architecture & design | §2 Architecture + §5 Public Contracts + §11 Change Guidance |

Legacy §1 (Overview) → the SKILL.md header; legacy §12 (Open Questions) → the
Open Questions block. Confidence scoring (1-5) is preserved — see
[references/confidence-scoring.md](references/confidence-scoring.md).

For the full area derivation, see
[references/content-areas.md](references/content-areas.md).

## Generated `SKILL.md` frontmatter

The generated pack's `SKILL.md` uses ONLY these supported keys; `description` is
**double-quoted** and keyword-rich so the harness auto-loads the pack:

```yaml
---
name: <feature-slug>-context
description: "Context pack for the <feature name> feature: entry points, per-layer file locations, glossary, patterns & practices, and architecture/design. Load when working on <feature name>. Keywords: <feature>, <area terms>, context pack, where is, code map."
user-invocable: true
---
```

## `context-pack.json` (provenance + idempotency key)

```json
{
  "schema_version": "1.0",
  "feature_slug": "<feature-slug>",
  "feature_name": "<human name>",
  "description": "<seed description>",
  "seed_paths": ["<path>", "..."],
  "source_repo": "<code-repo identity/path>",
  "layers_covered": ["code","data","tests","docs","config","dependencies"],
  "content_hashes": { "01-entry-points": "sha256:...", "...": "..." },
  "section_confidence": { "entry-points": 4, "file-locations": 5, "glossary": 3,
                          "patterns-practices": 3, "architecture-design": 4 },
  "generated_at": "<ISO-8601>",
  "updated_at": "<ISO-8601>"
}
```

`content_hashes` is the idempotency key: a re-run whose recomputed hashes match
is a no-op (writer + indexer short-circuit). `seed_paths` is read on UPDATE to
re-seed discovery.

## Best Practices

1. **Never assert without confidence** — every area carries a 1-5 score.
2. **Surface gaps, never drop them** — thin coverage → Open Questions, not
   silent omission.
3. **Uniform filenames** — `01-entry-points.md` … `05-architecture-and-design.md`
   exactly, so all packs look alike.
4. **Quote the `description`** — bare strings with `:` break the YAML loader.

## Quality Checklist

- [ ] All five areas present (with "none found" + confidence if empty).
- [ ] Per-area confidence (1-5) recorded.
- [ ] Open Questions block present.
- [ ] `context-pack.json` carries `content_hashes` + `section_confidence`.
- [ ] Generated `SKILL.md` frontmatter uses only `name`, `description`
      (double-quoted), `user-invocable`.

## References

- [content-areas.md](references/content-areas.md) — full 5-area derivation +
  legacy map.
- [confidence-scoring.md](references/confidence-scoring.md) — the 1-5 rubric.
