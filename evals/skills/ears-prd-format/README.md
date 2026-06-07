# Evals — `ears-prd-format` skill (EARS PRD Plugin)

Skill-in-isolation eval for the EARS format / quality-bar skill of the
`prd-pilot` plugin. `test_ears_shape.py` gives the skill a short list of
raw requirements and judges that every formatted Functional Requirement
matches one of the 6 EARS patterns, contains exactly one `shall`, names a
system (never "we"/"the user"), expresses what-not-how, and carries at
least one nested, testable Given/When/Then acceptance criterion.

Run: `pytest evals/skills/ears-prd-format/`
