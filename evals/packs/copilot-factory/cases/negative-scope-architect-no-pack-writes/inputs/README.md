# Inputs for negative-scope-architect-no-pack-writes

The harness's `copy_tree` step stages this directory into the
workspace root. No staged inputs are required for this case; the
SUT only needs an empty git repo plus the staged factory agents and
skills (handled by later workspace steps in `case.yaml`).

This README exists so the directory is committed to git.
