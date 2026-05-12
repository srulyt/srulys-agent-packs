# Inputs for smoke-update-minimal-edit-discipline

Contains a prior spec (under `fixtures/prior-spec-v1.md`) whose prose
is **stylistically imperfect but technically correct**: a few
slightly long sentences, an `&` that could be `and`, a table layout
that a tidy author might prefer to bullet-list, and a Solution
Summary that names an internal Kafka topic. None of these are
factually wrong. None violate a hard rule the user has asked to
enforce. **None of them should be touched in the revision.**

The user request asks for exactly one change: add a new FR for
keyboard shortcuts. The eval verifies that the drafter:

- Adds the new FR, bumps the version, adds the `Updates:` header,
  the `## Changes since v1.0` preamble, and a CHANGELOG entry —
  AND NOTHING ELSE.
- Emits `edit-audit-json` with every modified span justified by a
  legitimate reason (`correctness`, `requested`, `missing`,
  `mechanics`).
- Preserves the bait spans listed in
  `case.yaml.artifact_content_assertions.must_contain_verbatim`
  byte-for-byte.

The runner copies the entire `inputs/` tree into the workspace
before the run; the prompt references the prior spec at
`fixtures/prior-spec-v1.md`.
