# Risk Analysis Guidelines

This document provides detailed guidance on identifying and analyzing risks during planning.

## Risk Categories

### 1. Technical Risks

**Integration Risks**

- Changes to shared interfaces
- Database schema modifications
- API contract changes
- Cross-service dependencies

**Complexity Risks**

- Large file modifications (>500 lines)
- Multiple interconnected changes
- Legacy code with unclear behavior
- Missing test coverage

**Performance Risks**

- New database queries
- Increased memory usage
- Additional network calls
- Synchronous blocking operations

### 2. Process Risks

**Merge Conflict Risks**

- Hot files (frequently modified)
- Shared configuration files
- Common utility classes
- SQL migration scripts

**Review Risks**

- Large PR size
- Cross-team changes
- Security-sensitive code
- Breaking changes

**Timeline Risks**

- Dependencies on other work
- External team coordination
- Environment availability
- Testing complexity

### 3. Quality Risks

**Regression Risks**

- Changes to existing behavior
- Modifications to shared code
- Test coverage gaps
- Edge cases

**Data Risks**

- Data migration needs
- Backward compatibility
- State management changes
- Cache invalidation

## Risk Assessment Matrix

Use this matrix to evaluate risks:

| Likelihood \ Impact | Low     | Medium | High     |
| ------------------- | ------- | ------ | -------- |
| **High**            | Medium  | High   | Critical |
| **Medium**          | Low     | Medium | High     |
| **Low**             | Trivial | Low    | Medium   |

### Likelihood Indicators

**High Likelihood**:

- Has happened before in this area
- Involves known problematic code
- Requires coordination with others
- Touches critical paths

**Medium Likelihood**:

- Could happen under certain conditions
- Involves moderately complex changes
- Some uncertainty exists

**Low Likelihood**:

- Unlikely but possible
- Well-understood area
- Clear patterns to follow

### Impact Indicators

**High Impact**:

- Could cause production issues
- Would require rollback
- Affects many users
- Security implications

**Medium Impact**:

- Would require hotfix
- Affects some functionality
- Performance degradation

**Low Impact**:

- Minor issues
- Easy workarounds exist
- Limited scope

## Mitigation Strategies

### For Integration Risks

```markdown
| Strategy                    | When to Use                              |
| --------------------------- | ---------------------------------------- |
| Feature flags               | New features that may need quick disable |
| Backward compatible changes | API/contract modifications               |
| Parallel implementation     | High-risk replacements                   |
| Incremental rollout         | User-facing changes                      |
```

### For Complexity Risks

```markdown
| Strategy                 | When to Use          |
| ------------------------ | -------------------- |
| Smaller phases           | Large changes        |
| Spike/POC first          | Uncertain approaches |
| Pair review              | Critical changes     |
| Additional test coverage | Legacy modifications |
```

### For Merge Conflict Risks

```markdown
| Strategy                | When to Use       |
| ----------------------- | ----------------- |
| Early integration       | Hot file changes  |
| Coordination with teams | Shared code       |
| Lane branches           | Parallel work     |
| Smaller commits         | Long-running work |
```

### For Quality Risks

```markdown
| Strategy                | When to Use                 |
| ----------------------- | --------------------------- |
| More verification loops | High-risk changes           |
| Manual testing phase    | UI/UX changes               |
| Shadow testing          | Data processing changes     |
| Canary deployment       | Production-critical changes |
```

## Risk Documentation Template

For each identified risk, document:

```markdown
### Risk: <Short Name>

**Category**: Technical/Process/Quality

**Description**:
<What could go wrong?>

**Likelihood**: Low/Medium/High

**Impact**: Low/Medium/High

**Overall Rating**: Trivial/Low/Medium/High/Critical

**Detection**:
<How would we know if this happens?>

**Mitigation**:
<What will we do to reduce likelihood?>

**Contingency**:
<What will we do if it happens anyway?>

**Owner**: Executor/Verifier/User

**Status**: Open/Mitigated/Accepted
```

## Risk Identification Checklist

Use this checklist during planning:

### Code Change Risks

- [ ] Are we modifying files >500 lines?
- [ ] Are we changing shared utilities or base classes?
- [ ] Are we modifying public APIs or contracts?
- [ ] Are we changing database schemas?
- [ ] Are we modifying security-related code?

### Integration Risks

- [ ] Does this change affect other services?
- [ ] Are there cross-team dependencies?
- [ ] Do we need to coordinate deployment?
- [ ] Are there feature flag requirements?

### Quality Risks

- [ ] Is there existing test coverage for affected areas?
- [ ] Could this change cause regressions?
- [ ] Are there performance implications?
- [ ] Are there data migration needs?

### Process Risks

- [ ] Will this PR be large (>20 files)?
- [ ] Are we modifying frequently-changed files?
- [ ] Is special review required (security, architecture)?
- [ ] Are there timeline constraints?

## Risk Escalation

### When to Escalate to User

- Critical risks that may change approach
- Risks requiring business decisions
- Timeline-affecting risks
- Security or compliance risks

### How to Present Risks

```markdown
⚠️ RISK ALERT

We've identified the following significant risks:

1. **[Risk Name]** (Critical)
   - Issue: <brief description>
   - Mitigation: <proposed approach>
   - Trade-off: <what we give up>

Do you want to:
a) Proceed with proposed mitigations
b) Explore alternative approaches
c) Accept the risk
```

## Risk Monitoring During Execution

Certain risks should trigger verification:

| Risk Type   | Verification Trigger           |
| ----------- | ------------------------------ |
| Integration | After interface changes        |
| Performance | After query/algorithm changes  |
| Regression  | After shared code changes      |
| Data        | After schema/migration changes |

The verifier should pay special attention to flagged risks during quality loops.
