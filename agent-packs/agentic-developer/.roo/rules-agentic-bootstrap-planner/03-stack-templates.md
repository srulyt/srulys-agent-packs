# Stack Templates

Reference patterns for common project types. Use these as starting points, then customize based on specific requirements.

## Web Fullstack (TypeScript)

### Stack Overview

| Category | Choice | Version |
|----------|--------|---------|
| Language | TypeScript | 5.3+ |
| Runtime | Node.js | 20 LTS |
| Framework | Next.js | 14.x (App Router) |
| UI | React | 18.x |
| Styling | Tailwind CSS | 3.4+ |
| State | TanStack Query + Zustand | 5.x / 4.x |
| Forms | React Hook Form + Zod | 7.x / 3.x |
| Database | PostgreSQL | 16 |
| ORM | Prisma | 5.x |
| Testing | Vitest + Playwright | 1.x / 1.x |
| Linting | ESLint (flat config) | 9.x |
| Formatting | Prettier | 3.x |
| Package Manager | pnpm | 8.x |

### Folder Structure

```
project/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── (auth)/             # Auth route group
│   │   ├── (dashboard)/        # Dashboard route group
│   │   ├── api/                # API routes
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── ui/                 # Reusable UI components
│   │   └── features/           # Feature-specific components
│   ├── lib/
│   │   ├── db.ts               # Prisma client
│   │   ├── auth.ts             # Auth utilities
│   │   └── utils.ts            # Shared utilities
│   ├── hooks/                  # Custom React hooks
│   ├── stores/                 # Zustand stores
│   └── types/                  # TypeScript types
├── prisma/
│   ├── schema.prisma
│   └── migrations/
├── tests/
│   ├── unit/                   # Vitest unit tests
│   ├── integration/            # Integration tests
│   └── e2e/                    # Playwright E2E tests
├── public/
├── .env.example
├── .env.local
├── next.config.mjs
├── tailwind.config.ts
├── tsconfig.json
├── vitest.config.ts
├── playwright.config.ts
└── package.json
```

### Init Commands

```bash
# Create project
pnpm create next-app@14 . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"

# Add core dependencies
pnpm add @tanstack/react-query zod react-hook-form @hookform/resolvers zustand
pnpm add @prisma/client
pnpm add -D prisma vitest @vitejs/plugin-react jsdom @testing-library/react @testing-library/jest-dom
pnpm add -D @playwright/test prettier prettier-plugin-tailwindcss

# Initialize Prisma
pnpm prisma init

# Initialize Playwright
pnpm playwright install
```

---

## Backend API (TypeScript + Fastify)

### Stack Overview

| Category | Choice | Version |
|----------|--------|---------|
| Language | TypeScript | 5.3+ |
| Runtime | Node.js | 20 LTS |
| Framework | Fastify | 4.x |
| Validation | Zod + fastify-zod | 3.x |
| Database | PostgreSQL | 16 |
| ORM | Drizzle | 0.29+ |
| Auth | @fastify/jwt | 8.x |
| Testing | Vitest + supertest | 1.x |
| API Docs | @fastify/swagger | 8.x |
| Logging | Pino (built-in) | - |
| Package Manager | pnpm | 8.x |

### Folder Structure

```
project/
├── src/
│   ├── routes/
│   │   ├── v1/
│   │   │   ├── users.ts
│   │   │   ├── auth.ts
│   │   │   └── index.ts
│   │   └── health.ts
│   ├── schemas/                # Zod schemas
│   │   ├── user.ts
│   │   └── auth.ts
│   ├── db/
│   │   ├── schema.ts           # Drizzle schema
│   │   ├── client.ts           # DB client
│   │   └── migrations/
│   ├── services/               # Business logic
│   │   └── user.service.ts
│   ├── plugins/                # Fastify plugins
│   │   ├── auth.ts
│   │   └── db.ts
│   ├── utils/
│   ├── types/
│   ├── config.ts
│   └── app.ts
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── drizzle.config.ts
├── tsconfig.json
├── vitest.config.ts
└── package.json
```

