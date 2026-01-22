# Synthesis Index Guide for Agent Outputs

## Purpose

To prevent context overflow when the spec-formatter consolidates agent outputs, all specialist agents that produce detailed content MUST include a **Synthesis Index** at the top of their output files.

## What is a Synthesis Index?

A synthesis index is a structured summary section at the beginning of each agent output file that provides:
1. **Overview statistics** (count of items, categories, priorities)
2. **Summary tables** with key information for the final spec
3. **Section anchors** pointing to detailed content below
4. **Processing guidance** indicating which sections need full detail vs. summary-only treatment
5. **Cross-references** to related content or dependencies

## Why Synthesis Indexes?

- **Prevents context overflow**: Spec-formatter reads indexes first (small), then selectively reads details
- **Efficient processing**: Formatter can build spec structure from indexes alone for many sections
- **Selective detail reads**: Only sections needing full detail are read from complete files
- **Maintains quality**: All detail is preserved; formatter decides what to include in final spec

## Which Agents Need Synthesis Indexes?

**Required for agents producing detailed outputs:**
- Requirements Miner (functional requirements)
- NFR & Quality Guru (non-functional requirements)
- Test Sage (acceptance criteria, test scenarios)
- Metrics Master (goals, success metrics)
- Domain Detective (if producing detailed market analysis)

**Not required for:**
- Best Practices Buddy (produces recommendations, not content)
- Spec Reviewer (produces feedback, not content)

## Standard Synthesis Index Structure

```markdown
## Synthesis Index

### [Content Type] Overview
- **Total [Items]:** [N] ([X] P0, [Y] P1, [Z] P2)
- **Categories:** [List main categories]
- **File Structure:** [Single file or multiple parts]
- **Special Notes:** [Any important context]

### [Content Type] Summary Table
| ID | Priority | Category | Summary | Detail Section |
|----|----------|----------|---------|----------------|
| [ID] | [P0/P1/P2] | [Category] | [One-line summary] | [#anchor-link] |

### Processing Guidance for Spec Formatter
- **Summary sufficient for:** [List IDs that don't need detail reads]
- **Detail read required for:** [List IDs needing full content]
- **Related groups:** [IDs that should be read together]

### Cross-References
- [Reference to dependencies or related content]
- [Reference to phase/version dependencies]

---

## Detailed [Content Type]

[Full detailed content follows with proper section anchors...]
```

## Agent-Specific Guidelines

### Requirements Miner

```markdown
## Synthesis Index

### Requirements Overview
- **Total Requirements:** 25 (12 P0, 10 P1, 3 P2)
- **Categories:** Data Ingestion, Data Processing, Insights, Actions
- **File Structure:** Multiple files (see below)

### Requirements Summary Table
| Req ID | Priority | Category | Description | Detail Section |
|--------|----------|----------|-------------|----------------|
| FR-001 | P0 | Data Ingestion | System shall ingest OneLake API logs | #fr-001-onelake-api-log-ingestion |

### Processing Guidance for Spec Formatter
- **Summary sufficient for:** FR-005, FR-010, FR-015 (standard patterns)
- **Detail read required for:** FR-001, FR-002 (complex data elements)

### Cross-References
- FR-002 depends on FR-001
- FR-101-105 form OneLake Diagnostics group
```

### NFR & Quality Guru

```markdown
## Synthesis Index

### NFR Overview
- **Total NFRs:** 8 (4 P0, 3 P1, 1 P2)
- **Categories:** Performance, Scalability, Compliance
- **Scope:** Feature-specific only (standard baseline omitted)

### NFR Summary Table
| NFR ID | Priority | Category | Requirement Summary | Detail Section |
|--------|----------|----------|---------------------|----------------|
| NFR-001 | P0 | Performance | Query response <3sec P95 | #nfr-001-query-response-time |

### Processing Guidance for Spec Formatter
- **Summary sufficient for:** NFR-002, NFR-005 (standard patterns)
- **Detail read required for:** NFR-001 (complex measurement details)
- **Platform-inherited:** Standard auth, encryption, accessibility (omitted)
```

