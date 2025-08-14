# SPARC Development Documentation

This directory contains SPARC (Specification, Pseudocode, Architecture, Refinement, Completion) methodology documentation for the KB Query CLI project.

## SPARC Phases

### ✅ Phase 1: [Specification](01-specification.md)
**Status**: Complete  
Defines what the system should do, including requirements, user stories, and success criteria.

### ⏳ Phase 2: [Pseudocode](02-pseudocode.md)
**Status**: Pending  
High-level algorithmic design and logical flow of the system.

### ⏳ Phase 3: [Architecture](03-architecture.md)
**Status**: Pending  
System design, component interactions, and technical architecture.

### ⏳ Phase 4: [Refinement](04-refinement.md)
**Status**: Pending  
Iterative improvements, optimizations, and implementation details.

### ⏳ Phase 5: [Completion](05-completion.md)
**Status**: Pending  
Final implementation, testing, and deployment preparation.

## How to Use These Documents

1. **Start with Specification** - Understand what we're building and why
2. **Review Pseudocode** - See the logical flow before implementation
3. **Study Architecture** - Understand component design and interactions
4. **Follow Refinement** - Track iterative improvements
5. **Check Completion** - Ensure all requirements are met

## SPARC Commands for This Project

```bash
# Run full SPARC pipeline
npx claude-flow sparc pipeline "KB Query CLI implementation"

# Run specific phases
npx claude-flow sparc run spec-pseudocode "Natural language SPARQL CLI"
npx claude-flow sparc run architect "Design modular CLI architecture"
npx claude-flow sparc tdd "Grammar processor module"

# Get information about modes
npx claude-flow sparc info architect
```

## Document Standards

Each SPARC document should include:
- Clear phase identification
- Status indicator (Pending/In Progress/Complete)
- Date of last update
- Links to related ADRs
- Code examples where applicable
- Testing criteria

## Cross-References

- [Architecture Decision Records](../adr/README.md) - Detailed architectural decisions
- [API Reference](../api-reference.md) - Technical API documentation
- [Examples](../examples.md) - Usage examples and patterns