### Init Commands

```bash
# Initialize project
pnpm init
pnpm add typescript @types/node tsx -D
pnpm tsc --init

# Add Fastify ecosystem
pnpm add fastify @fastify/cors @fastify/helmet @fastify/jwt @fastify/swagger @fastify/swagger-ui

# Add validation
pnpm add zod fastify-type-provider-zod

# Add database
pnpm add drizzle-orm postgres
pnpm add -D drizzle-kit

# Add testing
pnpm add -D vitest supertest @types/supertest
```

---

## CLI Tool (Rust)

### Stack Overview

| Category | Choice | Version |
|----------|--------|---------|
| Language | Rust | 1.75+ (stable) |
| CLI Framework | clap | 4.x |
| Async | tokio | 1.x |
| HTTP | reqwest | 0.11 |
| Serialization | serde + serde_json | 1.x |
| Error Handling | anyhow + thiserror | 1.x |
| Testing | cargo test | built-in |
| Linting | clippy | built-in |
| Formatting | rustfmt | built-in |

### Folder Structure

```
project/
├── src/
│   ├── main.rs
│   ├── cli.rs                  # CLI argument definitions
│   ├── commands/
│   │   ├── mod.rs
│   │   ├── init.rs
│   │   └── run.rs
│   ├── config.rs
│   ├── error.rs                # Custom error types
│   └── lib.rs                  # Library exports
├── tests/
│   ├── integration_tests.rs
│   └── fixtures/
├── Cargo.toml
├── Cargo.lock
├── .rustfmt.toml
├── clippy.toml
└── README.md
```

### Init Commands

```bash
# Create project
cargo new project-name
cd project-name

# Add dependencies (edit Cargo.toml)
# [dependencies]
# clap = { version = "4", features = ["derive"] }
# tokio = { version = "1", features = ["full"] }
# serde = { version = "1", features = ["derive"] }
# serde_json = "1"
# anyhow = "1"
# thiserror = "1"

cargo build
```

---

## Python Backend (FastAPI)

### Stack Overview

| Category | Choice | Version |
|----------|--------|---------|
| Language | Python | 3.12+ |
| Framework | FastAPI | 0.109+ |
| Server | Uvicorn | 0.27+ |
| Validation | Pydantic | 2.x |
| Database | PostgreSQL | 16 |
| ORM | SQLAlchemy | 2.x |
| Migrations | Alembic | 1.x |
| Testing | pytest + httpx | 8.x / 0.26 |
| Linting | Ruff | 0.2+ |
| Formatting | Ruff (format) | 0.2+ |
| Package Manager | uv | 0.1+ |

### Folder Structure

```
project/
├── src/
│   └── project_name/
│       ├── __init__.py
│       ├── main.py             # FastAPI app
│       ├── config.py           # Settings
│       ├── routers/
│       │   ├── __init__.py
│       │   ├── users.py
│       │   └── auth.py
│       ├── models/             # SQLAlchemy models
│       │   ├── __init__.py
│       │   └── user.py
│       ├── schemas/            # Pydantic schemas
│       │   ├── __init__.py
│       │   └── user.py
│       ├── services/
│       │   └── user.py
│       ├── db/
│       │   ├── __init__.py
│       │   └── session.py
│       └── utils/
├── tests/
│   ├── conftest.py
│   ├── test_users.py
│   └── fixtures/
├── alembic/
│   ├── versions/
│   └── env.py
├── alembic.ini
├── pyproject.toml
├── .python-version
└── README.md
```

### Init Commands

```bash
# Initialize with uv
uv init project-name
cd project-name

# Add dependencies
uv add fastapi uvicorn[standard] pydantic pydantic-settings
uv add sqlalchemy[asyncio] asyncpg alembic
uv add --dev pytest pytest-asyncio httpx ruff

# Initialize Alembic
uv run alembic init alembic
```

---

## Mobile App (React Native + Expo)

### Stack Overview

