# ADR-0003: SQLAlchemy 2.0 Async + Alembic

## Status
Accepted

## Context
FastAPI is async-first. Blocking DB drivers would hurt concurrency under agent workloads.

## Decision
- SQLAlchemy 2.0 with async sessions
- Alembic for migrations (async online mode)
- Explicit models with Mapped[] annotations

## Consequences
- Non-blocking I/O for request handlers
- Migration workflow is explicit and reviewable
- Team must be careful with session lifecycle in async code
