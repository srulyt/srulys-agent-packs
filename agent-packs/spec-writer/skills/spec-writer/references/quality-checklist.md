# Quality checklist

Check the spec against this list before presenting it. A **blocker** must be fixed. A **major** issue should be fixed or explicitly called out to the user.

## Blockers

- **Sections:** a mandatory section is missing, renamed, out of order, or empty without a `[TBD — reason]` + `OQ-NN`.
- **Fabrication:** invented evidence, quotes, metrics, personas, jobs, journey steps, roles, or answers.
- **Lifecycle:**
  - Status and version disagree (the `-draft` suffix doesn't match Status).
  - A draft carries change-tracking content or bumps its version.
  - A spec was published without explicit instruction or without a changelog entry.
- **IDs:** a published ID was renumbered or silently deleted, or a reference is left dangling.
- **Citations:** a citation points to a local, scratch, or `.gitignore`-matched path, or to a non-authoritative or non-primary source.
- **Template:** a persona table is duplicated, or personas are restated outside Users & Personas.

## Major

- **FR shape:** an FR is not a single EARS shall-statement, lacks a priority, names implementation in `product`/`mixed` mode, or is vague or unfalsifiable.
- **ACs:** an FR has no nested Given/When/Then AC, or an AC paraphrases the FR instead of testing it.
- **What-if coverage:**
  - An FR or journey step covers only the happy path even though plausible failure, boundary, permission, or concurrency cases exist (see [what-if coverage](what-if-coverage.md)).
  - A policy-level what-if was guessed rather than written as TBD + OQ.
- **Goals:** a goal lacks a baseline, a target, or a measurement window, or describes an output instead of an outcome.
- **Traceability:** the chain problem/users → goals → FRs → ACs → metrics doesn't hold, or a P0 depends on a P1/P2.
- **Gating:**
  - A gated section is included without its axis firing (or is disallowed by `spec_kind`), or is omitted despite a clear signal.
  - The UX section appears for a single-affordance tweak.
- **Roles:** on UI-forward specs, a primary journey is missing or narrative-only, a role/permission matrix is missing, or there are no deny-path ACs.
- **NFRs:** NFRs restate the platform baseline, or lack measurable targets or verification.
- **Content placement:** upper sections carry trade-offs, per-FR rationale, edge cases, or open questions that belong lower.
- **Updates:** an update edits text without a valid reason (minimal-edit rule), or rewrites the upper sections unrequested.

## Minor

- **Length:** a backstop word cap is exceeded, or a sentence runs over 25 words.
- **Wording:** filler, buzzwords, unexplained hedges, or bold pseudo-headers.
- **Out of Scope:** contains an item that fails the adjacency test.
- **Formatting:** bare-name cross-references instead of anchored links, or citation formatting defects.
