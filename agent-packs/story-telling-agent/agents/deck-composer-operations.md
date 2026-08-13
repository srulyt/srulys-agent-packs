# Deck Composer Operations

All commands use explicit absolute or repository-root-resolved paths and no network.

1. **Validate**: invoke `scripts/validate_contract.py`. Persist immutable receipts with exclusive creation. Invalid producer input still returns a valid receipt with `diagnostic_class=producer-artifact-invalid`; tool/runtime failure uses `validator-internal-error`.
2. **Compose**: preflight capabilities; map approved plan to one `deck-spec.json`; validate it; run `render_deck.py`. Never use undeclared fallback fields.
3. **Render**: both sibling projections consume the same parsed model and seed. Record tool/font versions, substitutions, checksums, semantic hashes, and channel status.
4. **Preflight publication**: resolve the destination only from `state.publication_destination.effective_output_dir` and its immutable `effective_destination_event_id`, both bound to the validated `intake_sha256`; reject prompt/state/event mismatch. Run `publish_artifacts.py --preflight`; inspect only requested names. Return destination, destination event ID, names, status, collisions, metadata fingerprint, timestamp, and policy.
5. **Publish**: resolve and re-check the same state/event-backed effective destination and collision metadata; validate QA and accepted event; copy pinned files to a same-filesystem temporary version directory, fsync where supported, checksum, rename to immutable `versions/<publication-id>`, then atomically replace `current.json`. Journal intent/commit/rollback. A destination change creates a new immutable destination-selection event and invalidates preflight/publication controls only; changed intake/manifest/QA invalidates publication and requires downstream revalidation.
