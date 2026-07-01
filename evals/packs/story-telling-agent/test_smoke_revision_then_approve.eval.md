---
name: story-telling-agent-smoke-revision-then-approve
target: story-orchestrator
kind: agent
tags: [pack, slow]
timeout: 1200
---

# Proposal revision then approve

## Description
Proposal feedback loop: the user rejects the first proposal with specific feedback, the strategist revises, then the user approves. `proposal_iteration` must reach >=2 and Stop-B (no build before APPROVED) must be honoured.

Ported from legacy `cases/smoke-revision-then-approve/`.

## Act
```prompt
@story-orchestrator

Build me a 10-minute deck for our weekly engineering all-hands.

**Audience**: ~80 engineers, mixed seniority.

**Decision needed**: none -- informational. Goal is to share Q1
reliability results and set expectations for Q2.

**Context**:
- Q1 incident count down 32% YoY.
- p95 latency improved from 850ms -> 420ms.
- One major outage in March (12 min); root cause was config rollout.
- Q2 focus: shift-left testing, on-call rotation overhaul.

**Tone**: candid, peer-to-peer. No marketing language.

---

When you show me the proposal, I will respond with feedback the FIRST
time. Specifically: I will ask you to (a) replace the opening with the
March outage timeline rather than the YoY metric, and (b) drop the
comparison slide in favor of a metric spotlight. After your revised
proposal, I will reply ``APPROVED``.

When the deck is built and QA-passed, return the path to the .pptx
file.
```

## Assert
```yaml
files:
  exists:
    - ".story-telling-stm/runs/*/state.json"
    - ".story-telling-stm/runs/*/agents/story-strategist/proposal.md"
    - ".story-telling-stm/runs/*/agents/deck-builder/output.pptx"
matches:
  - { path: ".story-telling-stm/runs/*/state.json", pattern: '"proposal_iterations?"\s*:\s*[2-9]' }
  - { path: ".story-telling-stm/runs/*/state.json", pattern: '"user_approved"\s*:\s*true' }
```
