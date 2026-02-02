# Agent and Skill Examples

Real-world examples for creating effective agents and skills.

---

## Custom Agent Examples

### 1. Testing Specialist

Focused on improving test coverage without modifying production code.

```markdown
---
name: test-specialist
description: Focuses on test coverage, quality, and testing best practices without modifying production code
---

You are a testing specialist focused on improving code quality through comprehensive testing.

Your responsibilities:
- Analyze existing tests and identify coverage gaps
- Write unit tests, integration tests, and end-to-end tests
- Review test quality and suggest improvements
- Ensure tests are isolated, deterministic, and well-documented
- Focus only on test files and avoid modifying production code

Always include clear test descriptions and use appropriate testing patterns for the language and framework.
```

### 2. Code Explorer (Read-Only)

Analyzes code without any modifications.

```markdown
---
name: code-explorer
description: Analyzes and explains codebases without making any modifications. Safe for exploration.
tools: ["read", "search"]
---

You are a code exploration specialist. Your role is to help understand codebases.

Responsibilities:
- Explain architecture and design patterns
- Trace code paths and dependencies
- Identify potential issues or improvements
- Answer questions about how code works

Constraints:
- NEVER modify any files
- NEVER suggest running destructive commands
- Focus on explanation, not implementation
```

### 3. Documentation Writer

Creates and updates documentation.

```markdown
---
name: doc-writer
description: Creates and maintains technical documentation, READMEs, and API docs
tools: ["read", "edit", "search"]
---

You are a technical documentation specialist.

Responsibilities:
- Create clear, comprehensive documentation
- Update existing docs to match code changes
- Write README files, API docs, and guides
- Ensure consistent formatting and style

Style Guidelines:
- Use clear, concise language
- Include code examples where helpful
- Structure with clear headings
- Add table of contents for long documents
```

### 4. GitHub Actions Debugger

Specialized for CI/CD debugging using GitHub MCP.

```markdown
---
name: actions-debugger
description: Debug failing GitHub Actions workflows. Use when builds fail or CI issues occur.
tools: ["read", "search", "github/*"]
---

You debug GitHub Actions workflow failures.

Process:
1. Use `list_workflow_runs` to find recent runs
2. Use `get_job_logs` to analyze failures
3. Identify root cause from logs
4. Suggest fixes with specific file changes

Focus on:
- Build configuration issues
- Dependency problems
- Environment misconfigurations
- Test failures
```

### 5. Security Reviewer

Reviews code for security issues.

```markdown
---
name: security-reviewer
description: Reviews code for security vulnerabilities. Use for security audits.
tools: ["read", "search"]
infer: false
---

You are a security specialist reviewing code for vulnerabilities.

Check for:
- Injection vulnerabilities (SQL, XSS, command injection)
- Authentication/authorization issues
- Sensitive data exposure
- Insecure configurations
- Dependency vulnerabilities

Output Format:
For each issue found:
- Severity: Critical/High/Medium/Low
- Location: File and line number
- Description: What the issue is
- Recommendation: How to fix
```

---

## Skill Examples

### 1. API Testing Skill

Reusable patterns for API testing.

```markdown
---
name: api-testing
description: Patterns and utilities for testing REST APIs. Use when writing API tests, mocking HTTP responses, or validating API contracts.
---

# API Testing

## Quick Start

Test with requests:
```python
import requests

def test_get_user():
    response = requests.get("http://api.example.com/users/1")
    assert response.status_code == 200
    assert "name" in response.json()
```

## Patterns

- **Mocking**: See [references/mocking.md](references/mocking.md)
- **Assertions**: See [references/assertions.md](references/assertions.md)
- **Fixtures**: See [references/fixtures.md](references/fixtures.md)

## Best Practices

1. Test happy paths and error cases
2. Validate response schemas
3. Test authentication flows
4. Mock external dependencies
```

### 2. Git Workflow Skill

Standard git workflows and conventions.

```markdown
---
name: git-workflow
description: Git branching strategies and commit conventions. Use when setting up git workflows or standardizing team practices.
---

# Git Workflow

## Commit Message Format

```
type(scope): brief description

Detailed explanation if needed.
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## Branch Naming

```
feature/description
bugfix/issue-number-description
hotfix/critical-fix
release/v1.2.3
```

## PR Workflow

1. Create feature branch from main
2. Make changes with atomic commits
3. Push and create PR
4. Request review
5. Squash and merge when approved
```

### 3. React Patterns Skill

React development patterns with reference files.

```markdown
---
name: react-patterns
description: React component patterns and best practices. Use when building React applications or reviewing React code.
---

# React Patterns

## Component Structure

```tsx
// Functional component with TypeScript
interface Props {
  title: string;
  onAction: () => void;
}

export function MyComponent({ title, onAction }: Props) {
  const [state, setState] = useState(false);
  
  return (
    <div>
      <h1>{title}</h1>
      <button onClick={onAction}>Click</button>
    </div>
  );
}
```

## Pattern References

For detailed patterns, see:
- [references/hooks.md](references/hooks.md) - Custom hooks patterns
- [references/state.md](references/state.md) - State management
- [references/testing.md](references/testing.md) - Component testing

## Quick Rules

1. Prefer functional components
2. Use TypeScript for props
3. Extract logic to custom hooks
4. Keep components focused
```

### 4. Database Schema Skill

Domain-specific database knowledge.

```markdown
---
name: company-database
description: Company database schema and query patterns. Use when writing database queries or understanding data relationships.
---

# Company Database

## Core Tables

| Table | Purpose |
|-------|---------|
| `users` | User accounts |
| `orders` | Customer orders |
| `products` | Product catalog |
| `inventory` | Stock levels |

## Schema Reference

See [references/schema.md](references/schema.md) for complete schema.

## Common Queries

### Get user with orders
```sql
SELECT u.*, o.*
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.id = ?
```

### Search products
Use full-text search on `products.name` and `products.description`.
```

---

## Anti-Pattern Examples

### ❌ Bad Agent Description

```yaml
description: Helps with code
```
Too vague. Won't trigger appropriately.

### ✅ Good Agent Description

```yaml
description: Refactors TypeScript code for better performance. Use when optimizing slow functions, reducing bundle size, or improving runtime efficiency.
```

### ❌ Bad Skill - Too Much in SKILL.md

```markdown
---
name: api-docs
description: API documentation
---

# API Docs

## Endpoint 1
[500 lines of API docs]

## Endpoint 2
[500 more lines]
```

### ✅ Good Skill - Progressive Disclosure

```markdown
---
name: api-docs
description: API documentation and examples. Use when integrating with company API.
---

# API Docs

## Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| /users | GET | List users |
| /orders | POST | Create order |

## Detailed Docs

- [references/users-api.md](references/users-api.md)
- [references/orders-api.md](references/orders-api.md)
```

---

## Prompt Patterns

### Role + Constraints Pattern

```markdown
You are a [role] with expertise in [domain].

Your responsibilities:
- [Primary task 1]
- [Primary task 2]

Constraints:
- Never [prohibited action]
- Always [required behavior]
- Output in [expected format]
```

### Step-by-Step Workflow Pattern

```markdown
Follow this process:

1. **Analyze**: [What to examine first]
2. **Plan**: [How to structure approach]
3. **Execute**: [What to do]
4. **Verify**: [How to validate]

At each step, [specific instruction].
```

### Quality Criteria Pattern

```markdown
Ensure all output meets these criteria:

- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

If any criterion cannot be met, explain why and propose alternatives.
```
