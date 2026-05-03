# Golden artefacts for smoke-update-existing-spec

No byte-for-byte golden. The case asserts via:
- path patterns (specification.md AND CHANGELOG.md must exist);
- artifact_content_assertions (Updates: header, FR-07 [Deprecated],
  "Changes since v1" preamble in spec; ### Added and ### Deprecated
  in CHANGELOG);
- rubric overrides escalating id-stability and versioning-correctness
  to error.
