# Bootstrap Plan: [Project Name]

## Metadata

```yaml
run_id: "<run-id>"
created: "<ISO-8601 timestamp>"
actor: "agentic-bootstrap-planner"
prd_version: "1.0"
```

---

## 1. Project Overview

### 1.1 Description

[Brief description extracted from PRD]

### 1.2 Project Type

- **Type**: [web-frontend | web-backend | fullstack | mobile | cli | library | service]
- **Platforms**: [browser, node, ios, android, electron, etc.]

### 1.3 Key Requirements

From PRD:
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

### 1.4 Constraints

User-specified:
- [Constraint 1, e.g., "Must use TypeScript"]
- [Constraint 2, e.g., "Deploy to AWS"]

---

## 2. Technology Stack

### 2.1 Language & Runtime

| Aspect | Choice | Version | Rationale |
|--------|--------|---------|-----------|
| Language | | | |
| Runtime | | | |
| Compilation Target | | | |
| Language Config | | | |

### 2.2 Package Management

| Aspect | Choice | Configuration |
|--------|--------|---------------|
| Package Manager | | |
| Lockfile Strategy | | |
| Workspace Setup | | |

### 2.3 Framework & Libraries

| Category | Library | Version | Purpose |
|----------|---------|---------|---------|
| Primary Framework | | | |
| UI Library | | | |
| State Management | | | |
| Data Fetching | | | |
| Routing | | | |
| Forms | | | |
| Validation | | | |
| Styling | | | |

### 2.4 Database & Persistence

| Aspect | Choice | Details |
|--------|--------|---------|
| Primary Database | | |
| ORM/Query Builder | | |
| Migrations | | |
| Caching Layer | | |
| File Storage | | |

### 2.5 Testing Stack

| Type | Tool | Configuration |
|------|------|---------------|
| Unit Testing | | |
| Integration Testing | | |
| E2E Testing | | |
| Mocking | | |
| Coverage Target | | |

### 2.6 Development Tooling

| Tool Type | Choice | Configuration |
|-----------|--------|---------------|
| Linting | | |
| Formatting | | |
| Type Checking | | |
| Git Hooks | | |
| Editor Config | | |

### 2.7 Deployment & Infrastructure

| Aspect | Choice | Details |
|--------|--------|---------|
| Hosting Platform | | |
| Container Strategy | | |
| CI/CD Pipeline | | |
| Environment Strategy | | |

### 2.8 API & Communication

| Aspect | Choice | Details |
|--------|--------|---------|
| API Style | | |
| Documentation | | |
| Authentication | | |
| Authorization | | |

### 2.9 Observability

| Aspect | Choice | Details |
|--------|--------|---------|
| Logging | | |
| Metrics | | |
| Tracing | | |
| Error Tracking | | |

---

## 3. Architecture & Design

### 3.1 Architectural Pattern

[Describe the chosen architecture pattern: modular monolith, microservices, serverless, etc.]

**Justification**: [Why this pattern fits the requirements]

### 3.2 Folder Structure

```
project-root/
├── src/
│   ├── [describe structure]
│   └── [with explanations]
├── tests/
│   └── [test organization]
├── [other directories]
│   └── [purpose]
└── [config files]
```

### 3.3 Module Boundaries

| Module | Responsibility | Dependencies |
|--------|---------------|--------------|
| | | |
| | | |

**Dependency Rules**:
- [Rule 1, e.g., "Features cannot import from other features directly"]
- [Rule 2, e.g., "Shared utilities are in /lib"]

### 3.4 Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Files (components) | | |
| Files (utilities) | | |
| Files (tests) | | |
| Components | | |
| Functions | | |
| Types/Interfaces | | |
| Constants | | |
| Environment Variables | | |

### 3.5 Code Style Guidelines

Beyond linting rules:

- [Style guideline 1]
- [Style guideline 2]
- [Style guideline 3]

---

## 4. Initialization Sequence

### 4.1 Prerequisites

```bash
# Required tools and versions
node --version  # Expected: v[X.X.X]
[package-manager] --version  # Expected: [X.X.X]
[other-tool] --version  # Expected: [X.X.X]
```

### 4.2 Project Scaffolding

```bash
# Step 1: Create project
[exact command]

# Step 2: Navigate to project
cd [project-name]

# Step 3: [Description]
[exact command]
```

### 4.3 Dependency Installation

```bash
# Core dependencies
[package-manager] add [dependencies]

# Development dependencies
[package-manager] add -D [dev-dependencies]

# [Category] dependencies
[package-manager] add [dependencies]
```

### 4.4 Configuration Files

#### 4.4.1 [filename]

```[language]
[exact file contents]
```

#### 4.4.2 [filename]

```[language]
[exact file contents]
```

#### 4.4.3 [filename]

```[language]
[exact file contents]
```

[Continue for all configuration files]

### 4.5 Initial File Structure

Create these files in order:

| Order | File | Purpose |
|-------|------|---------|
| 1 | | |
| 2 | | |
| 3 | | |

### 4.6 Database Setup

```bash
# Initialize database schema
[command]

# Run migrations
[command]

# Seed data (if applicable)
[command]
```

### 4.7 Verification Steps

```bash
# Verify installation
[command to verify setup]

# Run type checking
[command]

# Run linting
[command]

# Run tests
[command to run initial tests]

# Start development server
[command to start dev server]

# Expected output: [description]
```

---

## 5. ADR References

| ADR | Title | Decision |
|-----|-------|----------|
| [ADR-001](./adrs/ADR-001-*.md) | | |
| [ADR-002](./adrs/ADR-002-*.md) | | |
| [ADR-003](./adrs/ADR-003-*.md) | | |

---

## 6. Environment Variables

### 6.1 Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| | | |
| | | |

### 6.2 .env.example

```bash
# [Category]
VARIABLE_NAME=example_value

# [Category]
ANOTHER_VAR=example
```

---

## 7. Next Steps

After bootstrap completes:

1. [ ] [First implementation task]
2. [ ] [Second implementation task]
3. [ ] [Third implementation task]

---

## 8. Verification Checklist

Before marking bootstrap complete:

- [ ] All dependencies installed without errors
- [ ] TypeScript/language compiles without errors
- [ ] Linting passes
- [ ] Initial tests pass
- [ ] Development server starts
- [ ] Database connection works (if applicable)
- [ ] All configuration files created
- [ ] Folder structure matches specification

---

_Generated by Agentic Bootstrap Planner_
_Template Version: 1.0_
