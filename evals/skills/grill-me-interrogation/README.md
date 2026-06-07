# Evals — `grill-me-interrogation` skill (EARS PRD Plugin)

Skill-in-isolation eval for the step-2 interrogation skill of the
`prd-pilot` plugin. `test_question_discipline.py` gives the skill an
under-specified brief with one enumerable-answer gap (auth/sharing model)
and one open-ended gap (latency budget) and judges question discipline:
one gap per question, P0/P1/P2 tags, multiple-choice (2–6 distinct
options + a "Not sure / decide later" / freeform escape) for the
enumerable gap, freeform for the open-ended gap, and no invented answers.
The judge explicitly does **not** assert any maximum question count — the
skill removes the legacy cap deliberately.

Run: `pytest evals/skills/grill-me-interrogation/`
