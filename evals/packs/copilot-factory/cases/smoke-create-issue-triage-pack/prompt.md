Please design and build a small Copilot CLI agent pack that helps a
maintainer triage incoming GitHub issues. The pack should have **two
agents**:

1. An orchestrator that receives an issue URL or number and returns a
   triage recommendation (label suggestions, priority, and a short
   summary of any duplicate or related issues it found).
2. A sub-agent specialised in searching the repository for related
   issues and prior discussion.

Treat this as a real production pack: it must include `agent-packs/<name>/`
with both agent definitions, a README, and explicit File Access Boundaries
on every agent. The triage feature is **{{feature}}** — keep that wording
in your architecture document.

Use your standard four-phase workflow (architect → engineer → critic) and
land everything under your normal session directory.
