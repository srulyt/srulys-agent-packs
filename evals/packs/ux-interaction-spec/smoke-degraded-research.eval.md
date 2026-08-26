---
name: ux-interaction-spec-smoke-degraded-research
target: ux-interaction-spec
kind: agent
tags: [pack, smoke, slow, judge]
timeout: 3600
---

# Degraded research grounds what it can and names what it cannot

## Description

The only spec in the suite that exercises a research mode other than `skipped`,
and the only one where Document 2 carries real content. It runs offline: the
fixture *is* the evidence, so `degraded` mode is reachable deterministically
with no network call.

The bundle supplies substantial first-party host-product material — a dated help
centre article, an internal design-system pattern page, a platform engineering
memo with hard numerical limits, and a support-ticket theme report — and
explicitly states that no competitor and no adjacent-domain material could be
obtained. That asymmetry is the point. The researcher must ground host-product
findings in the supplied sources with attribution and dates, and must record the
competitor and adjacent areas as *named, categorised* unverifiable gaps rather
than quietly writing nothing, inventing plausible competitor behaviour, or
downgrading the whole run to a stub.

This is the path that exercises the evidence-labelling contract, the source
hierarchy, pattern verdicts, the precedent matrix with real rows, the critic's
research-verification checks against non-empty input, and — because coverage is
asymmetric — the definition-of-done points that become `n/a`-eligible for one
research area while remaining scored for another. In `skipped` mode all of that
is vacuous.

The hard numbers in the memo (25 grants per request, no rollback, partial
success with no undo) also give the specification a real constraint to model,
so the judge can tell grounded specification from confident prose.

## Setup

```yaml
stage:
  agent: ux-interaction-spec
  include_skills: true
files:
  - copy: "fixtures/host-product-docs.md"
    dest: "inputs"
```

## Act

```prompt
Feature: Bulk approvals for access requests
Host product: Acme Data Cloud
Inputs: inputs/host-product-docs.md
Output dir: docs/eis/bulk-approvals
Research mode: degraded
Interaction mode: non-interactive
On existing files: overwrite
Max review rounds: 1
Max specialist retries: 1

This environment has no network access. The attached bundle is the only
material available: it covers our own product in depth and states plainly that
comparable products and adjacent domains could not be obtained. Work from what
is there. Produce the interaction specification and deliver all three documents.
```

## Assert

