# Inputs for this case

The harness's `copy_tree` step stages this directory into the workspace
root. Keep test inputs here; the system-under-test sees this content as
the starting state of its repository.

The case's `prompt.md` is the user message; per-case `inputs/` files
(if any) are user-provided source material the brief-orchestrator will
hand off to `@evidence-analyst`. We keep this README so the directory
exists and is committed to git.
