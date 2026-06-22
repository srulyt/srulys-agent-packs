# Data Products MVP — scope overview

This document describes the scope of the Data Products MVP. It is a scope
proposal, not a specification, and it does not ask for a decision — the
team has already committed to building the MVP this half. The goal here is
only to make the in-scope and out-of-scope boundary clear to partner teams.

## What a Data Product is (in this MVP)

A Data Product is a publishable item that bundles one or more tables with
a description and an owner. A producer creates it, publishes it, and
consumers discover and read it. The MVP covers create, publish, discover,
and read. It does not cover versioning, lifecycle workflows, or approval
gates.

## Who is in scope

- **Producers**: data engineers who already own tables in the lakehouse
  and want to expose a curated subset to other teams.
- **Consumers**: analysts in adjacent teams who need read access to
  published products without filing access tickets per table.

Platform administrators and external/partner-org consumers are explicitly
out of scope for the MVP.
