---
name: deck-contracts
description: "Strict v3 schemas, handoff receipts, checksums, state, and publication contracts."
---

# Deck Contracts

Schemas in `schemas/v3/` are machine-authoritative. Use schema version `3.0`, reject undeclared fields, and validate before handoff. `deck-spec.json` is the sole model for both channels.

## Producer Preflight

Producers must read the relevant schema before writing. The Story Orchestrator
must choose `design_system_id` from `design-systems/registry.json`, never from a
scenario label. Narrative Strategist must locally self-check its ledger and
plan with `scripts/validate_contract.py` before handoff. Self-checking does not
replace the independent Composer receipt.

Evidence IDs, claim IDs, source IDs, and slide IDs are unique. Unsupported
claims have no evidence IDs, `unsupported: true`,
`allowed_use: "unsupported"`, and an explicit qualification. Supported claims
have evidence IDs, `unsupported: false`, and a non-unsupported allowed use.
Story-plan references must resolve to ledger IDs. `proposal.md` includes the
exact `decision_sought` and `one_sentence_thesis` values from the plan.

Each handoff requires an independent immutable receipt whose validator differs from producer. Persist both `validation_receipt_ids` and the matching `validation_receipts` index. Each index entry binds receipt ID, run, handoff, artifact kind/ID/checksum, producer, validator operation, predecessor event, active lineage, capability status, render manifest, and applicable approval/acceptance identity. The ID list and index keys must match exactly. A guarded transition must reject missing, unrelated, stale, superseded, operation-mismatched, capability-mismatched, or identity-mismatched envelopes before persistence. Changed inputs invalidate all dependent artifacts and receipts. Publication uses immutable versions plus an atomic state-backed current pointer.

## Boundaries
This skill provides domain knowledge only. It grants no workflow, state, publication, review-verdict, web-disclosure, or file-write authority. Follow the invoking agent's boundaries and the v3 schemas.
