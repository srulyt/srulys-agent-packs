# Content Areas — full derivation (reference)

Overflow reference for `context-pack-schema/SKILL.md`. Specifies what each of
the five mandated content areas must capture, how it is derived, and how legacy
12-section content condenses into it.

## 1. Feature entry points → `01-entry-points.md`

**Captures:** every place execution or interaction *enters* the feature.

- HTTP/RPC controllers and routes; GraphQL resolvers; CLI commands; scheduled
  jobs; event/message handlers; UI entry components; public library functions;
  "context roots" (the top-level module(s) a newcomer should open first).

**Derived from:** discovery (route/handler registration, command tables) +
analyzer notes (signatures, triggers). Legacy source: §3 Entry Points &
Triggers.

**Each entry:** name, path, trigger (what calls it), and a one-line purpose.

## 2. Important file & folder locations per layer → `02-file-locations.md`

**Captures:** the key paths a developer must know, grouped by **layer**:
`code`, `data`, `tests`, `docs`, `config`, `dependencies`.

**Derived from:** discovery inventories (all layers). Legacy source: §4 Code
Inventory + §6 Dependencies.

**Each entry:** path, layer, and what it holds / why it matters. Group by layer
with a short heading per layer; include a "none found" note for empty layers.

## 3. Glossary of terms → `03-glossary.md`

**Captures:** the domain and code vocabulary a newcomer must know — entities,
acronyms, status enums, internal jargon.

**Derived from:** analyzer notes over code + docs (type/enum names, comments,
README/docs prose). Legacy source: §7 Domain Concepts.

**Each entry:** term → concise definition + where it is defined/used.

## 4. Patterns & practices → `04-patterns-and-practices.md`

**Captures:** recurring conventions the agents *discovered* (not prescribed):
error-handling style, dependency injection, validation, logging, naming
conventions, testing approach, feature-flagging, etc.

**Derived from:** analyzer pattern detection across the inventory. Legacy
source: §8 Patterns & Practices.

**Each entry:** the pattern, where it recurs (representative paths), and the
"do likewise" guidance for changes.

## 5. Architecture & code design → `05-architecture-and-design.md`

**Captures:** how the pieces fit — module decomposition, public contracts /
interfaces, data flow, key invariants, and change-guidance ("if you change X,
also touch Y").

**Derived from:** synthesizer over analyzer notes (code-derived). Legacy
source: §2 Architecture + §5 Public Contracts + §11 Change Guidance.

**Each entry:** a short narrative + a component/flow list + explicit change
guidance.

## Header + Open Questions (not numbered areas)

- **Overview/Purpose header** (legacy §1): 2-4 sentences — what the feature is,
  who uses it, why the pack exists.
- **Open Questions** (legacy §12): unresolved ambiguities, thin-coverage layers,
  and conflicts the synthesizer could not resolve — each with a default
  assumption. Never omit a gap silently.

## Mapping summary

| 5-area file | Legacy 12-section | Primary deriver |
|---|---|---|
| `01-entry-points.md` | §3 | discovery + analyzer |
| `02-file-locations.md` | §4 + §6 | discovery (all layers) |
| `03-glossary.md` | §7 | analyzer |
| `04-patterns-and-practices.md` | §8 | analyzer |
| `05-architecture-and-design.md` | §2 + §5 + §11 | synthesizer (code-derived) |
