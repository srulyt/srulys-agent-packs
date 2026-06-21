# Index Schema — Discovery & Area Indexes

Overflow reference for `knowledge-indexing/SKILL.md`. Indexes are a
**routing layer**: each entry tells a future agent *what exists, where, and
why it matters* — a path plus a one-line rationale, never a content dump.

## Repo-wide master index — `<kb-root>/index.md`

The entry point. Lists product areas and top-level cross-cutting concepts.

```markdown
# Knowledge Brain — Master Index

Last updated: <YYYY-MM-DD>

## Product Areas
- [feature-a](areas/feature-a/area-index.md) — onboarding & activation surface.
- [platform](areas/platform/area-index.md) — shared infra & auth.

## Discovery Indexes
- [Product](indexes/product-index.md) · [Customer](indexes/customer-index.md)
  · [Competitive](indexes/competitive-index.md) · [Research](indexes/research-index.md)
  · [Strategic](indexes/strategic-index.md) · [Team](indexes/team-index.md)

## Cross-cutting
- Personas: [enterprise-admin](personas/enterprise-admin.md)
- Strategic goals: [north-star-activation](strategic/north-star-activation.md)
```

## Top-level index SKILL — `<kb-root>/_skills/knowledge-index/SKILL.md`

A **Step-7 index artifact**: the **installable, auto-discoverable twin of
`index.md`**. Generate or refresh it when the caller requests a top-level /
repo-wide index skill, or during a full repo-wide index refresh; when you do,
keep it in sync with `index.md` so the two do not drift. It renders the same
repo-wide routing layer as a keyword-discoverable skill so a future agent can
find the knowledge base without scanning the repo. It is **not** a Step-8
"dynamic"/"refactor" output.

- Bare name `knowledge-index` (the install script adds the `<kb-ns>-` prefix
  on copy — see `harness-skills-dir.md`); `name` == `_skills/` dir name.
- `user-invocable: true`; a **double-quoted**, keyword-rich `description`.
- Body is a routing layer (path + why-it-matters) over the area indexes, the
  discovery indexes, and the key root concepts — mirroring `index.md`.

Full frontmatter + body template: see the **top-level / root index skill
template** in [`dynamic-index-skills.md`](dynamic-index-skills.md).

## Discovery index — `<kb-root>/indexes/<domain>-index.md`

One per knowledge domain (product, customer, competitive, research,
strategic, team). Each lists the relevant pages with a why-it-matters line.

```markdown
# Product Index

Last updated: <YYYY-MM-DD>

| Page | Area | Why it matters |
|---|---|---|
| [onboarding-flow](../areas/feature-a/knowledge/onboarding-flow.md) | feature-a | Defines activation funnel; drives the north-star metric. |
| [quick-start](../areas/feature-b/knowledge/quick-start.md) | feature-b | Self-serve entry path; top requested by SMB segment. |
```

## Area index — `<kb-root>/areas/<area>/area-index.md`

The area's own routing layer.

```markdown
# Feature A — Area Index

Last updated: <YYYY-MM-DD>

## Knowledge
- [onboarding-flow](knowledge/onboarding-flow.md) — current activation design + rationale.

## Specifications / Research / Customer Feedback / Designs
- research: [activation-study-q2](research/activation-study-q2.md) — 1-step beats 3-step.
```

## Update rules (step 7)

For each created/updated page in the cycle:
1. Ensure it appears in its **area-index.md** under the right sub-section.
2. Ensure it appears in the **discovery index** matching its
   front-matter `type:`.
3. Ensure the **area** appears in the repo-wide `index.md` (add if new).
4. **When (re)generating the top-level index SKILL
   `_skills/knowledge-index/SKILL.md`** (on caller request or a repo-wide index
   refresh), keep it in sync with `index.md` (it is `index.md`'s installable
   twin).
5. Update each touched index's `Last updated:` date.
6. Entries carry the **path + one-line why-it-matters**, derived from the
   page's `## Current Understanding` — never copy the page body.

## Backlink reflection

When relationships were added (step 6), discovery indexes may surface the
strongest cross-area links (e.g. which features support a strategic goal).
Keep these as links, not duplicated prose.

## Staleness invariant

After a cycle, no changed page may be absent from `index.md`, its
`area-index.md`, and its type's discovery index. When the top-level index SKILL
`_skills/knowledge-index/SKILL.md` is present, it must reflect the current
`index.md` (its twin). A stale index — or a top-level skill out of sync with
`index.md` — is a failure mode (index drift).
