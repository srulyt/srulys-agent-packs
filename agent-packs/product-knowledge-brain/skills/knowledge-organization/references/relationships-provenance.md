# Relationships & Provenance — Link Syntax

Overflow reference for `knowledge-organization/SKILL.md`. How to make
knowledge **networked, not isolated**, and how to keep every important
claim **traceable**.

## Typed relationships (first-class)

Relationships are first-class. Express them **two ways**, kept consistent:

1. **Structured** — in front-matter `relationships:`:
   ```yaml
   relationships:
     - rel: supports
       target: strategic/north-star-activation.md
     - rel: requested-by
       target: segments/enterprise.md
   ```
2. **Inline** — wiki-links in prose for human readers:
   ```markdown
   Activation work [[areas/feature-a/knowledge/onboarding-flow]] supports
   the [[strategic/north-star-activation]] goal.
   ```

### Relationship vocabulary

| `rel` | Meaning | Inverse (target's backlink) |
|---|---|---|
| `supports` | A advances B (e.g. feature → goal) | `supported-by` |
| `requested-by` | A was asked for by B (feature ← segment/persona) | `requests` |
| `blocks` | A blocks B | `blocked-by` |
| `relates-to` | general association | `relates-to` |
| `supersedes` | A replaces B (decisions/pages) | `superseded-by` |
| `affects` | A changes/impacts B | `affected-by` |
| `derived-from` | A is derived from B (claim ← research/evidence) | `informs` |
| `competes-with` | A competes with B (competitive) | `competes-with` |

## Backlinks (bidirectional consistency)

When you add an edge **A —rel→ B**, you MUST ensure **B** reflects the
inbound relationship in its `## Related` section (using the inverse from the
table). Backlinks let an agent landing on B discover what depends on it.
`knowledge-indexing` rebuilds backlinks into the discovery indexes, but the
page-level `## Related` is written here at step 6.

Example — on the goal page `strategic/north-star-activation.md`:
```markdown
## Related
- supported-by ← [[areas/feature-a/knowledge/onboarding-flow]]
- supported-by ← [[areas/feature-b/knowledge/quick-start]]
```

## Cross-domain chains

The design goal is traversable chains across product areas:
`Feature A → Persona X → Segment Y → Strategic Goal Z → Feature B`. Build
these out of the typed edges above rather than copying content between
pages. A reader can then walk the graph from any node.

## Provenance / evidence model

- **Granularity (default)**: **one `E-<nnn>` evidence descriptor per source
  document**; **per-claim inline citations** reference it.
- **Inline citation**: `[^E-031]` immediately after the claim it supports,
  with a matching footnote definition `[^E-031]: see evidence/E-031.md` and
  the id in the page front-matter `evidence:` list.
- **Descriptor** (`evidence/E-<nnn>.md`): records `source_type`, `date`, and
  a one-line summary — **never** the raw source content.
- **Traceability**: from any claim a future agent can reach the evidence
  descriptor and learn which source/meeting/decision introduced it.
- **Uncited claims**: are NOT asserted as fact — they go under the page's
  `## Open Questions / Uncertainties` until evidence exists.

## Consistency invariants

- Every front-matter `relationships:` edge has a matching inline `[[...]]`
  link somewhere in the page body (or vice versa) and a backlink on the
  target.
- Every id in `evidence:` resolves to an existing `evidence/E-<nnn>.md`.
- Every inline `[^E-nnn]` appears in the `evidence:` list and has a
  footnote definition.
