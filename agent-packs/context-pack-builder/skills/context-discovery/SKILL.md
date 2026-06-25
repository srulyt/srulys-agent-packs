---
name: context-discovery
description: "Multi-layer codebase discovery heuristics for context packs: how to find ALL related paths across code, data, tests, docs, config, and dependencies, breadth-first, from a feature seed. Keywords: discovery, find related code, layers, code map, search heuristics, context pack."
---

# Context Discovery

Per-layer search heuristics for finding **all** related paths for a feature
across the **whole** repo. Loaded by the discovery agent. Discovery is
**breadth-first** — catalog paths, do not deep-read contents (that is the
analyzer's job).

## When to Use This Skill

Load this skill when:
- Expanding a feature seed into a per-layer path inventory.
- Deciding which paths belong to a feature and at what confidence.

## The six layers (cover every one)

| Layer | What to find |
|-------|--------------|
| **code** | Source implementing the feature: modules, classes, functions, routes/handlers, services. |
| **data** | Schemas, migrations, models/ORM, fixtures, seed data, data contracts. |
| **tests** | Unit/integration/e2e tests, fixtures, mocks, snapshots targeting the feature. |
| **docs** | READMEs, ADRs, design docs, runbooks, inline doc pages mentioning the feature. |
| **config** | Env/config files, feature flags, build/CI config, IaC touching the feature. |
| **dependencies** | Internal modules the feature imports + external packages it relies on (manifests). |

Always produce an inventory file per layer, even if it records "none found"
(with a confidence note). Never silently skip a layer.

## Expansion strategy (seed → full inventory)

1. **Start from the seed paths** (and the feature name/description as search
   terms).
2. **Expand by reference** (breadth-first, repeat until no new paths):
   - **Imports / requires / includes** from seed files → more `code`.
   - **Route/command/event registration** tables → entry-point `code`.
   - **Type/model names** → `data` (schemas, migrations) + `tests`.
   - **Test files** referencing seed symbols → `tests`.
   - **Config keys / flag names** used in seed code → `config`.
   - **Package/manifest entries** for libraries the seed imports →
     `dependencies`.
   - **Doc mentions** of the feature name or its key symbols → `docs`.
3. **Whole-repo sweep**: search the entire tree for the feature's distinctive
   terms (names, route prefixes, table names) to catch related code far from the
   seed.
4. **Verify existence** of every path before recording — never fabricate.

## Confidence per path (1-5)

Tag each inventory entry with a discovery confidence:
- **5** seed path or directly imported by one;
- **4** referenced by name from a seed/4-5 path;
- **3** matched a whole-repo term search with corroboration;
- **2** weak/ambiguous term match;
- **1** speculative — include but flag in Open Questions.

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Deep-reading file bodies | That is analyzer work; slow + out of scope | Catalog paths + one-line "why related" only |
| Skipping a thin layer | Hides coverage gaps | Record "none found" + confidence, surface in Open Questions |
| Recording unverified paths | Fabricated inventory | Verify each path exists first |
| Stopping at the seed dir | Misses related code elsewhere | Whole-repo term sweep |

## References

- [layer-heuristics.md](references/layer-heuristics.md) — concrete per-layer
  search patterns and signals.
