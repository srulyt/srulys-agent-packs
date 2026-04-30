---
id: format-compliance
description: |
  Does the artifact comply with the structural format the spec requires
  (headings, tables, code-block fences, front-matter)?
inputs: [artifact]
output_schema:
  type: object
  required: [score, rationale, evidence]
  properties:
    score: {type: number, minimum: 0, maximum: 1}
    rationale: {type: string}
    evidence: {type: array}
scoring_anchors:
  "0.0": "Artifact is unparseable or violates more than one major structural rule."
  "0.5": "Artifact mostly conforms; one minor format infraction (e.g., a missing heading level, table column off)."
  "1.0": "Artifact conforms to every structural rule the spec requires."
---

# Format-compliance rubric

You will be shown:

- ``apply_to = {{apply_to}}``
- Artifact paths:
{{artifact_paths}}
- Golden reference paths:
{{golden_paths}}

The golden reference (where present) demonstrates the expected
structural shape. Compare structure only — not content quality. Score
per the anchors and cite specific structural defects in ``evidence``.

This rubric is appropriate to promote to ``severity: blocker`` once it
has stabilised across runs, because format-compliance failures usually
indicate a real defect rather than judge variance.
