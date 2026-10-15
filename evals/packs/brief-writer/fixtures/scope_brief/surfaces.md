# Surfaces and in/out-of-scope boundaries

## Create surface (in scope)

A producer selects existing tables, adds a name, description, and owner,
and saves a draft Data Product. Reuses the existing item-creation model;
no new permission primitive is introduced.

## Publish surface (in scope)

A single publish action makes a draft discoverable to consumers in the
same org. No staged review, no approval workflow.

## Discover and read surface (in scope)

Consumers browse published products in the catalog and open one to read
its tables. Access inherits from the existing identity model — no
per-table grant step.

## Out of scope for the MVP

- Versioning and change history for a published product.
- Deprecation / retirement lifecycle.
- Approval or governance workflows before publish.
- Cross-org / external-partner sharing.
- Usage analytics and consumption metering.

These are not yet decided and are intentionally deferred; they are listed
so partner teams know what the MVP does and does not deliver.
