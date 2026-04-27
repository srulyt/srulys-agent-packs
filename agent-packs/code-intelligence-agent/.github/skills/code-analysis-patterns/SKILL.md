---
name: code-analysis-patterns
description: "Business logic detection patterns for identifying authorization, events, domain models, and API mappings across common frameworks. Use when analyzing code to extract business-relevant knowledge. Keywords: business logic, authorization, RBAC, events, domain model, API mapping."
---

# Code Analysis Patterns

Patterns for identifying business-relevant code structures across languages and frameworks. This skill is the single source of truth for how to recognize business logic, authorization models, events, domain entities, and API-to-business mappings in source code.

## When to Use This Skill

Load this skill when:
- Analyzing source code to extract business capabilities
- Identifying authorization and access control patterns
- Detecting business event emission and telemetry
- Mapping API endpoints to business operations
- Recognizing domain model entities and relationships

## Core Concepts

### Business Logic vs. Infrastructure Code

Business logic is code that implements business rules, policies, or domain behaviors. Infrastructure code supports execution but does not encode business meaning.

| Category | Examples | Business Relevance |
|----------|----------|-------------------|
| **Business Rules** | Validation logic, eligibility checks, pricing calculations | High — directly encodes domain policy |
| **Authorization** | Role checks, permission enforcement, access control | High — defines who can do what |
| **Domain Events** | Event emissions tied to business actions | High — signals business-significant state changes |
| **Data Transformations** | Mapping between business entities and storage | Medium — reveals domain model structure |
| **Infrastructure** | Logging, caching, serialization, HTTP plumbing | Low — supports execution, not business meaning |

### Signal Strength

Not all code patterns carry the same analytical weight:

- **Strong signals**: Business-named functions (`calculateDiscount`, `approveOrder`), domain-specific exceptions (`InsufficientFundsError`), explicit rule engines
- **Medium signals**: Conditional branches on domain state, configuration-driven behavior, feature flags
- **Weak signals**: Generic CRUD operations, framework boilerplate, auto-generated code

## Patterns

### Pattern 1: Business Rule Detection

**Use when**: Identifying code that encodes business policies, validation rules, or domain logic.

**Indicators**:
- Conditional logic on domain state (not infrastructure concerns like null checks)
- Functions named with business verbs: `validate`, `calculate`, `approve`, `reject`, `qualify`, `enforce`
- Switch/match statements on business-meaningful enums (order status, user type, subscription tier)
- Threshold or limit checks with business-meaningful constants
- Custom exception/error types named after business scenarios

**Framework-Specific Patterns**:

| Framework | Pattern | Example |
|-----------|---------|---------|
| **Spring** | `@Service` classes with business-named methods | `OrderService.calculateTotal()` |
| **Django** | Model methods, manager methods, form validation | `Order.can_cancel()`, `clean()` methods |
| **Express/NestJS** | Service layer classes, middleware validators | `PricingService.applyDiscount()` |
| **Rails** | Model validations, callbacks, service objects | `validates :age, numericality: { greater_than: 18 }` |
| **ASP.NET** | Domain services, FluentValidation rules | `OrderValidator : AbstractValidator<Order>` |
| **Go** | Domain package functions, interface methods | `func (o *Order) CanBeCancelled() bool` |

**Search Patterns** (for grep/glob):
```
# Business validation
validate|Validate|Validator|isValid|isEligible|canBe|qualifies

# Business calculations
calculate|compute|determine|evaluate|assess|estimate

# Business decisions
approve|reject|authorize|deny|grant|revoke|suspend|activate

# Business rules
Rule|Policy|Constraint|Specification|Criteria
```

### Pattern 2: Authorization & Access Control

**Use when**: Identifying who can do what in the system — roles, permissions, and enforcement points.

**Indicators**:
- Role/permission checks before business operations
- Middleware or decorators that enforce access
- User role enumerations and permission definitions
- Token/session inspection for authorization data

**Framework-Specific Patterns**:

| Framework | Pattern | Search For |
|-----------|---------|------------|
| **Spring Security** | `@PreAuthorize`, `@Secured`, `SecurityConfig` | `@PreAuthorize`, `hasRole`, `hasAuthority`, `SecurityFilterChain` |
| **Django** | `@permission_required`, `@login_required`, custom mixins | `permission_required`, `LoginRequiredMixin`, `has_perm` |
| **Express** | Middleware functions, JWT verification | `req.user.role`, `authorize(`, `isAuthenticated` |
| **NestJS** | `@UseGuards`, `@Roles`, custom guards | `@UseGuards`, `@Roles`, `canActivate`, `RolesGuard` |
| **Rails** | Pundit policies, CanCanCan abilities | `authorize`, `policy(`, `can?`, `ability.rb` |
| **ASP.NET** | `[Authorize]`, policies, claims | `[Authorize(Roles`, `[Authorize(Policy`, `RequireClaim` |
| **Go** | Middleware functions, context-based auth | `middleware.Auth`, `ctx.Value("user")`, `HasPermission` |

**What to Extract**:
- List of roles/groups defined in the system
- Permissions associated with each role
- Enforcement points (which endpoints/operations check authorization)
- The authorization model type: RBAC, ABAC, ACL, or custom

### Pattern 3: Event & Telemetry Detection

**Use when**: Identifying business events the system emits, telemetry it tracks, and logging with business context.

**Indicators**:
- Event emission calls with business-named event types
- Message queue publishing (Kafka, RabbitMQ, SQS, etc.)
- Analytics/telemetry tracking calls with business properties
- Audit logging with business context

**Framework-Specific Patterns**:

