---
id: completeness
description: |
  Does the SUT artifact cover every element the golden reference treats as required?
inputs: [artifact, golden]
output_schema:
  type: object
  required: [score, rationale, evidence]
  properties:
    score: {type: number, minimum: 0, maximum: 1}
    rationale: {type: string}
    evidence: {type: array}
scoring_anchors:
  "0.0": "More than half of the required elements from the golden reference are missing."
  "0.5": "Most required elements present; one or two non-trivial omissions remain."
  "1.0": "All required elements present and substantively addressed; nothing essential missing."
---

# Completeness rubric

You will be shown:

- ``apply_to = {{apply_to}}``
- Artifact paths:
{{artifact_paths}}
- Golden reference paths:
{{golden_paths}}

The golden reference enumerates the elements a correct artifact must
cover. For each enumerated element, decide whether the SUT artifact
addresses it substantively (not just by mention).

Score per the anchors. Cite each element you found missing in
``evidence`` with a path + quote pointing at the golden reference, and
each present element similarly pointing at the SUT artifact when helpful.
