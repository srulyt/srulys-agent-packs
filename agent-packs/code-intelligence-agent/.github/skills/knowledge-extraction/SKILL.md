---
name: knowledge-extraction
description: "Rules for structuring code analysis findings with traceability, confidence labeling, and incremental update protocols. Use when producing or consuming structured knowledge findings. Keywords: finding schema, traceability, confidence, incremental update, evidence."
---

# Knowledge Extraction

Rules for structuring analytical findings from code analysis into a consistent, traceable format. This skill is the single source of truth for finding schemas, confidence labeling, traceability requirements, and incremental update protocols.

Shared by `@domain-analyst` (producing findings) and `@kb-composer` (consuming findings).

## When to Use This Skill

Load this skill when:
- Producing structured findings from code analysis
- Consuming and synthesizing findings into knowledge base content
- Validating that findings meet traceability requirements
- Performing incremental updates to an existing knowledge base
- Handling contradictions between code and documentation

## Core Concepts

### The Finding

A **finding** is the atomic unit of extracted knowledge. Every piece of business or technical knowledge extracted from code must be expressed as a finding that follows the schema defined below.

### Traceability

**Traceability** means every business assertion in the knowledge base can be traced back to specific code locations. This is not optional — untraceable assertions have no value and must be flagged as gaps.

### Confidence

**Confidence** represents how certain the analyst is about a finding's accuracy. It is always one of three levels: Explicit, High, or Inferred. The level determines how the finding is presented in the final knowledge base.

## Finding Entry Schema

Every finding MUST include these fields:

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| **Assertion** | Yes | String | A business-level statement about what the code does. Written in plain language. |
| **Confidence** | Yes | Enum | `Explicit`, `High`, or `Inferred` — see calibration rules below. |
| **Evidence** | Yes | Reference[] | One or more code locations: file path, function/class name, line range. |
| **Call Path** | Conditional | Path[] | Invocation chain from entry point to implementation. Required when the finding involves a business flow or multi-step operation. |
| **Category** | Recommended | Enum | `business-rule`, `authorization`, `event`, `entity`, `flow`, `api-mapping`, `convention` |
| **Tags** | Optional | String[] | Domain-specific tags for grouping (e.g., `payments`, `auth`, `onboarding`) |

### Finding Format (Markdown)

```markdown
- **Assertion**: {plain-language business statement}
  - **Confidence**: {Explicit | High | Inferred}
  - **Evidence**: `{file_path}:{function_or_class}` (L{start}-L{end})
  - **Call Path** (if applicable):
    ```
    {entry_point} ({file}:{line})
      → {step_2} ({file}:{line})
        → {step_3} ({file}:{line})
    ```
  - **Category**: {category}
  - **Tags**: {tag1}, {tag2}
```

### Evidence Reference Format

Standard formats for code references:

| Context | Format | Example |
|---------|--------|---------|
| **Inline** | `→ path/file.ext:FunctionName (L##-L##)` | `→ src/auth/rbac.ts:checkPermission (L42-L67)` |
| **Table cell** | `path/file.ext:FunctionName` + line range | `src/auth/rbac.ts:checkPermission` (L42-L67) |
| **Call path step** | Indented `→` with file:line | `→ RBACService.evaluate (src/auth/rbac.ts:112)` |

**Rules**:
- Always use forward slashes in paths (even on Windows) for KB portability
- Include function/method name when identifiable
- Include line range when possible — at minimum the start line
- When referencing a class, use `file:ClassName` format
- When referencing a module, use `file` without function qualifier

## Confidence Labeling Rules

### Explicit

The finding is directly confirmed by human-written documentation in the codebase:
- Code comments or docstrings that state the business intent
- README or documentation files that describe the capability
- Test names or descriptions that state expected business behavior
- OpenAPI/Swagger annotations with business descriptions
- Inline `// BUSINESS RULE:` or similar explicit markers

**When producing**: Quote or closely paraphrase the confirming source.
**When consuming**: Present without qualification — this is a stated fact.

### High

The finding is strongly supported by code structure but not explicitly documented:
- Function/class names that clearly encode business meaning (e.g., `calculateShippingDiscount`)
- Enum values that represent business states (e.g., `OrderStatus.CANCELLED`)
- Middleware/decorator names that declare intent (e.g., `@RequireRole('admin')`)
- Error types named after business scenarios (e.g., `InsufficientBalanceError`)
- Configuration keys with business-meaningful names

**When producing**: Cite the structural evidence and explain why it supports the assertion.
**When consuming**: Present as factual but note the structural basis.

### Inferred

The finding is the analyst's interpretation of code behavior:
- A function checks `user.subscriptionTier` before applying a discount — inferred as tiered pricing logic
- A queue consumer processes items in a specific order — inferred as priority-based processing
- Multiple services call the same validation function — inferred as a shared business rule

**When producing**: State the interpretation and the code behavior that led to it. Use phrases like *(inferred from naming convention)*, *(inferred from call pattern)*, *(inferred from structural analysis)*.
**When consuming**: Present with explicit `(inferred)` label and the reasoning.

## No-Fabrication Rule

**CRITICAL**: Never create a finding without code evidence.

If you cannot determine the business meaning of a code element:
1. Do NOT guess or infer loosely
2. Record it as a gap finding
3. Use this format:

```markdown
- **Assertion**: [GAP] Purpose of `{function/class}` in `{file}` unclear
  - **Confidence**: N/A
  - **Evidence**: `{file}:{function}` (L{start}-L{end})
  - **Note**: {What you can see in the code and why business intent cannot be determined}
```

Gaps are valuable — they tell the knowledge base consumer where human expertise is needed.

## Incremental Update Protocol

When updating an existing knowledge base, findings must be tagged with their update status:

### Finding Status Tags

| Tag | Meaning | Usage |
|-----|---------|-------|
| `[NEW]` | Finding not present in existing KB | New discovery from this analysis run |
| `[UPDATED]` | Finding modifies an existing KB entry | Evidence changed, confidence changed, or assertion refined |
| `[CONTRADICTS-EXISTING]` | Finding conflicts with existing KB | Code behavior differs from what KB states |
| `[DEPRECATED]` | Finding should remove existing KB entry | Code referenced by existing KB has been deleted or fundamentally changed |
| `[CONFIRMED]` | Finding matches existing KB exactly | Validates that existing documentation is still accurate |

### Incremental Update Rules

1. **Preserve existing structure**: When updating, match the existing KB's section organization, tone, and formatting
2. **Additive by default**: Add new findings to appropriate sections without removing existing content unless explicitly contradicted
3. **Change tracking**: Every incremental update must produce a change summary listing what was added, modified, or removed and why
4. **No silent removals**: Never remove existing KB content without a `[DEPRECATED]` tag and explanation
5. **Conflict resolution**: When `[CONTRADICTS-EXISTING]` is used, present both the existing KB content and the new finding, letting the KB consumer decide

## Contradiction Handling

When code and documentation disagree:

### Step 1: Identify the Contradiction
```markdown
- **Assertion**: [CONTRADICTION] Documentation says X, but code implements Y
  - **Confidence**: High (code behavior) vs. Explicit (documentation)
  - **Code Evidence**: `{file}:{function}` (L{start}-L{end}) — implements Y
  - **Doc Evidence**: `{doc_file}` — states X
  - **Note**: {Explain the specific discrepancy}
```

### Step 2: Present Both Sides
- Include the documentation-based assertion as `Explicit` confidence
- Include the code-based assertion as `High` confidence
- Let the KB reader resolve — they may know which is outdated

### Step 3: Recommend Resolution
- If the code is clearly newer (recent commits), lean toward code truth
- If documentation has been recently updated, note this
- Always recommend human verification for contradictions

## Patterns

### Pattern 1: Business Capability Finding

**Use when**: Documenting a major business capability.

```markdown
## User Registration

- **Assertion**: The system supports self-service user registration with email verification
  - **Confidence**: High
  - **Evidence**: `src/auth/register.ts:registerUser` (L15-L45)
  - **Call Path**:
    ```
    POST /api/auth/register (src/routes/auth.ts:22)
      → AuthController.register (src/controllers/auth.ts:34)
        → UserService.createUser (src/services/user.ts:67)
          → EmailService.sendVerification (src/services/email.ts:12)
    ```
  - **Category**: flow
  - **Tags**: auth, onboarding
```

### Pattern 2: Authorization Finding

**Use when**: Documenting access control rules.

```markdown
- **Assertion**: Only users with 'admin' role can delete other user accounts
  - **Confidence**: Explicit
  - **Evidence**: `src/middleware/auth.ts:requireRole('admin')` (L23), `src/controllers/user.ts:deleteUser` (L89-L105)
  - **Note**: Comment at L89 states: "Admin-only operation per security policy SEC-201"
  - **Category**: authorization
  - **Tags**: auth, admin, user-management
```

### Pattern 3: Gap Finding

**Use when**: Cannot determine business meaning.

```markdown
- **Assertion**: [GAP] Business purpose of `reconcileAccounts()` unclear
  - **Confidence**: N/A
  - **Evidence**: `src/jobs/reconciler.ts:reconcileAccounts` (L1-L150)
  - **Note**: Complex function that queries multiple database tables and produces a report, but no comments or tests explain the business context. Called by a daily cron job. Recommend review by finance team.
  - **Category**: business-rule
  - **Tags**: finance, reconciliation
```

## Best Practices

1. **One assertion per finding**: Each finding should make one clear business statement. Complex capabilities should be broken into multiple findings.
2. **Evidence before interpretation**: Always read the code evidence thoroughly before forming an assertion. Do not fit evidence to a preconceived narrative.
3. **Include negative findings**: If you looked for something (e.g., authorization on an endpoint) and it wasn't there, that's a finding too — document the absence.
4. **Use consistent terminology**: Once you name a business concept (e.g., "subscription tier"), use that exact term consistently across all findings.
5. **Link related findings**: Use tags and cross-references to connect findings that form a larger business narrative.
6. **Prefer specificity**: `"Admin role bypasses the 3-attempt rate limit on login"` is better than `"Admin has special login privileges"`.

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Findings without evidence | Untraceable, unverifiable claims | Every finding must have at least one code reference |
| Over-confident labeling | Calling interpretations "Explicit" | Apply calibration rules strictly — when in doubt, downgrade |
| Fabricating to fill gaps | Creating false knowledge | Use `[GAP]` markers for uncertain areas |
| Copy-pasting code as evidence | Bloated findings, hard to read | Reference file:function:line, don't embed code blocks |
| Mixing business and technical language in assertions | Confuses non-technical readers | Assertions should be business-level; technical details go in evidence |
| Ignoring contradictions | Silently using one source over another | Always document contradictions with both sides |

## Quality Checklist

- [ ] Every finding has all required fields (Assertion, Confidence, Evidence)
- [ ] Confidence labels follow calibration rules strictly
- [ ] No assertions exist without code evidence references
- [ ] Evidence references use the standard format (file:function:line)
- [ ] Gaps are flagged with `[GAP]` markers, not filled with assumptions
- [ ] Inferred findings include reasoning explanation
- [ ] Contradictions documented with both perspectives
- [ ] Incremental findings tagged with status (`[NEW]`, `[UPDATED]`, etc.)
- [ ] Consistent terminology used across all findings
- [ ] No raw code blocks embedded in findings (use references instead)
