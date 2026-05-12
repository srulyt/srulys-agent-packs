# Golden — smoke-upper-section-isolation (C1, F1 regression guard)

This case asserts post-F1 behaviour on a creation-mode prompt that
deliberately bait-mixes Problem narrative, Solution direction,
ownership, and rollout into a single paragraph. There is no fixed
golden file — assertions are inline regex (`must_not_match_in_section`)
plus a critic `findings-json` predicate.

## What is asserted

- **Solution Summary** must not contain problem-narrative phrases
  (`drowning`, `12 hours/week`, `no single view`) and must not name
  owners (`Maya`, `Devon`, `platform PM`, `platform EM`).
- **Problem Statement** must not preempt the solution (`dashboard`,
  `drill-down`) and must not name owners.
- **Goals & Success Metrics** must not name owners or describe
  rollout language (`behind a flag`, `two weeks later`).
- Critic `findings-json` must contain no entry whose `issue` or
  `rubric` field includes the substring `isolation` (the D4
  upper-section-isolation sub-rubric).

## What is NOT asserted

- Specific wording in any section.
- Persona table contents (the prompt does not supply enough to fix
  personas).
- Rubric scores other than D4 `content-quality` (escalated to
  `warn` / `threshold: 0.7`).

## Failure interpretation

- A `must_not_match_in_section` hit → F1 has regressed in the drafter.
- An `isolation` finding from the critic → F1 has regressed in the
  critic OR the drafter.
- Both → F1 has been reverted across both surfaces.
