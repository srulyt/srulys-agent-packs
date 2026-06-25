# Per-Layer Discovery Heuristics (reference)

Overflow reference for `context-discovery/SKILL.md`. Concrete, language-agnostic
signals for each layer. Use file-glob + content-search; verify existence before
recording.

## code

- **Entry points**: route tables, controller/handler dirs, `main`/`cmd`/`bin`,
  CLI command registries, event/subscriber registration, public API surfaces.
- **Signals**: files importing seed modules; files defining the feature's
  primary types/services; directories named after the feature.
- **Globs**: `**/*.{py,js,ts,go,java,cs,rb,rs,php,kt,swift}` filtered by term
  match + import graph from the seed.

## data

- **Signals**: schema/migration dirs (`migrations/`, `schema/`, `*.sql`), ORM
  models, DTO/contract definitions, fixtures/seed files referencing the
  feature's entities.
- **Globs**: `**/migrations/**`, `**/*.sql`, `**/models/**`, `**/schema*/**`,
  `**/fixtures/**` filtered by entity/term match.

## tests

- **Signals**: test files importing seed symbols; tests named after the feature;
  fixtures/mocks/snapshots for the feature's types.
- **Globs**: `**/{test,tests,spec,__tests__}/**`, `**/*_test.*`, `**/*.spec.*`,
  `**/*.test.*` filtered by term/symbol match.

## docs

- **Signals**: READMEs in the feature's dirs; ADR/design-doc dirs; doc pages
  mentioning the feature name, its routes, or key symbols.
- **Globs**: `**/*.md`, `**/docs/**`, `**/adr/**`, `**/*.rst` filtered by term
  match.

## config

- **Signals**: env files, app config (`*.yaml/yml/toml/ini/json` config),
  feature-flag definitions, build/CI config, IaC (`*.tf`, `Dockerfile`,
  k8s manifests) referencing the feature's keys/flags.
- **Globs**: `**/{config,configs,.config}/**`, `**/*.env*`, `**/*.toml`,
  `**/*.ini`, `**/.github/workflows/**`, `**/*.tf` filtered by key/flag match.

## dependencies

- **Internal**: modules the seed imports that live elsewhere in the repo (follow
  the import graph one or two hops out).
- **External**: packages the seed imports, resolved against manifest files
  (`package.json`, `requirements.txt`/`pyproject.toml`, `go.mod`, `pom.xml`,
  `*.csproj`, `Gemfile`, `Cargo.toml`).
- **Record**: name + manifest path + why the feature needs it.

## General tips

- **Two-pass**: (1) import-graph expansion from the seed; (2) whole-repo term
  sweep for distinctive names (routes, tables, flags) to catch far-flung code.
- **Distinctive terms only**: sweep on names unlikely to collide (avoid generic
  words like `user` alone — combine with a feature qualifier).
- **Confidence**: seed/direct-import → 5; named reference → 4; corroborated term
  match → 3; weak match → 2; speculative → 1 (flag in Open Questions).
