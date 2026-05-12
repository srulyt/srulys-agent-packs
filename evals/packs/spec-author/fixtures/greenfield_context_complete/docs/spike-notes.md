# Engineering spike notes — Workspace activity digest

We already publish a workspace event stream (issues, PRs, doc edits)
to an internal Kafka topic `workspace-events`. A daily digest
job can consume from this topic; no new datastore is needed.
Notifications team owns the in-app notification surface.

No new public API. No new auth flow. Single team delivery.
