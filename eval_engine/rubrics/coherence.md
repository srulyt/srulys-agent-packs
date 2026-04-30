---
id: coherence
description: |
  How internally consistent and well-structured is the SUT's main artifact?
inputs: [artifact]
output_schema:
  type: object
  required: [score, rationale, evidence]
  properties:
    score: {type: number, minimum: 0, maximum: 1}
    rationale: {type: string}
    evidence: {type: array}
scoring_anchors:
  "0.0": "Artifact is contradictory, incomplete, or shows clear copy-paste/template residue."
  "0.5": "Artifact is mostly coherent but has at least one notable contradiction, gap, or unresolved thread."
  "1.0": "Artifact is internally consistent end-to-end; sections reinforce each other; no dangling references."
---

# Coherence rubric

You will be shown:

- The SUT artifact paths to evaluate: ``apply_to = {{apply_to}}``
- Artifact paths:
{{artifact_paths}}
- Golden reference paths (may be empty):
{{golden_paths}}

Read the artifacts and evaluate **coherence only**: do all sections agree
with each other; are forward references resolved; are decisions presented
in one place stated consistently elsewhere? Do not score correctness or
completeness here — those have separate rubrics.

Use the anchors above. Output the JSON object specified in
``output_schema`` and nothing else.