| Framework | Pattern | Search For |
|-----------|---------|------------|
| **Spring** | `ApplicationEventPublisher`, `@EventListener` | `publishEvent`, `@EventListener`, `@KafkaListener` |
| **Django** | Django signals, Celery tasks | `signal.send`, `post_save`, `.delay()`, `.apply_async()` |
| **Node.js** | EventEmitter, message queue clients | `emit(`, `publish(`, `sendMessage(`, `amqplib`, `bullmq` |
| **Rails** | ActiveSupport::Notifications, Sidekiq | `instrument(`, `ActiveSupport::Notifications`, `perform_async` |
| **ASP.NET** | MediatR notifications, Azure Service Bus | `Publish(`, `INotification`, `ServiceBusClient` |
| **Go** | Channel-based events, message queue clients | `ch <-`, `nats.Publish`, `kafka.Produce` |

**What to Extract**:
- Event name/type and business meaning
- Where in the codebase the event is emitted
- What triggers the event (business action)
- Event payload structure (what data is carried)
- Known consumers/handlers of the event

### Pattern 4: Domain Model Recognition

**Use when**: Identifying the core business entities, their properties, relationships, and where they are defined.

**Indicators**:
- Classes/structs with business-named properties
- Database schema definitions (migrations, ORM models)
- Relationship declarations (has-many, belongs-to, foreign keys)
- Aggregate root patterns, entity/value object distinctions

**Framework-Specific Patterns**:

| Framework | Pattern | Search For |
|-----------|---------|------------|
| **Spring/JPA** | `@Entity`, `@Table`, relationship annotations | `@Entity`, `@OneToMany`, `@ManyToOne`, `@MappedSuperclass` |
| **Django** | `models.Model` subclasses, `ForeignKey` | `class.*Model`, `ForeignKey`, `ManyToManyField` |
| **TypeORM/Prisma** | Entity decorators, schema definitions | `@Entity()`, `schema.prisma`, `@Column` |
| **Rails** | `ActiveRecord::Base`, associations | `has_many`, `belongs_to`, `has_one`, `validates` |
| **EF Core** | `DbContext`, entity configurations | `DbSet<`, `HasMany`, `HasOne`, `ModelBuilder` |
| **Go** | Struct definitions, GORM tags | `gorm:"`, struct field tags, `type.*struct` |

**What to Extract**:
- Entity name and business purpose
- Key properties/fields and their business meaning
- Relationships between entities (and cardinality)
- Where the entity is defined (file, class/struct)
- Aggregate boundaries (if DDD patterns are used)

### Pattern 5: API-to-Business Mapping

**Use when**: Mapping REST, GraphQL, or gRPC endpoints to the business operations they perform.

**Indicators**:
- Route/endpoint definitions with HTTP methods
- Controller/handler functions that invoke business services
- Request/response DTOs that reveal business data structures
- API documentation annotations (Swagger/OpenAPI decorators)

**What to Extract Per Endpoint**:
- HTTP method and path (or GraphQL operation name, or gRPC service method)
- Business operation it performs (in plain language)
- Input parameters and their business meaning
- Response structure and business entities returned
- Authorization requirements (who can call it)
- Business events triggered (if any)

## Confidence Calibration Rules

Apply these rules when labeling the confidence of each finding:

| Level | Criteria | Examples |
|-------|----------|---------|
| **Explicit** | Directly confirmed by code comments, docstrings, README, test descriptions, or OpenAPI annotations | `// Checks if user has admin role`, `"""Calculate the total including tax"""` |
| **High** | Strong naming/structural signal — unambiguous intent without comments | Function named `isAdmin()`, class named `OrderCancellationPolicy`, middleware named `requireAuth` |
| **Inferred** | Analyst interpretation of behavior — code does X which likely means Y | A function checks `user.tier === 'premium'` before applying a discount — inferred as a premium pricing rule |

**When in doubt, choose the lower confidence level.** It's better to be conservative than to overclaim.

## Best Practices

1. **Start from entry points, not random files**: Always trace business logic from known entry points (routes, CLI commands, event handlers) into the implementation.
2. **Follow the money**: Business logic often lives in service layers between controllers and data access — focus there.
3. **Read tests for intent**: Test descriptions and test names often reveal business intent more clearly than implementation code.
4. **Check config files for feature flags**: Feature flags reveal business capabilities that may not be obvious from code structure alone.
5. **Look for domain language**: Business terms in variable names, function names, and class names are your strongest signal for business meaning.
6. **Cross-reference with error messages**: Error messages and exception types often contain plain-language descriptions of business rules.

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Analyzing framework boilerplate | Wastes time on infrastructure, not business logic | Skip auto-generated code, focus on custom business logic |
| Reporting CRUD as business capabilities | Every app has CRUD — it's not insight | Focus on the business rules that govern CRUD operations |
| Ignoring test files | Missing explicit intent descriptions | Read test names and descriptions for business context |
| Over-inferring from generic code | Creating false business narratives | Mark as `[GAP]` when code purpose is genuinely unclear |
| Tracing into third-party libraries | Following code outside the business domain | Stop at library boundaries, note the dependency |
| Confusing logging with business events | Not all `log()` calls are business events | Only catalog log calls with business-named events or structured business data |

## Quality Checklist

- [ ] Business rules identified with specific code locations
- [ ] Authorization model documented with roles and enforcement points
- [ ] Business events cataloged with emitters and consumers
- [ ] Domain entities mapped with relationships
- [ ] API endpoints mapped to business operations
- [ ] Every finding has a confidence label
- [ ] Inferred findings include reasoning explanation
- [ ] Gaps flagged explicitly, not filled with assumptions
- [ ] Framework-specific patterns applied for the detected tech stack
- [ ] Tests and documentation checked for explicit business intent
