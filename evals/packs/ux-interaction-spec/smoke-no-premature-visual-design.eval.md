---
name: ux-interaction-spec-smoke-no-premature-visual-design
target: ux-interaction-spec
kind: agent
tags: [pack, smoke, slow, judge]
timeout: 3600
---

# Visual hints in the input do not become visual design in the EIS

## Description

The load-bearing constraint of the whole pack: specify behaviour, not
interface. The fixture brief is deliberately stuffed with visual decisions —
`16px semibold`, `#6B7280`, a green/red button pair, `8px` spacing, a modal,
Inter, a `24px` page gutter, a bell icon, a three-across card grid — alongside
the behaviour that actually matters.

Asserts that none of those visual attributes survive into `eis.md`, and that
the behaviour underneath them does. Value tokens (`16px`, `#6B7280`,
`semibold`) are checked as literal needles; the typeface constraint is checked
by context, because naming the concept while explicitly deferring it is the
compliant behaviour and must not be punished. The two sections where
interface-layer content is permitted (`## 9. Entry Points and Discovery` and
`## 18. UX Requirements for Design Handoff`) are checked by judge for
phrasing-as-constraint rather than phrasing-as-design.

## Setup

```yaml
stage:
  agent: ux-interaction-spec
  include_skills: true
files:
  - copy: "fixtures/visual-hint-brief.md"
    dest: "inputs"
```

## Act

```prompt
Feature: Owner approval inbox
Host product: Acme Data Cloud
Inputs: inputs/visual-hint-brief.md
Output dir: docs/eis/owner-approval-inbox
Research mode: skipped
Interaction mode: non-interactive
On existing files: overwrite
Max review rounds: 1
Max specialist retries: 1

Produce the interaction specification for this feature and deliver all three
documents.
```

## Assert

```yaml
files:
  exists:
    - "docs/eis/owner-approval-inbox/eis.md"
    - "docs/eis/owner-approval-inbox/ux-pattern-research.md"
    - "docs/eis/owner-approval-inbox/decision-log.md"
not_contains:
  - { path: "docs/eis/owner-approval-inbox/eis.md", text: "#6B7280", ignore_case: true }
  - { path: "docs/eis/owner-approval-inbox/eis.md", any: ["16px", "8px", "24px"], ignore_case: true }
  # "semibold" is a weight VALUE and "font-family" a CSS property name: neither
  # can occur in a natural out-of-scope sentence, so a bare needle is safe.
  # "typeface" is NOT safe as a bare needle and "Inter" is not safe as a bare
  # substring - both are enforced by the context-scoped `matches` guards below.
  - { path: "docs/eis/owner-approval-inbox/eis.md", any: ["semibold", "font-family"], ignore_case: true }
  - { path: "docs/eis/owner-approval-inbox/eis.md", text: "<!-- EIS-PENDING" }
matches:
  - { name: "no hex colors in eis.md", path: "docs/eis/owner-approval-inbox/eis.md", pattern: "^(?![\\s\\S]*#[0-9a-fA-F]{6}\\b)[\\s\\S]*$" }
  # Typeface enforcement, in two parts.
  #
  # (1) No typeface is NAMED. The brief pushes "Inter"; a bare substring needle
  #     for it matches "Interaction" and is therefore unsatisfiable in a document
  #     class called "Experience Interaction Specification". \b makes it a
  #     delimited token: \bInter\b occurs 0 times across all six run-4 documents
  #     (~600 KB) but still catches "set in Inter" / "Inter typeface".
  #     \b is ALSO satisfied by a hyphen, so \bInter\b still matched
  #     "Inter-tenant" / "Inter-service" at sentence start - a latent false
  #     failure of exactly the family this check was rewritten to end. The
  #     (?!-) suffix closes it without touching the other typefaces, whose
  #     names are not productive English prefixes.
  - { name: "no typeface is specified by name", path: "docs/eis/owner-approval-inbox/eis.md", pattern: "^(?![\\s\\S]*\\b(?:Inter(?!-)|Helvetica|Arial|Roboto|Lato|Verdana|Calibri|Futura|Garamond|Tahoma|Times New Roman|Segoe UI|SF Pro|Open Sans|Noto Sans)\\b)[\\s\\S]*$" }
  # (2) No typeface is GIVEN A VALUE. The requirement is that the document must
  #     not SPECIFY a typeface - not that it may never name the concept while
  #     declining to specify one. The pack's own out-of-scope disclaimer
  #     ("...color, typeface, spacing... are deferred to interface design") is
  #     the sentence that PROVES compliance, so it must not trip the check.
  #     This fires only on a copula/assignment followed by a real value, and
  #     explicitly exempts deferral values.
  #     The optional modifier group admits an intervening noun, so
  #     "font family is Inter" and "typeface family: Roboto" fire; without it
  #     the copula had to follow the noun directly and those forms escaped.
  - { name: "typeface or font is never given a value", path: "docs/eis/owner-approval-inbox/eis.md", pattern: "^(?![\\s\\S]*\\b(?:typefaces?|font-family|fonts?)\\b(?:[ \\t]+(?:sizes?|weights?|famil(?:y|ies)|styles?))?[ \\t]*(?:[:=]|\\bis\\b|\\bare\\b|\\bmust be\\b|\\bshould be\\b)[ \\t]*(?!deferred|not |no |tbd|to be|none|n/a|out of scope)[\"']?[A-Za-z])[\\s\\S]*$", flags: "i" }
contains:
  - { path: "docs/eis/owner-approval-inbox/eis.md", all: ["## 7. Permissions and Capabilities", "## 8. State Models", "## 9. Entry Points and Discovery", "## 13. Interaction Scenarios", "## 18. UX Requirements for Design Handoff"] }
  - { path: "docs/eis/owner-approval-inbox/eis.md", any: ["denial", "deny", "Deny"] }
judge:
  artifact: "docs/eis/owner-approval-inbox/eis.md"
  threshold: 0.7
  criteria: |
    You are scoring an Experience Interaction Specification produced from a
    brief that contained BOTH real behavioural requirements AND a pile of
    unvalidated visual decisions (card grid three across, 16px semibold type,
    hex color #6B7280, green/red button pair, 8px spacing, a modal for the
    denial reason, white background, 24px gutter, Inter typeface, a bell icon).

    Score 1.0 ONLY if ALL of the following hold:
    (a) The document specifies NO visual design anywhere: no colors, no type
        sizes or weights, no spacing values, no typeface names, no icon
        choices, no "modal"/"card grid"/"left nav" prescribed as the solution.
    (b) The real behaviour from the brief IS specified: oldest-first ordering
        of pending work, a required reason on denial, visibility of imminent
        auto-escalation, prevention of two owners deciding the same request
        twice, and the requester-left-the-company case.
    (c) Where interface-level content appears, it appears ONLY in section 9
        (Entry Points and Discovery) or section 18 (UX Requirements for Design
        Handoff), and it is phrased as a CONSTRAINT ON design — e.g. "the
        decision action must be reachable without leaving the list" or "the
        reason must be captured before the denial is committed" — never as a
        design decision such as "use a modal" or "place the buttons bottom
        right".
    (d) The visual suggestions from the brief, if mentioned at all, are
        recorded as evaluated proposals or as deferred design decisions, not
        adopted as requirements.

    Score 0.5 if (a) holds but interface-layer content leaks into sections
    other than 9 and 18, or if (b) is only partly satisfied.

    Score 0.0 if any visual attribute from the brief survives as a
    specification statement.

    Be strict. The single most important property is that this document
    constrains design without doing design.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better,
      baseline: rolling_mean, tolerance: 0.1 }
```
