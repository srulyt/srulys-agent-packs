---
name: copilot-factory-smoke-issue-triage
target: copilot-factory
kind: agent
tags: [pack, slow, judge]
timeout: 900
---

# Creates two-agent issue-triage pack

## Description
Smoke evals for the `copilot-factory` agent pack.

This `.eval.md` spec runs an action prompt and then evaluates the result with rubric and structural checks:

1. Stages the pack (and shared skills/instructions) into a tmpdir workspace via the `agent_pack` fixture.
2. Runs `copilot -p ... --agent copilot-factory` non-interactively.
3. Asserts on the artifacts the factory produces.
4. Optionally calls the LLM-as-judge helper (`judge` fixture) to score the architecture document for semantic correctness.

These replace the legacy YAML cases under `evals/packs/copilot-factory/cases/`. See `evals/README.md` for the authoring guide.

## Setup
```yaml
stage: { all: true }
```

## Act
```prompt
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
on every agent. The triage feature is **issue triage** -- keep that
wording in your architecture document.

Use your standard four-phase workflow (architect -> engineer -> critic) and
land everything under your normal session directory.
```

## Assert
```yaml
files:
  exists:
    - ".copilot-factory/sessions/*/artifacts/architecture.md"
    - ".copilot-factory/sessions/*/artifacts/build-manifest.json"
glob_count:
  - { pattern: ".copilot-factory/sessions/*/artifacts/architecture.md", equals: 1 }
  - { pattern: ".copilot-factory/sessions/*/artifacts/build-manifest.json", equals: 1 }
  - { pattern: "agent-packs/*/.github/agents/*.agent.md", equals: 2 }
  - { pattern: "agent-packs/*/README.md", equals: 1 }
judge:
  artifact: ".copilot-factory/sessions/*/artifacts/architecture.md"
  threshold: 0.7
  criteria: |
    The architecture document MUST:
    1. Describe exactly two agents (an orchestrator + a search sub-agent for finding related issues).
    2. Use the phrase 'issue triage' verbatim somewhere in the document (the user requested this feature wording).
    3. Declare File Access Boundaries (read/write scopes) for each of the two agents.
    4. Be coherent prose with named sections, not a stub.
    Score 1.0 only if all four are met. Score 0.5 if 2-3 are met. Score 0.0 if 0-1 are met.
```
