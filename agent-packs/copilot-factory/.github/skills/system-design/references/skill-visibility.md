# Skill Visibility Rule

Every agent in a pack can load every skill. When deciding whether
content belongs in a skill or in an agent prompt, ask:

> If a different agent loaded this skill, could it cause that agent to
> overstep its role or scope?

- **Yes** → Keep the content inside the owning agent's prompt, or
  beside it as an agent-local file the agent reads directly. Do NOT
  package it as a skill.
- **No** (cross-cutting reference: templates, naming rules, format
  specs, regex patterns, link to source-of-truth docs) → Safe to
  extract into a skill or skill reference.

## Worked classifications

| Content | Decision | Reason |
|---|---|---|
| YAML `description` quoting rule | skill-reference | Format rule, harmless if any agent reads it |
| Eval directory layout + skeletons | skill-reference | Reference for whoever authors evals |
| Critic severity model | agent-prompt (critic-only) | Only the critic should apply it |
| Engineer build-step sequence | agent-prompt (engineer-only) | Other agents must not perform builds |
| Negative-scope ("must NOT") lists | agent-prompt (per agent) | Each agent's negatives are role-specific |
| Output contracts (per agent) | agent-prompt (per agent) | Same reason |
| Topology patterns (hierarchical, pipeline) | skill-reference | Pure reference |
| File-access boundary patterns table | skill-reference | Reference; per-agent values stay in agent prompt |

## Heuristic

If the content is **a rule the agent must follow when acting**, keep it
in the agent prompt. If the content is **knowledge the agent consults
to act correctly**, a skill reference is fine.

## Agent-local files

When a piece of detail is too large for an agent prompt but is
role-specific (e.g. the engineer's full build checklist), put it in a
markdown file **next to the agent** (same directory) and have only
that agent read it. Do not package it as a skill — that exposes it to
every agent in the pack.