```yaml
files:
  exists:
    - "docs/eis/bulk-approvals/eis.md"
    - "docs/eis/bulk-approvals/ux-pattern-research.md"
    - "docs/eis/bulk-approvals/decision-log.md"
contains:
  - { path: "docs/eis/bulk-approvals/eis.md", all: ["## 4. Actors and Roles", "## 8. State Models", "## 15. Error and Recovery Behavior", "## 16. Edge Cases", "## 20. Assumptions", "## 21. Open Questions", "## 22. Requirements Traceability"] }
  - { path: "docs/eis/bulk-approvals/ux-pattern-research.md", all: ["## 1. Research Objective", "## 2. Host Product Analysis", "## 3. Competitive Products", "## 4. Adjacent Patterns", "## 9. Implications for the EIS", "## 10. Sources"] }
  - { path: "docs/eis/bulk-approvals/decision-log.md", all: ["## Assumptions", "## Contradictions / Risks"] }
not_contains:
  - { path: "docs/eis/bulk-approvals/eis.md", text: "<!-- EIS-PENDING" }
  - { path: "docs/eis/bulk-approvals/ux-pattern-research.md", text: "<!-- EIS-PENDING" }
matches:
  # research ran: the mode is declared as degraded, not skipped
  - { path: "docs/eis/bulk-approvals/ux-pattern-research.md", pattern: "research_mode:\\s*degraded" }
  # unverifiable areas are named as categorised gap records, not left blank
  - { path: "docs/eis/bulk-approvals/ux-pattern-research.md", pattern: "EV-GAP-[0-9]{3}" }
  # host-product findings are grounded in supplied evidence records
  - { path: "docs/eis/bulk-approvals/ux-pattern-research.md", pattern: "EV-RS-[0-9]{3}" }
  # at least one pattern reached a recorded verdict
  # NOTE: JavaScript RegExp has no inline-flag syntax; "(?i)..." is a COMPILE
  # ERROR and fails the check unconditionally. Case-insensitivity goes in `flags`.
  - { path: "docs/eis/bulk-approvals/ux-pattern-research.md", pattern: "(adopt|adapt|reject|context-only)", flags: "i" }
  - { path: "docs/eis/bulk-approvals/eis.md", pattern: "Q-(IN|RS|MD)-[0-9]{3}" }
  # The four assertions below were `section_contains` / `section_not_contains`
  # with bare `max_chars` windows. Measured against the run-4 corpus the windows
  # were badly wrong in the SPILL direction, which is the silent one: section 2
  # is 2,831 chars and the window read 8,000 (5,169 chars of sections 3+), and
  # section 3 is 146 chars while the window read 7,190 - 98% of what the
  # "competitive products section" check scanned was not that section. The
  # tempered token (?:(?!\n##\s)[\s\S])*? bounds each scan at the next H2.
  # `:104` and the two `## 10.` identifier checks below were narrowed in round 9.
  #
  # The old `:104` alternation ended `|Help Centre|Design System` — source-type
  # DESCRIPTIONS, and precisely what the round-8 citation contract reclassifies
  # as unsourced. `Help Centre` also appears verbatim in the pack's own worked
  # example, so the assertion could be satisfied by a document that had not read
  # the bundle at all. A green `:104` would then have been no evidence that the
  # contract was met, on the one defect this round exists to fix. Narrowing had
  # to happen BEFORE the run that measures it: an assertion satisfiable by the
  # paraphrase we just banned measures nothing, and a true negative is worth
  # more than an uninformative pass.
  #
  # Membership rule for these alternations: **every member is a token the
  # supplied material writes about ITSELF, and none can be produced by
  # describing the source.** `help.acme.example`, `ds.acme.internal` and
  # `PLAT-2026-114` are unguessable; `Approving an access request` and
  # `top themes Q1 2026` are exact titles; `Acme Design System` is the system's
  # actual name, where bare `Design System` was a generic type. Six members
  # spanning all four identified sources and both citation styles (URL, or
  # title-plus-publication) — the contract accepts either, so requiring a URL
  # alone would fail a correct citation.
  #
  # `## 10.` gets the same treatment as a sibling of the same defect class: the
  # old check needed only the string `2026` anywhere in Sources, which any date
  # satisfies. The contract makes RES-§10 carry the identifiers, so this is
  # where they are most explicitly owed. The two required sources are the two
  # that are certainly used — the memo, whose 25-operation limit is load-bearing
  # for judge criterion (d) and asserted at the EIS end, and the help-centre
  # article, which is the document's subject. Neither is a guess about what the
  # author might choose to cite.
  - { name: "sources section cites the supplied material with retrieval dates", path: "docs/eis/bulk-approvals/ux-pattern-research.md", pattern: "##\\s+10\\.\\s+Sources(?:(?!\\n##\\s)[\\s\\S])*?2026" }
  - { name: "sources section identifies the engineering memo by its own identifier", path: "docs/eis/bulk-approvals/ux-pattern-research.md", pattern: "##\\s+10\\.\\s+Sources(?:(?!\\n##\\s)[\\s\\S])*?PLAT-2026-114" }
  - { name: "sources section identifies the help centre article by its own identifier", path: "docs/eis/bulk-approvals/ux-pattern-research.md", pattern: "##\\s+10\\.\\s+Sources(?:(?!\\n##\\s)[\\s\\S])*?(?:help\\.acme\\.example|Approving an access request)" }
  - { name: "host product analysis cites a supplied source by its own identifier, not by description", path: "docs/eis/bulk-approvals/ux-pattern-research.md", pattern: "##\\s+2\\.\\s+Host Product Analysis(?:(?!\\n##\\s)[\\s\\S])*?(?:help\\.acme\\.example|ds\\.acme\\.internal|PLAT-2026-114|Approving an access request|top themes Q1 2026|Acme Design System)" }
  - { name: "the 25-grant limit reaches the specification", path: "docs/eis/bulk-approvals/eis.md", pattern: "##\\s+16\\.\\s+Edge Cases(?:(?!\\n##\\s)[\\s\\S])*?(?:25|partial)", flags: "i" }
  # The negative is deliberately NOT re-scoped to section 3. Bounding it there
  # would shrink the scan from 7,190 chars to 146 and quietly LOSE coverage while
  # claiming to strengthen the check. The bundle states no competitor material was
  # obtainable, so naming one of these anywhere in the research document is
  # fabrication - judge criterion (a) scores it 0.0. Document-wide is both the
  # honest scope and strictly stronger than the window it replaces.
  #
  # Two false-positive modes had to be closed before that scope was safe:
  #
  # (1) Judge criterion (a) requires gaps be "recorded as explicitly unverifiable
  #     - each naming what would have been checked". A gap record that names its
  #     intended competitor targets is therefore judge-COMPLIANT, and a bare
  #     document-wide needle would fail the very behaviour the judge rewards.
  #     The lookbehind exempts a name that appears within 160 chars after gap /
  #     deferral / could-not language, so "we would have checked Sailpoint" passes
  #     while "Sailpoint uses a batch approval tray" fails.
  # (2) "Okta" was REMOVED from the list. `competitor-and-adjacent.md` - a skill
  #     the researcher loads - uses "### Okta" as its canonical RES-section-3
  #     worked example, so a researcher echoing the pack's own example tripped a
  #     case-insensitive document-wide needle. Keeping it would have made the
  #     pack's own teaching material a test failure.
  - { name: "no invented competitor is named anywhere in the research document", path: "docs/eis/bulk-approvals/ux-pattern-research.md", pattern: "^(?![\\s\\S]*(?<!(?:gap|unverifiable|unavailable|not obtainable|could not|would have|deferred|no competitor|absent|explicitly not)[\\s\\S]{0,160})\\b(?:Sailpoint|Saviynt|BetterCloud|Torii)\\b)[\\s\\S]*$", flags: "i" }
