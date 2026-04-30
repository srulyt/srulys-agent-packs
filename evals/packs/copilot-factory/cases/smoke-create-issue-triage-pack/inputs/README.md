# Inputs for the smoke-create-issue-triage-pack case

The harness's `copy_tree` step stages this directory into the workspace
root. Keep test inputs here; the system-under-test sees this content as
the starting state of its repository.

The case's `prompt.md` is the user message; nothing in `inputs/` is
required to be present for the SUT to succeed. We keep this README so
the directory exists and is committed to git.
