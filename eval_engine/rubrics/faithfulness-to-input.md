---
id: faithfulness-to-input
description: |
  Does the SUT artifact accurately reflect the user's input, without
  introducing requirements that weren't asked for and without dropping
  ones that were?
inputs: [artifact, user_input]
output_schema:
  type: object
  required: [score, rationale, evidence]
  properties:
    score: {type: number, minimum: 0, maximum: 1}
    rationale: {type: string}
    evidence: {type: array}
scoring_anchors:
  "0.0": "Artifact contradicts or fabricates substantial parts of the user input."
  "0.5": "Artifact is mostly faithful but introduces or drops at least one non-trivial requirement."
  "1.0": "Artifact preserves every explicit requirement from the input and adds nothing material that wasn't requested or trivially implied."
---

# Faithfulness-to-input rubric

You will be shown:

- ``apply_to = {{apply_to}}``
- Artifact paths:
{{artifact_paths}}
- Golden reference paths (one of them is the user input snapshot):
{{golden_paths}}

Compare the artifact strictly against the user-input snapshot. Flag any
requirement that was added without being requested ("hallucinated scope")
and any that was dropped or weakened. Score per the anchors.
