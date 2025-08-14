# ADR-002: Query Methodology and Grammar Generation

## Status
Accepted

## Context
The system needs to convert natural language queries to SPARQL without requiring users to know SPARQL syntax. The existing design uses OWL ontology structure to automatically generate valid query patterns.

## Decision
We will maintain and enhance the **ontology-driven pattern generation** approach:

1. **Pre-processing Phase**
   - Parse OWL/RDF vocabulary file
   - Extract classes, properties, domains, and ranges
   - Generate natural language patterns from property names
   - Cache generated grammar for performance

2. **Query Processing**
   - Match user input against generated patterns
   - Extract entities and constraints
   - Build SPARQL query from matched pattern
   - Execute against configured endpoint

3. **Feedback Loop**
   - Show generated SPARQL (optional)
   - Display parsing errors with suggestions
   - Provide debug mode for development

## Pattern Generation Examples

| OWL Property | Domain | Range | Generated Patterns |
|-------------|--------|-------|-------------------|
| kb:hasAttendee | kb:Meeting | kb:Person | "meetings with {Person}", "meetings attended by {Person}" |
| kb:assignedTo | kb:Todo | kb:Person | "todos assigned to {Person}", "{Person}'s todos" |
| kb:hasTag | kb:Entity | xsd:string | "{Entity} tagged {tag}", "{Entity} with tag {tag}" |

## Consequences

### Positive
- No SPARQL knowledge required from users
- Automatically valid queries based on ontology structure
- Natural language patterns derived from property names
- Extensible to new ontologies without code changes

### Negative
- Initial processing time for large ontologies
- Limited to patterns derivable from ontology structure
- May miss complex query patterns not expressible in OWL

## Cache Strategy
- Grammar cached after first generation
- Cache invalidated when ontology file modified
- Manual cache clear option via CLI flag