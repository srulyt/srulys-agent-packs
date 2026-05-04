@spec-author write a PRD for **Workspace activity digest** — a daily
summary of changes in a product workspace, delivered to each member
via in-app notification.

This is a **product** spec (not a design doc). When you ask me at
Stop 0 I will reply with `output_path: docs/specs/digest.md,
spec_kind: product`.

Some framing the team has been using internally — please translate
this into product-shape behaviour (do NOT echo the implementation
nouns into FRs):

- We plan to source events from the existing **Kafka** event-stream
  and persist digest snapshots in **Postgres**. We may also use
  **Redis** for de-duplication. **MongoDB** is on the table for
  long-term archival.
- Personas: PM and Engineering Manager (file at `docs/personas.md`).

The PRD must describe externally observable behaviour only:
freshness, delivery cadence, content, opt-out, etc. Implementation
nouns (datastore choices, message-bus choices, framework choices)
must not appear in FRs or ACs. They belong in engineering design,
not in this PRD.

When you propose the section set at Stop A, I will reply `APPROVE`
on the first ask.
