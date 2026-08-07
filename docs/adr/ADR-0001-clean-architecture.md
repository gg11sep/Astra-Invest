# ADR-0001: Clean Architecture / Hexagonal Style

## Status
Accepted

## Context
Astra-Invest will grow into a complex system with multiple agents, data sources, and domain rules. We need clear boundaries so domain logic is not coupled to frameworks.

## Decision
Organize the backend by dependency direction:
- Domain models and pure business rules inward
- Application services orchestrate use cases
- Adapters (API, DB, external APIs) at the edges

## Consequences
- Easier testing of business logic without FastAPI/DB
- Slightly more boilerplate early on
- Scales better as agents and strategies are added
