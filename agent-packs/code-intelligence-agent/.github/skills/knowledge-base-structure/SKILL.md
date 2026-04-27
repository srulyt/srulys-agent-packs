---
name: knowledge-base-structure
description: "Knowledge base template structure, section rules, dual-layer formatting, and quality lint rules for code intelligence output. Use when synthesizing findings into KB documents or validating KB output. Keywords: KB template, knowledge base, dual-layer, formatting, section structure."
---

# Knowledge Base Structure

Defines the opinionated KB template, section structure, formatting rules, and quality standards for Code Intelligence Agent output. This skill is the single source of truth for how knowledge bases are organized and formatted.

Used by `@kb-composer` (primary — applies template during synthesis) and `@cia-orchestrator` (for output validation).

## When to Use This Skill

Load this skill when:
- Synthesizing analytical findings into knowledge base documents
- Validating KB output for structural compliance
- Creating a new greenfield knowledge base
- Updating an existing knowledge base incrementally
- Checking KB quality against lint rules

## KB Directory Template

### Greenfield KB Structure

```
{kb-output-dir}/
├── README.md                       # KB overview, scope, generation metadata
├── architecture/
│   ├── system-overview.md          # High-level system architecture
│   ├── tech-stack.md               # Technologies, frameworks, dependencies
│   └── module-map.md               # Module purposes and boundaries
├── business-capabilities/
│   ├── {capability-name}.md        # One file per major business capability
│   └── ...
├── domain-model/
│   ├── entities.md                 # Core domain entities and relationships
│   └── glossary.md                 # Business term → technical term mapping
├── flows/
│   ├── {flow-name}.md              # End-to-end business flow documentation
│   └── ...
├── api-surface/
│   └── endpoints.md                # API endpoints mapped to business operations
├── authorization/
│   └── access-model.md             # Roles, permissions, enforcement points
├── events/
│   └── event-catalog.md            # Business events, telemetry, logging
└── _metadata/
    ├── generation-log.md           # When generated, from what query, confidence summary
    └── gaps.md                     # Known gaps and areas needing human validation
```

### Section Directory Rules

| Directory | Required | Contents |
|-----------|----------|----------|
| `architecture/` | Yes | Always generated — system structure context |
| `business-capabilities/` | Yes | Always generated — core purpose of the KB |
| `domain-model/` | Yes | Always generated — entity documentation |
| `flows/` | Conditional | Generated if business flows were identified |
| `api-surface/` | Conditional | Generated if API endpoints exist |
| `authorization/` | Conditional | Generated if access control patterns exist |
| `events/` | Conditional | Generated if business events exist |
| `_metadata/` | Yes | Always generated — provenance and gap tracking |

**Rule**: Required sections must always be created, even if data is sparse. Use `[INSUFFICIENT-DATA]` markers for sections where findings were incomplete. Conditional sections are only created when relevant findings exist.

## Section Structure Rules

### architecture/system-overview.md

**Purpose**: High-level picture of the system for someone who has never seen the code.

**Required Content**:
- What the system does (1-2 paragraph business description)
- Major components/services and how they interact
- Deployment topology if identifiable (monolith, microservices, serverless)
- Key integration points (external APIs, databases, message queues)

**Heading Structure**:
```markdown
# System Overview

## What This System Does
{Business-level description}

## Architecture Style
{Monolith / Microservices / Serverless / Hybrid}

## Major Components
### {Component Name}
{Purpose, key responsibilities}

## Integration Points
| System | Type | Purpose |
|--------|------|---------|
```

### architecture/tech-stack.md

**Purpose**: Technology inventory for architects and engineers.

**Required Content**:
- Programming languages with versions
- Frameworks and libraries with purposes
- Build tools and package managers
- Infrastructure and deployment tools
- Databases and data stores

### architecture/module-map.md

**Purpose**: Directory-to-purpose mapping for navigation.

**Required Content**:
- Every significant module/directory with its business purpose
- Dependencies between modules
- Architectural pattern per module (if identifiable)

### business-capabilities/{capability-name}.md

**Purpose**: Document a single major business capability in depth.

**Required Content**:
- Business-layer summary (PM-readable, no jargon)
- Technical implementation table
- Call paths for key operations
- Evidence table with confidence levels

**File Naming**: Use kebab-case business names: `user-registration.md`, `payment-processing.md`, `order-management.md`

### domain-model/entities.md

**Purpose**: Core domain entities, their properties, and relationships.

**Required Content**:
- Entity name and business purpose
- Key properties with business meaning
- Relationships between entities (with cardinality)
- Where each entity is defined (file reference)

### domain-model/glossary.md

**Purpose**: Bridge between business and technical vocabulary.

**Required Content**:
- Business term → technical term/location mapping
- Organized alphabetically
- Each entry cites where the term is implemented

**Format**:
```markdown
# Glossary

| Business Term | Technical Implementation | Location |
|---------------|------------------------|----------|
| Customer | `User` entity with `role = 'customer'` | `src/models/user.ts:User` |
| Shopping Cart | `CartService` + `CartItem` entity | `src/services/cart.ts` |
```

