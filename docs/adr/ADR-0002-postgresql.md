# ADR-0002: PostgreSQL as Primary Database

## Status
Accepted

## Context
We need a reliable relational store for companies, portfolios, transactions, and research artifacts, with good JSON support for flexible metadata.

## Decision
Use PostgreSQL 16 with asyncpg via SQLAlchemy 2.0 async.

## Consequences
- Strong consistency for portfolio/transaction data
- JSONB for flexible fields (meta, agent outputs)
- Operational familiarity and ecosystem maturity
