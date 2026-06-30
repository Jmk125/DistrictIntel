# Architecture Decisions

This file records important architectural decisions.

---

## Decision Template

Date:
YYYY-MM-DD

Status:
Proposed | Accepted | Superseded

Decision:
<One sentence summary>

Context:
Why was this decision needed?

Alternatives Considered:
- Option A
- Option B

Chosen Solution:
Describe the selected approach.

Consequences:
Positive:
- ...

Negative:
- ...

---

# ADR-0001

Date:
2026-06-30

Status:
Accepted

Decision:
Use SQLite as the initial application database.

Context:
Version 1 is a single-user research tool.

Alternatives:
- PostgreSQL
- SQLite

Chosen Solution:
SQLite

Reason:
Simple deployment, no server required, excellent performance for local
development, easy migration later.

Consequences:
+ Very easy setup
+ Portable database file
+ Great for development

- Not intended for heavy concurrent multi-user workloads

---

# ADR-0002

Date:
2026-06-30

Status:
Accepted

Decision:
Build independent research agents around a shared Research Engine.

Reason:
Keeps business logic reusable and allows new research capabilities without
rewriting the application.

---

# ADR-0003

Date:
2026-06-30

Status:
Accepted

Decision:
Use dataclass domain models with a small repository layer over SQLite for foundational district and school persistence.

Context:
Milestone 2 needs durable district and school storage plus CSV import without introducing research, AI, or business logic.

Alternatives Considered:
- Direct SQL calls from CLI and import services
- Full ORM such as SQLAlchemy

Chosen Solution:
Represent District and School as typed dataclasses, keep SQL isolated in repository classes, and coordinate CSV import through a service layer.

Consequences:
Positive:
- Keeps CLI, import orchestration, domain models, and SQL persistence separated.
- Avoids new runtime dependencies while the schema is small.
- Leaves room to introduce migrations or an ORM later if the data layer grows.

Negative:
- Repositories contain explicit SQL that must be maintained as schema changes.

---

# ADR-0004

Date:
2026-06-30

Status:
Accepted

Decision:
Define research extensibility through protocols, dataclass research models, and a coordinator that delegates to injected agents and source providers.

Context:
Milestone 3 needs the framework future research agents will plug into, but must not introduce OpenAI, web search, scraping, or real research behavior.

Alternatives Considered:
- Concrete base classes for every research component
- Direct function callbacks without named interfaces
- Implementing a placeholder concrete research agent

Chosen Solution:
Use Python protocols for ResearchAgent and SourceProvider, keep research data as typed dataclasses, and use a ResearchCoordinator to collect evidence from injected providers before delegating to an injected agent.

Consequences:
Positive:
- Future agents and providers can be tested independently and swapped without inheritance requirements.
- The coordinator establishes orchestration without owning research-specific logic.
- The project avoids external dependencies and fake business behavior in the architecture milestone.

Negative:
- Protocols provide structure but no shared implementation for future agents.
