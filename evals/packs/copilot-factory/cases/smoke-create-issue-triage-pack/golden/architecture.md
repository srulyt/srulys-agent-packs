# Reference architecture (issue-triage pack)

This is the reference outline the judge consults for the
``completeness`` and ``faithfulness-to-input`` rubrics. The actual
SUT-produced architecture document is judged against the elements listed
here.

## Required elements

1. **Pack identity** — name (kebab-case, lower) and one-line description.
2. **Agent inventory** — two agents named: an orchestrator and a search
   sub-agent.
3. **Boundaries** — each agent has an explicit "File Access Boundaries"
   section with allowed read paths and allowed write paths.
4. **Tool allow-lists** — each agent declares allowed tools in front-matter.
5. **Invocation contract** — orchestrator's input format (issue
   URL/number) and output format (triage recommendation with label
   suggestions, priority, related-issues summary).
6. **Delegation pattern** — orchestrator calls the search sub-agent
   exactly once per triage request; explicit prompt template.
7. **Failure modes** — at least three concrete failure modes are listed
   with mitigations.
8. **Risks** — section enumerating risks (rate limiting, label
   ambiguity, etc.).
9. **The phrase "issue triage"** must appear verbatim in the architecture
   (faithfulness-to-input check; the user said so).
