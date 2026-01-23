# Technology Research Methodology

This document defines the structured approach for researching and evaluating technology alternatives during bootstrap planning.

## Research Process

### Step 1: Define Decision Category

Identify which of the 12 categories this decision falls under:

| Category | Typical Decisions |
|----------|-------------------|
| Language & Runtime | Programming language, runtime version, compilation target |
| Package Management | Package manager, dependency strategy, monorepo tooling |
| Project Type | Application architecture, target platforms |
| Framework | Primary framework, UI libraries, state management |
| Architecture | Design patterns, folder structure, module boundaries |
| Database | Database engine, ORM, migration strategy |
| Caching | Cache layers, invalidation strategy |
| Testing | Test frameworks, coverage requirements, test types |
| Deployment | Hosting platform, containerization, CI/CD |
| Tooling | Linting, formatting, git hooks, editor config |
| API Design | API style, documentation, authentication |
| Observability | Logging, metrics, tracing, error tracking |

### Step 2: Gather Requirements

From the PRD and constraints, extract:

1. **Hard constraints** - Must-have requirements ("must use Python")
2. **Soft preferences** - Nice-to-have preferences ("preferably TypeScript")
3. **Scale expectations** - Load, data size, concurrent users
4. **Team context** - Team size, expertise, learning capacity
5. **Timeline pressures** - MVP deadline, iteration speed needs

### Step 3: Identify Alternatives

For each category, identify 2-4 viable alternatives that:

- Meet all hard constraints
- Are actively maintained (check GitHub activity, npm downloads)
- Have sufficient ecosystem support
- Match the project's scale requirements

**Avoid**:
- Dead or dying technologies (check last commit, issue activity)
- Experimental/alpha technologies for production projects
- Technologies with known security issues

### Step 4: Evaluate Alternatives

Use this evaluation framework:

#### Evaluation Criteria

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Fit** | 5 | How well does it meet requirements? |
| **Ecosystem** | 4 | Library availability, integrations, tooling |
| **Learning Curve** | 3 | Time to productivity for typical developer |
| **Community** | 3 | Documentation quality, Stack Overflow activity |
| **Performance** | 3-5 | Runtime performance (weight varies by project) |
| **Maintainability** | 4 | Long-term maintenance burden |
| **Security** | 4 | Security track record, vulnerability response |

Weights are defaults; adjust based on project priorities.

#### Scoring

For each alternative, score 1-5 on each criterion:

| Score | Meaning |
|-------|---------|
| 5 | Excellent - Best possible fit |
| 4 | Good - Strong option |
| 3 | Adequate - Meets requirements |
| 2 | Weak - Some concerns |
| 1 | Poor - Significant issues |

Calculate weighted total: Σ(score × weight)

### Step 5: Document Trade-offs

For each alternative, document:

**Pros**:
- Specific advantages for this project
- Concrete benefits (not generic marketing claims)

**Cons**:
- Specific disadvantages for this project
- Honest assessment of limitations

**Risks**:
- What could go wrong?
- Mitigation strategies

### Step 6: Make Recommendation

State your recommendation with:

1. **Clear choice** - One specific technology with version
2. **Primary rationale** - The main reason(s) for this choice
3. **Trade-offs accepted** - What we're giving up
4. **Risks acknowledged** - Known risks and mitigations

## Research Document Template

Create `.agent-memory/runs/<run-id>/research/technology-evaluation.md`:

