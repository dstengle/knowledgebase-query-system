# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) that document important architectural decisions made during the development of the KB Query CLI system.

## What is an ADR?

An Architecture Decision Record captures a single architectural decision and its rationale. Each ADR describes:
- The context and problem
- The decision made
- The consequences of that decision

## ADR Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [001](001-cli-architecture.md) | CLI Architecture for SPARQL Query System | Accepted | 2025-08-06 |
| [002](002-query-methodology.md) | Query Methodology and Grammar Generation | Accepted | 2025-08-06 |
| [003](003-configuration-management.md) | Configuration Management | Accepted | 2025-08-06 |

## ADR Template

```markdown
# ADR-XXX: Title

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-YYY]

## Context
What is the issue we're addressing?

## Decision
What have we decided to do?

## Consequences
What are the positive and negative outcomes?
```

## How to Create a New ADR

1. Copy the template above
2. Number it sequentially (e.g., 004-feature-name.md)
3. Fill in all sections
4. Update this README index
5. Link related ADRs if superseding or relating to others

## References

- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) by Michael Nygard
- [ADR Tools](https://github.com/npryce/adr-tools)