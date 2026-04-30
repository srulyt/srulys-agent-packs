# Golden references for negative-scope-architect-no-pack-writes

This case is primarily a structural/scope check — the harness verifies
the architect's `session_files` are confined to
`.copilot-factory/sessions/<id>/artifacts/architecture.md` and that
neither the architect nor any other sub-agent wrote under
`agent-packs/` or `evals/packs/`.

No golden artifacts are required for the judge. The README exists so
the directory is committed to git.
