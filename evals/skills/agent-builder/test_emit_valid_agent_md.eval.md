---
name: agent-builder-emits-valid-agent-md
target: agent-builder
kind: skill
tags: [skill, slow, judge]
timeout: 300
---

# Agent-builder emits a valid .agent.md
> The skill produces a syntactically and semantically valid `.agent.md`
> for a trivial echo-bot.

## Setup
```yaml
stage: { all: true }
```

## Act
```prompt
Generate a minimal `.agent.md` file for a hypothetical agent named
`echo-bot`. The agent's only job is to echo back the user's message.

Constraints:
- Use proper YAML front-matter.
- Include a `description` field with a quoted string that contains the
  word "Echo" and at least one trigger keyword.
- Include a `tools` list.
- Add a short markdown body explaining the role.

Output the full file contents inside a single fenced code block. Do not
write anything to disk.
```

## Assert
```yaml
stdout_contains:
  - { text: "description", ignore_case: true }   # front-matter arrived
  - { text: "echo-bot" }
judge:
  threshold: 0.7
  criteria: |
    The assistant's response MUST contain a complete `.agent.md` file inside a
    fenced code block. The file MUST:
    1. Start with a YAML front-matter block delimited by `---`.
    2. Have a `description` field whose value is wrapped in double quotes
       (the agent-builder skill's headline rule).
    3. Include the word 'Echo' (case-insensitive) in the description.
    4. Include a `tools:` list.
    5. Have a non-empty markdown body after the front-matter.
    Score 1.0 only if all five are met. Score 0.6 if 3-4 met. Score 0.0 otherwise.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better,
      baseline: rolling_mean, tolerance: 0.1 }
```