### flows/{flow-name}.md

**Purpose**: Document an end-to-end business process with full technical traceability.

**Required Content**:
- Business description of the flow (what triggers it, who uses it, what it achieves)
- Step-by-step technical trace with file:function references
- Authorization checkpoints within the flow
- Events emitted during the flow
- Error/exception paths

**File Naming**: Use kebab-case flow names: `user-registration-flow.md`, `order-checkout-flow.md`

### api-surface/endpoints.md

**Purpose**: Map every API endpoint to its business operation.

**Required Content**:
- HTTP method + path (or GraphQL operation, gRPC method)
- Business operation description
- Authorization requirements
- Request/response summary
- Handler function reference

**Format**:
```markdown
# API Surface

## {API Group Name}

| Method | Path | Business Operation | Auth Required | Handler |
|--------|------|--------------------|---------------|---------|
| POST | /api/users | Create user account | No | `src/controllers/user.ts:create` |
| GET | /api/users/:id | View user profile | User or Admin | `src/controllers/user.ts:getById` |
```

### authorization/access-model.md

**Purpose**: Document who can do what and how it's enforced.

**Required Content**:
- Authorization model type (RBAC, ABAC, ACL, custom)
- Roles/groups defined in the system
- Permissions per role
- Enforcement mechanism (middleware, decorators, manual checks)
- Enforcement points (which operations check authorization)

### events/event-catalog.md

**Purpose**: Catalog all business events the system emits.

**Required Content**:
- Event name and business meaning
- What triggers the event
- Event payload structure
- Known consumers/handlers
- Where the event is emitted (file reference)

**Format**:
```markdown
# Event Catalog

## {Event Category}

### {event.name}

**Business Meaning**: {what this event signifies}
**Trigger**: {what business action causes this event}
**Emitter**: `{file}:{function}` (L{line})
**Payload**: {key fields and their meaning}
**Consumers**: {known handlers or "unknown"}
```

### _metadata/generation-log.md

**Purpose**: Provenance tracking — when, how, and from what query.

**Format**:
```markdown
# Generation Log

## Run: {session-id}

| Field | Value |
|-------|-------|
| Generated | {ISO-8601 timestamp} |
| Mode | {greenfield / incremental} |
| Source Repository | {path or URL} |
| Query | {original user query} |
| Agent | Code Intelligence Agent v1.0 |

### Coverage Summary
{What was analyzed, what was skipped, and why}

### Confidence Distribution
| Level | Count | Percentage |
|-------|-------|------------|
| Explicit | {n} | {%} |
| High | {n} | {%} |
| Inferred | {n} | {%} |
```

### _metadata/gaps.md

**Purpose**: Honest accounting of what the KB does NOT cover.

**Required Content**:
- All `[GAP]` markers from findings
- All `[INCOMPLETE]` markers from iteration limits
- All `[DEPTH-LIMIT-REACHED]` markers from call tracing
- Recommendations for human follow-up

**Format**:
```markdown
# Known Gaps

## Unresolved Gaps

| Area | Gap Description | Reason | Recommendation |
|------|----------------|--------|----------------|
| {module} | {what is unknown} | {why — e.g., dynamic dispatch, no tests} | {suggested action} |

## Depth-Limited Traces

| Flow | Last Traced Point | Reason |
|------|------------------|--------|
| {flow name} | `{file}:{function}` | Call depth limit (5) reached |

## Incomplete Sections

| Section | Status | What's Missing |
|---------|--------|---------------|
| {section} | Partial | {description of missing content} |
```

## Dual-Layer Format Specification

Every content section in the KB MUST use a dual-layer format that serves both business and technical readers.

### Layer 1: Business Summary

The first content after the section heading. Written for PMs and architects. Rules:
- 2-4 sentences maximum
- No code references, no jargon
- Answer: What does this do? Who uses it? Why does it exist?
- Use present tense and active voice

### Layer 2: Technical Details

Follows the business summary. Written for engineers and AI agents. Includes:
- Implementation table (location, entry points, key functions, dependencies)
- Call paths with file:function:line references
- Evidence table with confidence levels

### Example

```markdown
## Order Cancellation

Customers can cancel orders before they are shipped. The cancellation process
reverses any pending payments, releases reserved inventory, and notifies the
fulfillment team. Only the order owner or an admin can cancel.

### Technical Implementation

| Aspect | Details |
|--------|---------|
| Primary Location | `src/orders/cancellation/` |
| Entry Points | `POST /api/orders/:id/cancel` |
| Key Functions | `OrderService.cancel()`, `PaymentService.reverse()`, `InventoryService.release()` |
| Dependencies | `OrderRepository`, `PaymentGateway`, `InventoryService`, `NotificationService` |

### Call Path

```
POST /api/orders/:id/cancel
  → OrderController.cancel (src/controllers/order.ts:89)
    → AuthMiddleware.requireOwnerOrAdmin (src/middleware/auth.ts:45)
    → OrderService.cancel (src/services/order.ts:234)
      → PaymentService.reverseCharge (src/services/payment.ts:112)
      → InventoryService.releaseReservation (src/services/inventory.ts:67)
      → NotificationService.send('order.cancelled') (src/services/notification.ts:23)