judge:
  artifact: "docs/eis/bulk-approvals/ux-pattern-research.md"
  threshold: 0.7
  criteria: |
    You are scoring a UX pattern research document produced in DEGRADED research
    mode with no network access. The only material available was a bundle of
    first-party host-product sources: a help centre article dated 2025-11-04, an
    internal design-system page (version 4.2, updated 2026-02-17) describing
    table selection and bulk-action patterns including partial-failure reporting,
    a platform engineering memo PLAT-2026-114 dated 2026-05-30 stating a hard
    limit of 25 grant operations per request with no transactional rollback, and
    a support report (n = 312) on approver complaints. The bundle states
    explicitly that NO competitor material and NO adjacent-domain material could
    be obtained.

    Score 1.0 ONLY if ALL of the following hold:

    (a) ASYMMETRY IS HONOURED. Host-product findings under section 2 (Host
        Product Analysis) are substantive and attributed to the specific
        supplied sources. Section 3 (Competitive Products) and section 4
        (Adjacent Patterns) are recorded as explicitly unverifiable — each
        naming what would have been checked and carrying a gap identifier — and
        are NOT filled with plausible-sounding claims about how other products
        behave. Inventing a competitor behaviour, or citing a source that is not
        in the bundle, scores 0.0 regardless of everything else.

    (b) EVIDENCE IS LABELLED, NOT ASSERTED. Claims drawn from the bundle are
        distinguishable from the author's inference. Dates and source identity
        are carried through rather than dropped. A reader can tell which
        statements are observed and which are reasoned.

        Source identity means the source's OWN stated identifier reproduced
        verbatim — its title, publication or system name, URL, or memo/version
        number, as the material writes them. A description of the source ("the
        product's current approval documentation", "an internal engineering
        note") is NOT source identity, however accurate: it cannot be looked
        up, and it cannot distinguish two documents about the same topic. The
        supplied bundle's filename and section number are a LOCATOR, telling a
        reader where the author found the material; they do not say what it is,
        and a body section in which every claim carries the same bundle
        filename has dropped source identity rather than carried it. Internal
        `EV-RS-###` ledger ids are expected and correct, but they are pointers
        into a ledger the reader has not seen and do not substitute for the
        identifier either. Deduct for identity carried only as a description,
        a bundle locator, or a bare ledger id.

    (c) THE PRECEDENT MATRIX IS HONEST. Where a row's precedent could not be
        verified it is marked unverified and its recommendation is demoted to an
        assumption for the specification author. It does not present an
        unverified row as an established precedent.

    (d) THE HARD CONSTRAINTS SURVIVE. The 25-operations-per-request limit, the
        absence of rollback, and the requirement to report partial success per
        row are all carried into the research implications rather than being
        lost between the memo and the specification.

    (e) THE DOCUMENT IS NOT A STUB. Because host-product research WAS possible,
        this must not read as a "research not performed" document. Section 2
        (Host Product Analysis) — which is where host-product content lives in
        this document's contract — and section 9 (Implications for the EIS)
        must both carry real, specific content derived from the bundle. Do NOT
        expect substantive content in section 3 (Competitive Products) or
        section 4 (Adjacent Patterns): the bundle makes those genuinely
        unverifiable, and a declared gap there is the correct answer, not a
        shortfall.

    Score 0.5 if (a) holds but the document is thin — for example, gaps are
    named correctly but the host-product findings restate the bundle rather than
    drawing implications from it.

    Score 0.0 if any competitor or adjacent-domain claim is fabricated, if a
    source not present in the bundle is cited, or if the whole document degrades
    to stub form despite substantial host-product material being available.

    Be strict. The specific failure this scores against is a model filling an
    evidential vacuum with confident prose.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better,
      baseline: rolling_mean, tolerance: 0.1 }
```