### Test Sage

```markdown
## Synthesis Index

### Acceptance Criteria Overview
- **Total ACs:** 30 (grouped by feature area)
- **Coverage:** All P0 FRs have ACs; P1 FRs have summary ACs
- **Format:** Gherkin-style (Given/When/Then)

### AC Summary Table
| AC ID | Related FR | Summary | Detail Section |
|-------|-----------|---------|----------------|
| AC-001 | FR-001 | Successful API log ingestion | #ac-001-api-log-ingestion |

### Processing Guidance for Spec Formatter
- **Summary sufficient for:** Simple pass/fail ACs
- **Detail read required for:** Complex multi-step scenarios
```

### Metrics Master

```markdown
## Synthesis Index

### Goals & Metrics Overview
- **Business Goals:** 4
- **User Outcome Goals:** 3
- **Success Metrics:** 12 (6 P0, 4 P1, 2 P2)
- **Critical Success Criteria:** 5

### Goals Summary Table
| Goal ID | Category | Goal Title | Success Indicator |
|---------|----------|------------|-------------------|
| BG-001 | Business | Improve governance visibility | 80% admin adoption |

### Metrics Summary Table
| Metric ID | Priority | Category | Metric Name | Target |
|-----------|----------|----------|-------------|--------|
| M-001 | P0 | Adoption | Feature usage rate | 60% in 3 months |

### Processing Guidance for Spec Formatter
- **Summary tables are usually sufficient** for Goals & Metrics section
- **Detail read for:** Metric measurement methodology if complex
```

## File Chunking with Synthesis Indexes

When content is split across multiple files (>500 lines):

### Main Index File
```markdown
## Synthesis Index

### Multi-File Structure
This specification's content is split across multiple files:
- `requirements-summary.md` - This file (index only)
- `fr-data-sources-part1.md` - FR-101 to FR-205
- `fr-data-sources-part2.md` - FR-301 to FR-405
- `fr-insights.md` - FR-501 to FR-510

### Complete Requirements Summary Table
[All requirements in single table]

### Processing Guidance for Spec Formatter
[Guidance covering all files]
```

### Detail Files
Each detail file should have its own focused index:
```markdown
## Synthesis Index (Part 1 of 3)

### This File's Content
- **Requirements in this file:** FR-101 to FR-205
- **Categories:** OneLake Diagnostics, Capacity Events
- **Total:** 10 requirements (6 P0, 3 P1, 1 P2)

### Requirements in This File
| Req ID | Priority | Category | Description | Detail Section |
|--------|----------|----------|-------------|----------------|
| FR-101 | P0 | Data Ingestion | OneLake API logs | #fr-101-... |

[Full detailed content for FR-101 to FR-205]
```

## Quality Checklist for Synthesis Indexes

Before finalizing any agent output with a synthesis index:

- [ ] Index is at the **very top** of the file (before any detailed content)
- [ ] Overview section provides **key statistics** (counts, categories, priorities)
- [ ] Summary table includes **all major items** with IDs
- [ ] **Section anchors** are provided for all detailed content
- [ ] Processing guidance indicates **summary vs. detail needs**
- [ ] Cross-references note **dependencies** and **related groups**
- [ ] Multi-file structures are **clearly documented**
- [ ] Index is **concise** (<100 lines typically)
- [ ] Detailed content **follows after** the index with proper anchors

## Benefits

1. **Spec-formatter reads indexes first** (~500 lines total vs. 5000+ lines of all details)
2. **Builds spec structure efficiently** using summary tables
3. **Selectively reads details** only when needed for specific sections
4. **No information loss** - all details preserved in files
5. **Faster processing** - fewer tool calls, less context usage
6. **Better quality** - formatter has full context without overflow

## Implementation Notes

- Synthesis indexes are required starting [implementation date]
- Existing agent outputs will be grandfathered (no retroactive changes needed)
- Spec-formatter has been updated to expect and use synthesis indexes
- Orchestrator tracks which agents produce indexed outputs
