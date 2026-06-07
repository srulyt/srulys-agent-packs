# Evals — `ears-prd-workflow` skill (EARS PRD Plugin)

Skill-in-isolation evals for the master workflow skill of the
`prd-pilot` plugin. `test_smoke_happy_path.py` drives the full 4-step flow
on a well-specified feature and judges that a valid EARS PRD (mandatory
sections, ≥3 single-`shall` FRs with nested Given/When/Then ACs, Open
Questions, a `prd-summary` block, no fabrications) is produced.
`test_outline_rejection_loop.py` verifies that rejecting the step-3
outline loops back to steps 1–2, re-grills only the touched slice, and
re-presents a revised outline with `revisions_used` incremented without
drafting — the workflow skill owns this loop (carry-concern C2).

Run: `pytest evals/skills/ears-prd-workflow/`
