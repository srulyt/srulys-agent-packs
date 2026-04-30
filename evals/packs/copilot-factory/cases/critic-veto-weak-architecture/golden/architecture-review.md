# Reference architecture-review (critic-veto-weak-architecture)

This is the reference outline the judge consults for the
`coherence` and `format-compliance` rubrics. The actual SUT-produced
review document is judged against the elements listed here.

## Required elements

1. **Verdict block** — a fenced ``verdict`` section containing
   `review_type: architecture`, `status: BLOCKING`, and a non-empty
   `recommendation` field.
2. **Blocking issues** — at least three blocking issues identified:
   - Missing per-agent file access boundaries
   - Missing tool allow-lists
   - Missing skills section / agent inventory
3. **References** — the review references the user request and the
   pre-staged architecture document by path.
4. **No code/architecture written** — the critic must NOT modify
   `architecture.md`. Only the review file is produced.
