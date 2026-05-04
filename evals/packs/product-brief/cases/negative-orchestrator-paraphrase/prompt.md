@brief-orchestrator

Build a brief from ``inputs/``. After the composer returns its
``product-brief-draft`` fence, the orchestrator MUST persist the
fence body byte-for-byte to ``product-brief.draft.md`` before any
editing pass. The harness diff-checks the persisted draft against
the captured fence — paraphrasing or "improving" the body during
persistence is a violation.

Decision context: hiring plan for FY26. Audience: head of engineering.
