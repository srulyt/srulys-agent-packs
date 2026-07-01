---
name: context-pack-builder-update-over-rewrite
target: cpb-orchestrator
kind: agent
tags: [pack, slow]
timeout: 1100
---

# Updating auth context pack preserves human edits without duplication

## Description
Idempotent update-over-rewrite smoke: running twice on the same feature yields exactly one pack dir (no duplicate), adds a Change Log entry on the second run, preserves a human-marked block, and a no-change re-run is a no-op.

## Act
```prompt
Build a context pack for the "auth" feature in this repository.
BOUNDED MODE (fast pass): keep this run cost-capped and single-pass.
Scope — confine discovery/analysis to EXACTLY src/auth/ (login.py and
session.py); do NOT scan the rest of the repository. The feature handles
login and session tokens. Produce the pack in context-packs/ and run to
completion.

Update the existing context pack for the "auth" feature.
BOUNDED MODE (fast pass): keep this run cost-capped and single-pass.
I added password reset to src/auth/reset.py. Scope — confine
discovery/analysis to EXACTLY src/auth/; do NOT scan the rest of the
repository. Re-run discovery/analysis and merge the update into the
EXISTING pack (do NOT create a duplicate pack). Preserve any
human-authored sections.
```

## Assert
```yaml
glob_count:
  - { pattern: "context-packs/*-context/plugin.json", equals: 1 }
contains:
  - { path: "context-packs/*-context/skills/*-context/SKILL.md", text: "HAND-WRITTEN NOTE: do not delete." }
  - { path: "context-packs/*-context/skills/*-context/SKILL.md", text: "Change Log" }
```
