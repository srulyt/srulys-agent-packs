# Removed-Skills Manifest + Install Receipt (reference)

Overflow reference for `knowledge-indexing/SKILL.md` **step 8a**. Specifies two
JSON files under `<kb-root>/_skills/`:

- **`removed-skills.json`** — the agent-maintained manifest of obsoleted/renamed
  index skills (by **bare** name), so the install script can delete **stale**
  harness skills on the next install — scoped to **this KB only**.
- **`installed-skills.json`** — the install **receipt** written by the install
  script (when the user runs it) recording what it installed, so a later run can
  diff and **uninstall-on-change**.

## On-disk location

Both live at `<kb-root>/_skills/` — they travel with the portable KB and are
consumed by the install script in the same dir. The agent (re)writes
`removed-skills.json` as part of step 8; the **install script** writes
`installed-skills.json` when the user runs it. Neither lives outside
`<kb-root>/`.

## `removed-skills.json` schema (JSON)

Removed names are **bare** (the source `_skills/` dir name, NOT namespaced). The
install script maps each bare name to `<kb-ns>-<name>` before deleting it from
the harness dir.

```json
{
  "kb_namespace": "knowledge-base",
  "removed": [
    { "name": "feature-x-knowledge-index",
      "removed_at": "2026-06-10T21:30:00Z",
      "reason": "renamed -> feature-a-knowledge-index" },
    { "name": "legacy-domain-knowledge-index",
      "removed_at": "2026-06-09T10:00:00Z",
      "reason": "domain merged into product-index" }
  ]
}
```

- `kb_namespace` (required) — this KB's namespace (`slugify(basename(kb_root))`,
  from `state.json.kb_namespace`). The install script uses it to map each bare
  removed `name` to the namespaced harness dir (`<kb-ns>-<name>`) and to prove
  every deletion belongs to this KB.
- `removed[]` — append-only list of obsoleted/renamed index-skill **bare names**
  (each equals its former `_skills/<name>/` directory), each with a
  `removed_at` ISO-8601 timestamp and a one-line `reason`.
- The manifest **always exists** once a cycle has generated any index skill,
  even if `removed` is `[]` (so the install script always has a manifest to
  read).

## `installed-skills.json` schema (JSON) — the install receipt

Written **by the install script** (not the agent) on every run, recording the
current truth of what is installed in the harness dir for THIS KB.

```json
{
  "kb_namespace": "knowledge-base",
  "harness_dir": "/abs/path/to/.github/skills",
  "installed_at": "2026-06-11T07:30:00Z",
  "installed": [
    { "source_bare_name": "knowledge-index",
      "installed_name": "knowledge-base-knowledge-index",
      "hash": "<sha256-or-mtime>" },
    { "source_bare_name": "feature-a-knowledge-index",
      "installed_name": "knowledge-base-feature-a-knowledge-index",
      "hash": "<sha256-or-mtime>" }
  ]
}
```

- `kb_namespace` (required) — this KB's namespace (every `installed_name` is
  `<kb_namespace>-<source_bare_name>`).
- `harness_dir` (required) — the absolute resolved harness skills dir the script
  installed into.
- `installed_at` — ISO-8601 timestamp of the last run.
- `installed[]` — one entry per installed skill: the `source_bare_name` (the
  bare `_skills/` dir), the `installed_name` (the namespaced harness dir), and a
  content `hash` (or mtime).

### Uninstall-on-change (receipt diff)

On each run the script loads the **previous** `installed-skills.json`, then:

1. installs the current bare `_skills/` dirs (namespacing each on copy);
2. for every entry in the **previous** receipt whose `source_bare_name` is **no
   longer present** in `_skills/` (deleted or renamed away), deletes
   `<harness_dir>/<installed_name>/` — **only if** `installed_name` starts with
   `<kb_namespace>-` (namespace-scoped);
3. also consumes `removed-skills.json` (mapping each bare `removed[].name` to
   `<kb-ns>-<name>`) and deletes those;
4. rewrites `installed-skills.json` to the new truth.

This makes the harness dir converge to exactly THIS KB's current bare skill set
(namespaced), self-cleaning renames/obsoletions, and **never** touching another
KB's installed skills.

## How the evolution cycle appends `removed-skills.json` (step 8a)

When generation would emit a skill whose **bare name differs** from a
previously-generated one for the same area/domain (a **rename**), or a
previously-generated skill's trigger no longer fires (an **obsoletion** —
area shrank below its tier threshold, domain merged), the agent **appends the
OLD name** to `removed[]` with a timestamp + reason **before** overwriting or
ceasing to (re)generate it. The set of "previously-generated names" is
recoverable from the existing `_skills/` directory listing plus
`refactor-plan.json.dynamic_index_skills`, so no new STM file is needed.

- `removed[]` is **append-only** within a session (mirrors the pack's
  existing append-only history discipline); entries are never silently
  dropped.
- Appends are **idempotent**: do not add a duplicate entry for a name already
  present in `removed[]`.

## How the install script consumes it

After the copy/sync pass (and the receipt diff), the script reads
`removed-skills.json` and, for each bare `removed[].name`, maps it to
`<kb_namespace>-<name>` and deletes `<harness-skills-dir>/<kb_namespace>-<name>/`
if it exists. It **MUST NOT** delete any directory whose name does not start
with this KB's `<kb_namespace>-` — that is how it **never touches another KB's
skills** in a shared harness dir. Deleting an absent dir is a no-op
(idempotent).

## Per-KB namespace interaction (critical)

Because the install script namespaces every installed dir as
`<kb_namespace>-<bare-name>` and confines every deletion (both receipt-diff and
`removed-skills.json`) to the `<kb_namespace>-*` prefix, its delete loop is
provably confined to this KB's skills. Two KBs installing into the same
`.github/skills/` each delete only their own stale entries; neither can clobber
the other.
