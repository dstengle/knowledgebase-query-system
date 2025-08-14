# ADR-001: CLI Architecture for SPARQL Query System

## Status
Accepted

## Context
We need a command-line interface for the existing natural language to SPARQL query system that:
- Provides both interactive and direct command modes
- Maintains the ontology-based grammar generation approach
- Supports multiple endpoint profiles with authentication
- Enables testing and debugging capabilities

## Decision
We will implement a **layered architecture** with:

1. **Core Service Module** (`kb_query.core`)
   - Handles SPARQL execution
   - Manages endpoint connections
   - Processes query results
   - Completely independent of CLI concerns

2. **Grammar Processor** (`kb_query.grammar`)
   - Pre-processes OWL vocabulary files
   - Generates and caches query patterns
   - Creates natural language grammar rules

3. **CLI Wrapper** (`kb_query.cli`)
   - Interactive REPL mode
   - Command-line argument parsing
   - Profile management
   - Result formatting (ASCII tables)

## Consequences

### Positive
- Clear separation of concerns enables unit testing of each layer
- Core service can be imported and used programmatically
- Grammar caching improves startup performance
- Profile system supports multiple environments

### Negative
- Additional complexity from multiple layers
- Need to maintain cache invalidation for grammar updates

## Implementation Notes
- Config stored in `$XDG_CONFIG_HOME/kb-query/`
- Grammar cache in `$XDG_CACHE_HOME/kb-query/`
- Profiles defined in `config.yaml` with endpoint URLs and auth