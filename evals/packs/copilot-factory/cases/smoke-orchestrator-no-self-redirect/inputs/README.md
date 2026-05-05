# smoke-orchestrator-no-self-redirect inputs

Empty workspace seed. The case verifies first-turn behaviour with
no prior session state in `.copilot-factory/`.

The repo's `.github/copilot-instructions.md` (with its routing-rule
guard) and `.github/instructions/factory.instructions.md` are
staged into the workspace by `case.yaml`'s `workspace.steps[]` so
the SUT runs against the real Layer-1 + Layer-2 fix together.
