---
name: ux-interaction-spec-smoke-conflict-and-gap-surfacing
target: ux-interaction-spec
kind: agent
tags: [pack, smoke, slow, judge]
timeout: 3600
---

# Contradictions are surfaced, not silently resolved; gaps become questions

## Description

Three inputs that disagree with each other, with three defects planted
deliberately:

1. **A contradiction.** The PRD caps pending requests at **3**; the ops
   runbook says production runs at **5**. Neither is authoritative. The pack
   must record the conflict as a contradiction and must not pick a winner.
2. **An unmodeled asynchronous operation.** The PRD says approval grants
   access "immediately"; the provisioning API is `202 Accepted` with a
   `provisioning → active | failed | partial` lifecycle taking minutes to
   hours. The specification must model the async states and the `partial`
   and `failed` outcomes.
3. **A missing permission rule.** The runbook describes org admins approving
   on behalf of an unresponsive owner; the PRD's role table has no org admin
   at all. The pack must surface this as a permission-model gap rather than
   inventing a rule or ignoring it.

This is the pack's highest-value behaviour, so the structural assertions are
narrow and the judge criteria name the three defects explicitly.

## Setup

```yaml
stage:
  agent: ux-interaction-spec
  include_skills: true
files:
  - copy: "fixtures/conflicting-inputs"
    dest: "inputs"
```

## Act

```prompt
Feature: Access governance
Host product: Acme Data Cloud
Inputs: inputs/prd-access-governance.md, inputs/ops-runbook.md, inputs/provisioning-api.md
Output dir: docs/eis/access-governance
Research mode: skipped
Interaction mode: non-interactive
On existing files: overwrite
Max review rounds: 1
Max specialist retries: 1

These three documents were written by different teams and do not fully agree.
Produce the interaction specification and deliver all three documents.
```

## Assert

```yaml
files:
  exists:
    - "docs/eis/access-governance/eis.md"
    - "docs/eis/access-governance/ux-pattern-research.md"
    - "docs/eis/access-governance/decision-log.md"
contains:
  - { path: "docs/eis/access-governance/eis.md", all: ["## 7. Permissions and Capabilities", "## 8. State Models", "## 15. Error and Recovery Behavior", "## 16. Edge Cases", "## 20. Assumptions", "## 21. Open Questions", "## 22. Requirements Traceability"] }
  - { path: "docs/eis/access-governance/decision-log.md", text: "## Contradictions / Risks" }
  - { path: "docs/eis/access-governance/decision-log.md", any: ["CON-001", "CON-"] }
not_contains:
  - { path: "docs/eis/access-governance/eis.md", text: "<!-- EIS-PENDING" }
matches:
  - { path: "docs/eis/access-governance/eis.md", pattern: "Q-(IN|RS|MD)-[0-9]{3}" }
  # The async state vocabulary must appear INSIDE section 8, and `section_contains`
  # cannot express that. Its `max_chars` window is not bounded by the next heading,
  # so it is wrong in both directions: 4000 truncated a section measured at 8,305-
  # 13,462 chars across the six run-4 documents (the needles first occur at index
  # 4,168 here, just past the cutoff), while any window large enough to cover the
  # section spills into sections 9+ and passes on THEIR text - verified vacuous in
  # 4 of 6 documents at max_chars 16000. Bounding the scan with (?!\n##\s) keeps it
  # strictly inside section 8 and needs no window at all.
  - { name: "state models section models the async provisioning outcomes", path: "docs/eis/access-governance/eis.md", pattern: "##\\s+8\\.\\s+State Models(?:(?!\\n##\\s)[\\s\\S])*?\\b(?:provisioning|partial|failed)\\b", flags: "i" }
  # Same conversion, `all` form. A lazy scan can only prove ONE needle, so each
  # needle gets its own tempered lookahead anchored at the same position - the
  # position immediately after the heading. Both must succeed, and neither can
  # reach past the next H2. Equivalent to the old all: ["3", "5"] but bounded.
  #
  # KNOWN-WEAK (deliberate, recorded for a later turn):
  #   The two needles are bare digits "3" and "5" scanning a ~2,025-char
  #   section, so they are satisfiable by any incidental digit - a date, a
  #   count, a section cross-reference. Widening them was NOT done in this turn
  #   on purpose: this conversion is accepted precisely because it replays
  #   run 4 one-for-one, and changing WHAT is measured would forfeit that
  #   property and mix a scoping fix with a strength fix.
  #   Intended widening, to be done deliberately and re-baselined:
  #   require both digits inside a single sentence, or require each adjacent
  #   to cap/pending context (e.g. /\b3\b[^.\n]{0,80}pending/), so the check
  #   witnesses the two pending-request caps rather than two digits.
  - { name: "contradictions section names both pending-request caps", path: "docs/eis/access-governance/decision-log.md", pattern: "##\\s+Contradictions / Risks\\s*\\n(?=(?:(?!\\n##\\s)[\\s\\S])*?3)(?=(?:(?!\\n##\\s)[\\s\\S])*?5)" }
judge:
  artifact: "docs/eis/access-governance/eis.md"
  threshold: 0.7
  criteria: |
    You are scoring an Experience Interaction Specification produced from three
    disagreeing inputs: a PRD, an ops runbook, and an entitlement provisioning
    API integration note. Three defects were planted.

    Score 1.0 ONLY if ALL THREE are handled correctly:

    (1) CONTRADICTION — The PRD caps pending requests per requester at 3; the
        ops runbook says the production cap is 5 and is configured per tenant.
        The specification must SURFACE this disagreement (as a contradiction,
        a risk, or an open question naming both values) and must NOT silently
        adopt one value as a requirement. Picking 3 or 5 without flagging the
        conflict is a failure.

    (2) ASYNC OPERATION — The PRD says approval grants access "immediately" and
        the requester sees the data product "on the next page load". The
        provisioning API is asynchronous: 202 Accepted, then provisioning →
        active | failed | partial, taking 30 seconds to (p99) 11 minutes, with
        named failure reasons (unknown_principal, resource_not_found) and a
        partial-grant case where the requester silently gets less access than
        was approved. Revocation is asynchronous too. The specification must
        model the pending/provisioning period as a real state with real user
        experience, and must specify behaviour for the failed and partial
        outcomes. Treating approval as instantaneous is a failure.

    (3) MISSING PERMISSION RULE — The runbook says org admins can approve (and
        technically deny) on behalf of an unresponsive data product owner after
        5 business days. The PRD's role table contains only Requester, Data
        product owner and Auditor — no org admin. The specification must
        surface this as a permission-model gap: either an open question about
        whether org-admin override is in scope, or an explicitly labelled
        assumption. Inventing a fully-specified override rule as if it were a
        confirmed requirement is a failure; omitting the org admin entirely is
        also a failure.

    Score 0.7 if two of the three are handled correctly.
    Score 0.3 if one is.
    Score 0.0 if none is, or if the document reads as though the three inputs
    agreed with each other.

    Be strict. Silently reconciling a conflict is the specific failure mode
    being tested.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better,
      baseline: rolling_mean, tolerance: 0.1 }
```
