# Inputs — smoke-stop-a-disambiguation

Fixtures for the C4 + C5 corner case.

- `interview-answers-partial.md` — scripted user reply to the first
  Stop B prompt. Deliberately leaves the rollout-risk P0 blank so
  the orchestrator must issue exactly one targeted retry, then
  proceed with a `[TBD]` placeholder.

The two ambiguous Stop A replies and the final `APPROVE` are inlined
in `case.yaml`'s `scripted_user:` array — they are short strings, not
files.
