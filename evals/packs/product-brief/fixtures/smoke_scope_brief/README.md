# Inputs for this case

The harness's `copy_tree` step stages this directory into the workspace
root. Keep test inputs here; the system-under-test sees this content as
the starting state of its repository.

This case models a **scope-brief**: the source describes the boundary of
an MVP (what is in and out of scope) and asks for no decision, approval,
or funding. The brief-orchestrator should classify it as a `scope-brief`,
expand Problem Scope and Solution Scope, and omit a Call to Action / Open
Questions section. We keep this README so the directory exists and is
committed to git.