```markdown
# Technology Research: [Project Name]

## Run Information
- Run ID: <run-id>
- Created: <timestamp>
- PRD Version: 1.0

---

## Category: [Category Name]

### Context
[Why this decision matters for this project]

### Requirements
- [Requirement 1 from PRD]
- [Requirement 2 from PRD]
- [Constraint from user]

### Options Evaluated

#### Option A: [Name + Version]

**Overview**: [2-3 sentence description]

**Pros**:
- [Specific pro for this project]
- [Another pro]

**Cons**:
- [Specific con for this project]
- [Another con]

**Fit Score**: [1-5]
**Ecosystem Score**: [1-5]
**Learning Curve Score**: [1-5]
**Community Score**: [1-5]
**Performance Score**: [1-5]
**Maintainability Score**: [1-5]
**Security Score**: [1-5]

---

#### Option B: [Name + Version]
[Same structure as Option A]

---

### Decision Matrix

| Criterion | Weight | [Option A] | [Option B] | [Option C] |
|-----------|--------|------------|------------|------------|
| Fit | 5 | [1-5] | [1-5] | [1-5] |
| Ecosystem | 4 | [1-5] | [1-5] | [1-5] |
| Learning Curve | 3 | [1-5] | [1-5] | [1-5] |
| Community | 3 | [1-5] | [1-5] | [1-5] |
| Performance | [3-5] | [1-5] | [1-5] | [1-5] |
| Maintainability | 4 | [1-5] | [1-5] | [1-5] |
| Security | 4 | [1-5] | [1-5] | [1-5] |
| **Weighted Total** | | [total] | [total] | [total] |

### Recommendation

**Choice**: [Technology + specific version]

**Rationale**: [Why this is the best choice]

**Trade-offs Accepted**:
- [What we're giving up by choosing this]

**Risks & Mitigations**:
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| [Risk 1] | Low/Med/High | [Mitigation strategy] |

---

[Repeat for each category requiring research]
```

## ADR Triggers

Create an ADR when a decision meets ANY of:

1. **Irreversibility** - Difficult or expensive to change later
2. **Cross-cutting** - Affects multiple components
3. **Controversial** - Multiple valid approaches with strong trade-offs
4. **Precedent-setting** - Establishes a pattern others will follow
5. **Risk-bearing** - Has security, performance, or reliability implications

Examples that ALWAYS need ADRs:
- Primary programming language
- Primary framework choice
- Database selection
- Authentication strategy
- Deployment platform

Examples that usually DON'T need ADRs:
- Linting rule preferences
- Test utility library choices
- Minor package selections

## Practical Research Techniques

### Verifying Technology Health

Before recommending a technology, verify:

1. **GitHub Activity**
   - Last commit date (should be within 3 months for active projects)
   - Open issues / PRs (high ratio of stale issues = concern)
   - Contributor count (more than 1-2 active maintainers)

2. **Package Downloads**
   - npm: weekly downloads trend
   - PyPI: monthly downloads
   - Crates.io: recent downloads

3. **Version Stability**
   - Breaking changes frequency
   - LTS availability
   - Deprecation policy

### Probing Available Tooling

Use `command` tool to check what's available:

```bash
# Check Node.js version
node --version

# Check if package manager is available
pnpm --version

# Check available runtimes
which python3
which rustc
```

### Stack Compatibility

Verify chosen technologies work together:

1. Check official integration guides
2. Look for "with [tech]" in documentation
3. Search for integration issues on GitHub
4. Check for official adapters/plugins

## Common Decision Patterns

### Web Fullstack (2024+)

| Category | Common Choices |
|----------|----------------|
| Language | TypeScript 5.x |
| Runtime | Node.js 20 LTS |
| Framework | Next.js 14, SvelteKit, Remix |
| Database | PostgreSQL 16, SQLite (small) |
| ORM | Prisma, Drizzle |
| Testing | Vitest + Playwright |
| Styling | Tailwind CSS |

### Backend API (2024+)

| Category | Common Choices |
|----------|----------------|
| Language | TypeScript, Go, Rust, Python |
| Framework | Fastify, Hono, Axum, FastAPI |
| Database | PostgreSQL, Redis |
| ORM/Query | Prisma, sqlx, SQLAlchemy |
| API Style | REST, tRPC, GraphQL |
| Testing | Framework-native + supertest |

### CLI Tool (2024+)

| Category | Common Choices |
|----------|----------------|
| Language | Rust, Go, TypeScript (Node) |
| Framework | Clap (Rust), Cobra (Go), Commander (Node) |
| Distribution | Homebrew, npm, cargo |
| Testing | Integration tests with temp dirs |

See [`03-stack-templates.md`](03-stack-templates.md) for complete stack patterns.
