---
name: hello-agent
target: REPLACE-WITH-YOUR-AGENT
kind: agent
tags: [smoke]
timeout: 600
---

# Agent produces a well-formed artifact
> A good result: the agent creates an on-topic Markdown artifact.

## Description
This eval checks the baseline "does the agent do the job" contract: given a
real prompt, the agent must produce at least one Markdown artifact that is
on-topic and directly answers the request. The judge scores whether the
content actually satisfies the prompt (not just that a file exists).

## Setup
```yaml
# stage: { agent: REPLACE-WITH-YOUR-AGENT }   # inferred from target+kind
# files: [{ copy: "fixtures/**", dest: "." }] # optional starting files
```

## Act
```prompt
Replace this with a prompt that exercises a real scenario for your agent.
Do NOT include the expected answer -- the point of the judge is that the
agent had to work it out.
```

## Assert
```yaml
files:
  exists: ["**/*.md"]
judge:
  # artifact: path/to/output.md    # omit to judge stdout
  threshold: 0.7
  criteria: |
    Describe concretely what a good result looks like. Be strict: score 1.0
    only if ALL criteria are met, 0.5 for partial, 0.0 if off-topic.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better,
      baseline: rolling_mean, tolerance: 0.1 }
```
