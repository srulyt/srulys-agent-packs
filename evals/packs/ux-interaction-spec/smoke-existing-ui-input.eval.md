---
name: ux-interaction-spec-smoke-existing-ui-input
target: ux-interaction-spec
kind: agent
tags: [pack, smoke, slow, judge]
timeout: 3600
---

# Notes about an existing screen become a product model, not a UI transcript

## Description

Exercises the `contains-existing-ui` input shape. The fixture describes a
shipped v1 screen: what it shows, what it conspicuously does **not** show, its
terminology drift ("Dataset" vs "data product", "Viewer/Editor" vs
`read`/`read-write`), and three known-wrong behaviours.

The failure mode this guards against is transcription — reproducing the
existing screen as the specification. The pack must instead read the UI for
what it implies about the product model, surface the absent states as gaps,
and reconcile the vocabulary. Structural assertions check the terminology
section and the edge-case section carry the reconciliation and the known
defects; the judge checks the specification models what is missing rather than
documenting what exists.

## Setup

```yaml
stage:
  agent: ux-interaction-spec
  include_skills: true
files:
  - copy: "fixtures/existing-ui-notes.md"
    dest: "inputs"
```

## Act

```prompt
Feature: Access request v2
Host product: Acme Data Cloud
Inputs: inputs/existing-ui-notes.md
Output dir: docs/eis/access-request-v2
Research mode: skipped
Interaction mode: non-interactive
On existing files: overwrite
Max review rounds: 1
Max specialist retries: 1

The input describes the screen we have today. We are replacing it. Produce the
interaction specification and deliver all three documents.
```

## Assert

```yaml
files:
  exists:
    - "docs/eis/access-request-v2/eis.md"
    - "docs/eis/access-request-v2/ux-pattern-research.md"
    - "docs/eis/access-request-v2/decision-log.md"
contains:
  - { path: "docs/eis/access-request-v2/eis.md", all: ["## 5. Conceptual Model", "## 6. Terminology", "## 8. State Models", "## 15. Error and Recovery Behavior", "## 16. Edge Cases", "## 20. Assumptions", "## 21. Open Questions"] }
  - { path: "docs/eis/access-request-v2/eis.md", any: ["data product", "Data product", "Data Product"] }
not_contains:
  - { path: "docs/eis/access-request-v2/eis.md", text: "<!-- EIS-PENDING" }
  - { path: "docs/eis/access-request-v2/eis.md", any: ["16px", "24px", "font-family", "typeface"], ignore_case: true }
matches:
  # Both of these were `section_contains` with a bare `max_chars` window. The
  # engine's `sectionBody` is /#+\s+<name>\s*\n([\s\S]{0,max_chars})/i - no
  # next-heading bound - so the window is a raw read-ahead from the heading and is
  # wrong in one of two directions: too small truncates the section, too large
  # spills into the sections that follow and passes on THEIR text. Section 8
  # measures 13,460 chars here against a 3,000 window (the needle landed at index
  # 2,066, so run 4 scanned 22% of the section); section 6 measures 2,774 against
  # 3,000, so it read 226 chars of section 7. The tempered token
  # (?:(?!\n##\s)[\s\S])*? stops at the next H2 - and only H2, since \s does not
  # match the third # of an H3 - so the scan is exactly the section, no window.
  - { name: "terminology section reconciles the existing screen's vocabulary", path: "docs/eis/access-request-v2/eis.md", pattern: "##\\s+6\\.\\s+Terminology(?:(?!\\n##\\s)[\\s\\S])*?(?:Dataset|Viewer|Editor)" }
  - { name: "state model carries the decided and expiry states the old screen lacked", path: "docs/eis/access-request-v2/eis.md", pattern: "##\\s+8\\.\\s+State Models(?:(?!\\n##\\s)[\\s\\S])*?\\b(?:denied|expire)", flags: "i" }
judge:
  artifact: "docs/eis/access-request-v2/eis.md"
  threshold: 0.7
  criteria: |
    You are scoring an Experience Interaction Specification produced from NOTES
    ABOUT AN EXISTING SCREEN that is being replaced. The notes described: a
    400-item unsearchable dropdown labelled "Dataset", an optional "Reason"
    field, a "Level" dropdown with Viewer/Editor, a Submit button with no
    confirmation, and a dead-end confirmation sentence. The notes also listed
    what the screen does NOT show (who decides, expected duration, the user's
    own requests, any state between submitted and granted, anything about
    expiry) and three known-wrong behaviours (double submit creates two
    requests, deleted dataset leaves an orphaned request, optional reason means
    owners approve blind).

    Score 1.0 ONLY if ALL of the following hold:
    (a) The document is a MODEL, not a transcript. It does not specify the
        existing screen's controls as requirements ("a dropdown labelled
        Dataset", "a Submit button").
    (b) The terminology section reconciles the drift: it states that the
        existing screen's "Dataset" corresponds to the catalog's "data
        product", and that "Viewer"/"Editor" correspond to read /
        read-write, and it picks a term to use going forward.
    (c) The state model includes the states the existing screen was missing —
        at minimum a decided/denied state and something about expiry — rather
        than only submitted and granted.
    (d) All three known-wrong behaviours are addressed as specified behaviour,
        an edge case, or an explicit open question: duplicate submission,
        resource deleted while a request is pending, and the consequence of an
        optional reason.
    (e) The absent information the notes call out (who decides, how long it
        takes, the user's own request history) appears somewhere as required
        behaviour or as an explicit gap — not silently dropped.

    Score 0.5 if the document models the product but misses two or more of
    (b)-(e).

    Score 0.0 if the document reads as documentation of the existing screen.

    Be strict. Reading a UI for what it implies about the product model is the
    skill being scored.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better,
      baseline: rolling_mean, tolerance: 0.1 }
```
