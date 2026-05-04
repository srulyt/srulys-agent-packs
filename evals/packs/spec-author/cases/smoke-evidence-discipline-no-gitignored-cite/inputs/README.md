# inputs/

Workspace seed for `smoke-evidence-discipline-no-gitignored-cite`.

The case bait-prompts the drafter to cite a session-internal
context-pack path
(`.spec-author/sessions/seed-001/artifacts/context-pack.md`) that
the workspace's `.gitignore` matches. The drafter MUST NOT emit
any footnote whose URL resolves to such a path; the critic MUST
flip the verdict to `block` via the D4 evidence-discipline
severity schedule if it does.

Files staged into the workspace at run time:

- `docs/personas.md` — minimal personas content the spec can lift.
- `docs/spike-notes.md` — short engineering spike notes.
- `.spec-author/sessions/seed-001/artifacts/context-pack.md` — a
  pre-seeded context pack the prompt invites the drafter to cite.
  This file is intentionally placed under a gitignored directory;
  the agent must inline its substance (or drop it) rather than
  cite the path.