| Category | Choice | Version |
|----------|--------|---------|
| Language | TypeScript | 5.3+ |
| Framework | React Native | 0.73+ |
| Platform | Expo | 50+ |
| Navigation | Expo Router | 3.x |
| State | TanStack Query + Zustand | 5.x / 4.x |
| UI | NativeWind | 4.x |
| Forms | React Hook Form + Zod | 7.x / 3.x |
| Testing | Jest + React Native Testing Library | 29.x |
| Package Manager | pnpm | 8.x |

### Folder Structure

```
project/
├── app/                        # Expo Router
│   ├── (tabs)/
│   │   ├── index.tsx
│   │   ├── profile.tsx
│   │   └── _layout.tsx
│   ├── (auth)/
│   │   ├── login.tsx
│   │   └── register.tsx
│   ├── _layout.tsx
│   └── +not-found.tsx
├── components/
│   ├── ui/
│   └── features/
├── hooks/
├── stores/
├── lib/
│   ├── api.ts
│   └── auth.ts
├── types/
├── assets/
├── app.json
├── babel.config.js
├── tailwind.config.js
├── tsconfig.json
└── package.json
```

### Init Commands

```bash
# Create Expo project
pnpm create expo-app@latest . --template tabs

# Add navigation (if not using tabs template)
pnpm add expo-router expo-linking expo-constants expo-status-bar

# Add state management
pnpm add @tanstack/react-query zustand

# Add forms
pnpm add react-hook-form @hookform/resolvers zod

# Add NativeWind
pnpm add nativewind
pnpm add -D tailwindcss@3.3.2 postcss
```

---

## Library/SDK (TypeScript)

### Stack Overview

| Category | Choice | Version |
|----------|--------|---------|
| Language | TypeScript | 5.3+ |
| Build | tsup | 8.x |
| Testing | Vitest | 1.x |
| Docs | TypeDoc | 0.25+ |
| Linting | ESLint + typescript-eslint | 9.x |
| Formatting | Prettier | 3.x |
| Package Manager | pnpm | 8.x |
| Publishing | npm | - |

### Folder Structure

```
project/
├── src/
│   ├── index.ts                # Main exports
│   ├── client.ts               # Primary class/functions
│   ├── types.ts                # TypeScript types
│   ├── errors.ts               # Custom errors
│   └── utils/
├── tests/
│   ├── client.test.ts
│   └── fixtures/
├── docs/                       # Generated TypeDoc
├── examples/
│   └── basic.ts
├── tsconfig.json
├── tsup.config.ts
├── vitest.config.ts
├── package.json
└── README.md
```

### Package.json Essentials

```json
{
  "name": "@scope/package-name",
  "version": "0.0.0",
  "type": "module",
  "exports": {
    ".": {
      "import": "./dist/index.js",
      "require": "./dist/index.cjs",
      "types": "./dist/index.d.ts"
    }
  },
  "main": "./dist/index.cjs",
  "module": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "files": ["dist"],
  "scripts": {
    "build": "tsup",
    "test": "vitest",
    "docs": "typedoc"
  }
}
```

### Init Commands

```bash
# Initialize project
pnpm init

# Add build tools
pnpm add -D typescript tsup vitest

# Add documentation
pnpm add -D typedoc

# Add linting
pnpm add -D eslint @typescript-eslint/eslint-plugin @typescript-eslint/parser prettier
```

---

## Usage Notes

### Customization

These templates are starting points. Always customize based on:

1. **Project requirements** - Remove unused categories
2. **Team expertise** - Choose familiar technologies when appropriate
3. **Scale expectations** - Add caching, queuing as needed
4. **Compliance needs** - Add security/audit features

### Version Pinning

Always pin to specific versions in bootstrap plans:

```json
// Good
"next": "14.1.0"

// Avoid
"next": "^14.0.0"
"next": "latest"
```

### Template vs. Custom

Use templates when:
- Project fits a common pattern
- Time is constrained
- Team wants proven stack

Build custom when:
- Unusual requirements
- Specific technology constraints
- Performance-critical applications
