---
name: spec-writer
description: "Write, update, or publish an EARS-style product/technical specification (PRD) using this team's template, gating rules, what-if coverage, and draft/publish lifecycle. Use for creating or revising specs and PRDs; not for general documents, code, or test plans."
user-invocable: true
---

# Spec writer

Produce a specification that implementers and reviewers can build and test against without asking "but what if…?". Follow the output contract in the [template](assets/spec-template.md).

## Invariants

- **Sections:** use the nine mandatory sections, verbatim and in order. Include a gated section only when its axis fires and `spec_kind` (`product` / `technical` / `mixed`) allows it. See [sections and gating](references/sections-and-gating.md).
- **Personas:** `Users & Personas` is the only persona table. Other sections reference personas by name.
- **Functional requirements:** each FR is one EARS shall-statement with a P0/P1/P2 priority and nested Given/When/Then criteria `AC-<FR>.<n>`. See [requirements writing](references/requirements-writing.md).
- **What-if coverage:** derive what can go wrong for every FR and journey step, even when the input never mentions it. Write each consequential case as a normal FR with negative ACs. When the right response is a business or policy decision, write `[TBD — reason]` plus an `OQ-NN` instead of guessing. See [what-if coverage](references/what-if-coverage.md).
- **No fabrication:** never invent evidence, data, quotes, personas, roles, or answers. Unknowns become `[TBD — reason]` with a matching Open Question.
- **Writing quality:** follow the voice, upper-section signal-density, Out-of-Scope adjacency, and citation rules in [writing quality](references/writing-quality.md).
- **Lifecycle:** new specs start at `Status: draft` / `Version: 0.0.1-draft`. Publishing happens only on explicit user instruction and changes only lifecycle bookkeeping, never requirement content. Published IDs are immutable. Updates are minimal edits. See [lifecycle](references/lifecycle.md).

## Working with the user

Close the gaps that block a useful spec before drafting, then draft directly. See [interviewing](references/interviewing.md). Ask where to save the spec if that isn't clear. When integrating review feedback, propose the changes before editing a spec.

## Done when

The spec passes the [quality checklist](references/quality-checklist.md) with no blockers. Every unknown appears as an Open Question. Tell the user the file path, status/version, number of FRs, and open questions that need owners.
