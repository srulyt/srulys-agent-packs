# Inputs for grillme_no_cap_mc_freeform

Contains `interview-answers.md` — the scripted user's reply when the
orchestrator parks at `awaiting-interview-answers` during the grill-me
interrogation. The runner copies this file's contents into the
orchestrator-produced session at `context/interview-answers.md` when
the scripted_user hook fires. The eval asserts against the
`interview-questions.md` artifact the interviewer produced BEFORE the
answers are applied.
