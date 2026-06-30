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
