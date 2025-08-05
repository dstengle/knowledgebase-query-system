# KB Query Interface API Reference

## KBQueryEngine

Main class for natural language to SPARQL conversion.

### Constructor

```python
KBQueryEngine(ontology_path: str, config_path: Optional[str] = None)
```

**Parameters:**
- `ontology_path`: Path to OWL/RDF ontology file (Turtle format)
- `config_path`: Optional path to YAML configuration file

### Methods

#### query(natural_language_query: str) -> Dict

Convert natural language query to SPARQL.

**Parameters:**
- `natural_language_query`: Query in natural language

**Returns:**
Dictionary containing:
- `sparql`: Generated SPARQL query
- `parsed`: Parsed query components
- `results`: Query results (if endpoint configured)

**Example:**
```python
result = engine.query("meetings with John Smith")
print(result['sparql'])
```

#### get_patterns_for_class(class_name: str) -> List[str]

Get all query patterns available for a class.

**Parameters:**
- `class_name`: Name of the ontology class

**Returns:**
List of example queries for the class

#### suggest_queries(partial: str) -> List[str]

Get query suggestions for partial input.

**Parameters:**
- `partial`: Partial query string

**Returns:**
List of suggested complete queries

## Exceptions

### KBQueryError
Base exception for all KB Query errors.

### OntologyError
Raised when ontology parsing fails.

### QueryParseError
Raised when natural language query cannot be parsed.

**Attributes:**
- `suggestions`: List of similar valid queries
