# Inputs (smoke-palette-preflight-rollback)

This directory is the workspace seed for the case. Its contents
are copied into the case's isolated working directory before the
prompt is run.

For this case the input set is intentionally empty — the only
mutation needed is the overwrite of
`.github/skills/slide-design-systems/references/systems/customer-coral.md`
with `fixtures/customer-coral.rollback.md`, which is performed
by the `copy_file` step in `case.yaml.workspace.steps`.

The agent set, skills, and STM scaffolding are sourced from the
real `agent-packs/story-telling-agent/` tree via the `copy_tree`
steps that precede the rollback overwrite.