```

### Evidence

| Assertion | Confidence | Source |
|-----------|------------|--------|
| Only owner or admin can cancel | Explicit | `src/middleware/auth.ts:requireOwnerOrAdmin` L45, comment: "SEC-102" |
| Payment is reversed on cancellation | High | `src/services/order.ts:cancel()` L240, calls `reverseCharge()` |
| Inventory is released on cancellation | High | `src/services/order.ts:cancel()` L242, calls `releaseReservation()` |
| Fulfillment team is notified | Inferred | `src/services/order.ts:cancel()` L244, emits `order.cancelled` event *(inferred — no comment confirms recipient is fulfillment)* |
```

## Heading Hierarchy

Consistent heading usage across all KB files:

| Level | Usage | Example |
|-------|-------|---------|
| H1 (`#`) | File title — one per file | `# System Overview` |
| H2 (`##`) | Major sections / business concepts | `## Order Cancellation` |
| H3 (`###`) | Subsections / technical layers | `### Technical Implementation`, `### Call Path` |
| H4 (`####`) | Detail groups within subsections | `#### Error Handling`, `#### Edge Cases` |

**Rules**:
- Every file starts with exactly one H1
- Never skip heading levels (no H1 → H3)
- H2 headings are the primary navigation level within a file
- Use H3 `### Technical Implementation`, `### Call Path`, `### Evidence` consistently in capability files

## Greenfield vs. Incremental Output Rules

### Greenfield

- Generate the complete directory structure from template
- All required sections must be present
- Conditional sections created only when findings exist
- Fresh `_metadata/` with generation log and gaps

### Incremental

- Preserve existing KB directory structure and file organization
- Match existing tone, style, and formatting conventions
- Add new sections/files where needed (following template conventions)
- Update existing sections with new findings (preserve surrounding content)
- Append to `_metadata/generation-log.md` with new run entry
- Update `_metadata/gaps.md` — resolve addressed gaps, add new ones
- Produce a change summary documenting all modifications

### Incremental Update Format

For each changed section:
```markdown
### Update: {section-path}

**Action**: {insert | replace | append}
**Reason**: {why this section needs updating}

#### Content
{The updated content to insert/replace/append}
```

## Quality Lint Rules

Apply these checks to all KB output:

| Rule | Check | Severity |
|------|-------|----------|
| No orphan assertions | Every business claim has a code reference | Error |
| No empty sections | Every H2 section has content (or `[INSUFFICIENT-DATA]`) | Error |
| Consistent heading hierarchy | No skipped levels, one H1 per file | Error |
| Dual-layer format | Every capability section has business summary + technical details | Error |
| Traceability format | Code references use standard `file:function (L##-L##)` format | Warning |
| Cross-reference validity | Links to other KB files use correct relative paths | Warning |
| Confidence labels present | Evidence tables include confidence column | Error |
| No raw analyst notes | Output does not contain finding schema format directly | Error |
| Gaps collected | All gap markers collected in `_metadata/gaps.md` | Warning |
| Glossary populated | `domain-model/glossary.md` has at least 5 entries (or `[INSUFFICIENT-DATA]`) | Warning |

## Best Practices

1. **Business first, always**: Every section opens with the business summary before diving into technical details.
2. **Consistent file naming**: Use kebab-case for all file names: `user-registration.md`, not `UserRegistration.md`.
3. **One capability per file**: Don't combine unrelated capabilities. Split into separate files for clarity and maintainability.
4. **Cross-reference generously**: Link between related capabilities, flows, and entities using relative markdown links.
5. **Metadata is not optional**: Always generate `_metadata/` files — they are the KB's self-awareness layer.
6. **Gaps are features**: A well-documented gap is more valuable than a fabricated section. Always include `gaps.md`.

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Single monolithic KB file | Hard to navigate, impossible to update incrementally | Use directory structure with one concept per file |
| Technical-only documentation | Excludes business stakeholders | Always include business-layer summaries |
| Orphan assertions | Business claims without code proof | Apply traceability lint rule |
| Inconsistent formatting | Erodes trust and usability | Follow heading hierarchy and dual-layer format strictly |
| Empty conditional sections | Clutters KB with noise | Only create conditional sections when findings exist |
| Stale gaps file | Users don't know what's been resolved | Update gaps.md with every incremental run |

## Quality Checklist

- [ ] KB directory follows the template structure
- [ ] All required sections are present
- [ ] Every business capability file uses dual-layer format
- [ ] All evidence tables include confidence levels
- [ ] No orphan assertions (every claim has code reference)
- [ ] Heading hierarchy is consistent (H1 → H2 → H3 → H4)
- [ ] File names use kebab-case
- [ ] `_metadata/generation-log.md` includes run provenance
- [ ] `_metadata/gaps.md` collects all gap markers
- [ ] Glossary maps business terms to technical implementations
- [ ] Cross-references between files use valid relative paths
- [ ] No raw analyst notes appear in output
