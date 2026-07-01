---
name: SKILL-NAME-short-slug
target: your-skill-name
kind: skill
tags: [skill, smoke]
timeout: 600
---

# One-line title of what this skill eval proves

## Description
What behaviour of the skill this eval checks, in isolation.

## Act
```prompt
The request that should trigger and exercise the skill under test.
```

## Assert
```yaml
files:
  exists:
    - "output/result.md"
contains:
  - path: "output/result.md"
    text: "expected content"
```
