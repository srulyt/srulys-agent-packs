---
name: ux-interaction-spec-smoke-prd-to-eis
target: ux-interaction-spec
kind: agent
tags: [pack, smoke, slow, judge]
timeout: 3600
---

# A complete PRD becomes a full 22-section EIS, not a reformatted PRD

## Description

Happy-path smoke for the primary use case: a reasonably complete PRD goes in,
three documents come out.

Asserts the structural contract first — all three deliverables exist, `eis.md`
carries all 22 headings in order with no surviving `EIS-PENDING` sentinel,
`ux-pattern-research.md` carries all ten headings even though research is
skipped, and `decision-log.md` carries its six. Then asserts the *substance*
the pack exists to add: a capability matrix in `EIS-§7`, a traceability
section in `EIS-§22`, and — the actual point — derived behaviour and open
questions that were not in the input. A judge checks the permission and state
modelling is real rather than a restatement of the PRD's requirement list.

## Setup

```yaml
stage:
  agent: ux-interaction-spec
  include_skills: true
files:
  - copy: "fixtures/access-request-prd.md"
    dest: "inputs"
```

## Act

```prompt
Feature: Governed data product access
Host product: Acme Data Cloud
Inputs: inputs/access-request-prd.md
Output dir: docs/eis/governed-data-product-access
Research mode: skipped
Interaction mode: non-interactive
On existing files: overwrite
Max review rounds: 1
Max specialist retries: 1

Produce the interaction specification for this feature. Run the full pipeline
to completion and deliver all three documents.
```

## Assert

```yaml
files:
  exists:
    - "docs/eis/governed-data-product-access/eis.md"
    - "docs/eis/governed-data-product-access/ux-pattern-research.md"
    - "docs/eis/governed-data-product-access/decision-log.md"
contains:
  - { path: "docs/eis/governed-data-product-access/eis.md", all: ["## 1. Executive Summary", "## 2. Scope", "## 3. Experience Goals", "## 4. Actors and Roles", "## 5. Conceptual Model", "## 6. Terminology", "## 7. Permissions and Capabilities"] }
  - { path: "docs/eis/governed-data-product-access/eis.md", all: ["## 8. State Models", "## 9. Entry Points and Discovery", "## 10. User Journeys", "## 11. Business / System Workflows", "## 12. Service Blueprint", "## 13. Interaction Scenarios", "## 14. System Feedback and Notifications"] }
  - { path: "docs/eis/governed-data-product-access/eis.md", all: ["## 15. Error and Recovery Behavior", "## 16. Edge Cases", "## 17. Accessibility / Localization Considerations", "## 18. UX Requirements for Design Handoff"] }
  - { path: "docs/eis/governed-data-product-access/eis.md", all: ["## 19. Confirmed Decisions", "## 20. Assumptions", "## 21. Open Questions", "## 22. Requirements Traceability"] }
  - { path: "docs/eis/governed-data-product-access/ux-pattern-research.md", all: ["## 1. Research Objective", "## 2. Host Product Analysis", "## 3. Competitive Products", "## 4. Adjacent Patterns", "## 5. Cross-Product Pattern Matrix"] }
  - { path: "docs/eis/governed-data-product-access/ux-pattern-research.md", all: ["## 6. Patterns We Recommend Adopting", "## 7. Patterns We Recommend Adapting", "## 8. Patterns We Recommend Rejecting", "## 9. Implications for the EIS", "## 10. Sources"] }
  - { path: "docs/eis/governed-data-product-access/ux-pattern-research.md", text: "research_mode: skipped" }
  - { path: "docs/eis/governed-data-product-access/decision-log.md", all: ["## Confirmed Decisions", "## Recommendations Awaiting Decision", "## Blocking Questions", "## Non-Blocking Questions", "## Assumptions", "## Contradictions / Risks"] }
not_contains:
  - { path: "docs/eis/governed-data-product-access/eis.md", text: "<!-- EIS-PENDING" }
  - { path: "docs/eis/governed-data-product-access/eis.md", text: "[Feature]" }
matches:
  - { path: "docs/eis/governed-data-product-access/eis.md", pattern: "DRV-[0-9]{3}" }
  - { path: "docs/eis/governed-data-product-access/eis.md", pattern: "Q-(IN|RS|MD)-[0-9]{3}" }
  # `section_contains` cannot express "inside this section". The engine's
  # `sectionBody` is /#+\s+<name>\s*\n([\s\S]{0,max_chars})/i with NO next-heading
  # bound, so `max_chars` is "how far past the heading to read, into whatever
  # follows" - not "how much of the section to read". Both of these were
  # truncating: section 7 measures 8,252 chars against a 2,500 window and section
  # 22 measures 5,550 against 2,500. They passed run 4 only because their needles
  # landed at index 4 and index 84. A needle that has to land early is not a
  # check. The tempered token (?:(?!\n##\s)[\s\S])*? stops at the next H2 and
  # leaves H3 alone (\s does not match #), so the scan IS the section.
  - { name: "permissions section carries a capability matrix", path: "docs/eis/governed-data-product-access/eis.md", pattern: "##\\s+7\\.\\s+Permissions and Capabilities(?:(?!\\n##\\s)[\\s\\S])*?(?:\\||Capability Matrix)" }
  - { name: "traceability section maps requirement ids", path: "docs/eis/governed-data-product-access/eis.md", pattern: "##\\s+22\\.\\s+Requirements Traceability(?:(?!\\n##\\s)[\\s\\S])*?REQ-" }
judge:
  artifact: "docs/eis/governed-data-product-access/eis.md"
  threshold: 0.7
  criteria: |
    You are scoring an Experience Interaction Specification produced from a PRD
    about governed data product access (analysts request access to data
    products; owners approve or deny; access expires).

    Score 1.0 ONLY if ALL of the following hold:
    (a) Section 4 names actors the PRD did not enumerate as a role list —
        at minimum a requester, a data product owner, and at least one of
        auditor / manager / the system itself — and states for each what they
        can do and what they must never do.
    (b) Section 7 contains a capability matrix with rows crossing actor,
        object, action and conditions — not a prose restatement of the PRD's
        numbered requirements.
    (c) Section 8 models an access request as a lifecycle with named states
        including at least one non-happy state (denied, expired, escalated,
        cancelled or superseded) and names what triggers each transition.
    (d) Sections 10 and 11 are visibly DIFFERENT representations — a
        user-facing journey and a system/business workflow — not the same
        sequence written twice.
    (e) Section 21 raises at least one open question that is genuinely absent
        from the PRD, and section 20 states, for each assumption, what would
        change if it were false.

    Score 0.5 if the document is structurally complete but two or more of
    (a)-(e) are only superficially satisfied.

    Score 0.0 if the document is essentially the PRD's requirement list
    reorganised under new headings, with no derived behaviour, no capability
    matrix, and no new questions.

    Be strict. Headings with text under them is not the same as modelling.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better,
      baseline: rolling_mean, tolerance: 0.1 }
```
