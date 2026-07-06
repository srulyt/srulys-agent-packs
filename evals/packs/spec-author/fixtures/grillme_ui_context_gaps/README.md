# Inputs for grillme_ui_context_gaps

Contains `interview-answers.md` — the scripted user's reply when the
orchestrator parks at `awaiting-interview-answers`. The runner copies
its contents into the orchestrator-produced session at
`context/interview-answers.md` when the scripted_user hook fires. This
is a UI-forward feature with missing persona/journey/role context, so
the grill-me interview should raise persona / JTBD / journey / RBAC
questions; the eval asserts against the `interview-questions.md`
artifact.
