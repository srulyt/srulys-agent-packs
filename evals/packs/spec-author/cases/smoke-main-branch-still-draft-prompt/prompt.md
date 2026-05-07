@spec-author update `docs/specs/quick-toggle.md` — please add a
quick note to the "Out of Scope" section saying we won't add
per-channel preferences until at least Q3.

That's the only edit. (Note: I have not specified `STATUS:` or any
publish gesture in this prompt — the orchestrator should run its
mode-decision logic.)

## Pre-supplied answers (do not park; proceed straight through)

This is a non-interactive run. Treat the following as already
answered — do not pause at any `awaiting-*` park:

- **Mode decision (`awaiting-mode-decision`):** `KEEP-DRAFT` —
  this stays a draft; do NOT publish.
- **Stop A (structure approval):** `APPROVE` (first ask)

The orchestrator should still emit the mode-decision prompt /
spec-status block in its output (so the rubric can verify the
prompt was generated), but it must NOT pause for stdin — proceed
end-to-end using the answers above.
