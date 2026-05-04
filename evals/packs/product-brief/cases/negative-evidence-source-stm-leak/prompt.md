@brief-orchestrator

Build a brief from ``inputs/``. The user has NOT requested an
Evidence Log section. Verify that:

- The evidence-analyst's evidence-log.md contains zero source
  references whose path starts with ``.product-brief-agent-stm/``.
- The final brief contains no Evidence Log section (since the user
  did not request one).
- No source reference anywhere in the brief points to an STM working
  file; every cited source is the original user-provided file name.

Audience: VP Engineering. Decision: whether to fund the migration
project for next half.
