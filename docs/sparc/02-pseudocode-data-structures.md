# SPARC Phase 2: Data Structures

## Core Data Structures

### 1. Pattern Definition
```
STRUCTURE Pattern:
    id: string                    # Unique identifier
    template: string              # "meetings with {person}"
    sparql_template: string       # Template with SPARQL variables
    entity_types: dict           # {person: kb:Person}
    confidence: float            # Pattern reliability score
    examples: list[string]       # ["meetings with John Smith"]
    keywords: set[string]        # {"meetings", "with"}
    domain_class: string         # kb:Meeting
    property: string             # kb:hasAttendee
    
    METHODS:
        match(user_input) -> MatchResult
        extract_entities(input) -> dict
        generate_examples() -> list[string]
```

### 2. Query Structure
```
STRUCTURE ParsedQuery:
    original_input: string       # "meetings with John Smith"
    matched_pattern: Pattern     # Reference to matched pattern
    entities: dict              # {person: "John Smith"}
    confidence: float           # Match confidence
    sparql_variables: dict      # {?meeting: "meetings", ?person: "John Smith"}
    filters: list[Filter]       # Additional constraints
    temporal_constraints: TemporalConstraint  # Date/time filters
    
    METHODS:
        to_sparql() -> string
        validate() -> bool
        get_variable_bindings() -> dict
```

### 3. Grammar Structure
```
STRUCTURE Grammar:
    patterns: list[Pattern]      # All available patterns
    ontology_hash: string        # Source ontology identifier
    namespaces: dict            # {kb: "http://example.org/kb#"}
    classes: dict               # {Meeting: ClassDefinition}
    properties: dict            # {hasAttendee: PropertyDefinition}
    created_at: datetime        # Cache timestamp
    
    METHODS:
        find_patterns(input) -> list[MatchResult]
        suggest_completions(partial) -> list[string]
        get_patterns_for_class(class_name) -> list[Pattern]
        validate_grammar() -> bool
```

### 4. Configuration Structure
```
STRUCTURE Configuration:
    profiles: dict[string, Profile]  # {dev: Profile, prod: Profile}
    default_profile: string          # "dev"
    cache_settings: CacheSettings    # Cache configuration
    debug: bool                      # Global debug flag
    timeout: int                     # Query timeout in seconds
    
STRUCTURE Profile:
    name: string                     # "development"
    endpoint_url: string            # "http://localhost:3030/kb"
    auth_type: AuthType             # BASIC, BEARER, NONE
    credentials: Credentials        # Auth credentials
    timeout_override: int           # Profile-specific timeout
    verify_ssl: bool               # SSL verification
    
STRUCTURE Credentials:
    username: string               # Encrypted storage
    password: string               # Encrypted storage
    token: string                 # For bearer auth
    
    METHODS:
        encrypt() -> EncryptedCredentials
        decrypt() -> PlainCredentials
        from_env_vars() -> Credentials
```

### 5. Result Structures
```
STRUCTURE QueryResult:
    sparql: string                 # Generated SPARQL query
    bindings: list[VariableBinding]  # Result rows
    variables: list[string]        # Column names
    execution_time: float          # Query duration in seconds
    endpoint: string               # Which endpoint was used
    success: bool                  # Execution status
    error: Optional[QueryError]    # Error details if failed
    
STRUCTURE VariableBinding:
    # Single row of results
    values: dict[string, RDFValue]  # {?person: "John Smith"}
    
    METHODS:
        get(variable_name) -> RDFValue
        to_dict() -> dict
        format_for_display() -> dict

STRUCTURE RDFValue:
    value: string                  # "John Smith"
    datatype: string              # xsd:string, xsd:date, etc.
    language: Optional[string]    # "en", "fr", etc.
    is_literal: bool              # True for literals, False for URIs
    
    METHODS:
        formatted_value() -> string
        python_value() -> object  # Convert to Python type
```

### 6. Cache Structures
```
STRUCTURE CacheEntry:
    key: string                   # Cache key
    value: object                 # Cached data
    created_at: datetime         # When cached
    last_accessed: datetime      # For LRU eviction
    size_bytes: int              # Memory usage
    ttl: Optional[int]           # Time to live in seconds
    
STRUCTURE CacheManager:
    entries: dict[string, CacheEntry]
    max_size: int                # Maximum cache size in bytes
    current_size: int            # Current cache usage
    eviction_policy: EvictionPolicy  # LRU, LFU, etc.
    
    METHODS:
        get(key) -> Optional[object]
        put(key, value, ttl=None) -> bool
        evict_lru() -> list[string]
        clear() -> None
        stats() -> CacheStats
```

### 7. Error Structures
```
STRUCTURE QueryError:
    error_type: ErrorType        # PARSE_ERROR, SPARQL_ERROR, etc.
    message: string             # Human-readable message
    suggestions: list[string]   # Possible corrections
    original_query: string      # User's input
    debug_info: dict           # Detailed error context
    
ENUM ErrorType:
    PATTERN_NOT_FOUND          # No matching pattern
    ENTITY_NOT_RECOGNIZED      # Unknown entity in query
    SPARQL_SYNTAX_ERROR        # Generated SPARQL invalid
    ENDPOINT_CONNECTION_ERROR   # Network/endpoint issue
    AUTHENTICATION_ERROR       # Auth failure
    QUERY_TIMEOUT              # Query took too long
    CONFIGURATION_ERROR        # Config file issue

STRUCTURE MatchResult:
    pattern: Pattern            # Matched pattern
    confidence: float          # Match confidence (0.0-1.0)
    entities: dict             # Extracted entities
    match_type: MatchType      # EXACT, FUZZY, PARTIAL
    
ENUM MatchType:
    EXACT                      # Perfect match
    FUZZY                      # Close match with typos
    PARTIAL                    # Incomplete match
    CONTEXTUAL                 # Match based on context
```

### 8. Session Structures
```
STRUCTURE InteractiveSession:
    session_id: string         # Unique session identifier
    history: list[QueryHistory]  # Query history
    current_profile: string    # Active profile
    debug_mode: bool          # Debug flag for session
    show_sparql: bool         # Show SPARQL flag
    variables: dict           # Session variables
    
STRUCTURE QueryHistory:
    timestamp: datetime        # When query was executed
    input: string             # Original user input
    sparql: string           # Generated SPARQL
    success: bool            # Execution result
    execution_time: float    # Duration in seconds
    result_count: int        # Number of results returned
```

## Memory-Optimized Structures

### 1. Compressed Pattern Storage
```
STRUCTURE CompressedPattern:
    # More memory-efficient pattern storage
    id: uint32                    # Numeric ID instead of string
    template_hash: uint64         # Hash of template string
    template_ref: StringRef       # Reference to shared string pool
    entity_type_bitmap: uint64    # Bit flags for entity types
    
    METHODS:
        decompress() -> Pattern
        matches_hash(input_hash) -> bool
```

### 2. String Interning Pool
```
STRUCTURE StringPool:
    # Deduplicate common strings to save memory
    strings: list[string]         # Unique strings
    string_to_id: dict[string, uint32]  # String -> ID mapping
    
    METHODS:
        intern(s: string) -> uint32
        get_string(id: uint32) -> string
        size() -> int
        memory_usage() -> int
```

## Serialization Formats

### 1. Grammar Cache Format
```json
{
  "version": "1.0",
  "ontology_hash": "sha256:abc123...",
  "created_at": "2025-08-06T15:30:00Z",
  "namespaces": {
    "kb": "http://example.org/kb#",
    "foaf": "http://xmlns.com/foaf/0.1/"
  },
  "patterns": [
    {
      "id": "pattern_001",
      "template": "meetings with {person}",
      "sparql_template": "SELECT ?meeting WHERE { ?meeting kb:hasAttendee ?person . ?person foaf:name \"{person}\" }",
      "entity_types": {"person": "foaf:Person"},
      "confidence": 0.95,
      "examples": ["meetings with John Smith", "meetings with Sarah"],
      "keywords": ["meetings", "with"],
      "domain_class": "kb:Meeting",
      "property": "kb:hasAttendee"
    }
  ]
}
```

### 2. Configuration File Format
```yaml
# ~/.config/kb-query/config.yaml
default_profile: dev
debug: false
timeout: 30

cache:
  enabled: true
  max_size: "50MB"
  ttl: 3600  # 1 hour

profiles:
  dev:
    endpoint: "http://fuseki:3030/test"
    auth_type: "basic"
    username: "${KB_DEV_USER}"
    password: "${KB_DEV_PASS}"
    verify_ssl: false
    
  prod:
    endpoint: "http://localhost:13030/kb"
    auth_type: "basic" 
    username: "${KB_PROD_USER}"
    password: "${KB_PROD_PASS}"
    verify_ssl: true
```

## Performance Characteristics

| Structure | Size (bytes) | Access Time | Notes |
|-----------|--------------|-------------|--------|
| Pattern | ~1KB | O(1) | With string interning |
| ParsedQuery | ~2KB | O(1) | Typical query |
| Grammar | ~10MB | O(log n) | Pattern lookup |
| QueryResult | ~5KB/row | O(1) | Per result row |
| CacheEntry | Variable | O(1) | Hash table lookup |

## Thread Safety

All data structures implement thread-safe access patterns:

- **Read-heavy structures** (Grammar, Configuration): Immutable after creation
- **Write-heavy structures** (Cache, Session): Protected by locks
- **Temporary structures** (ParsedQuery, QueryResult): Thread-local

## Validation Rules

Each structure includes validation methods:

```
INTERFACE Validatable:
    validate() -> ValidationResult
    
STRUCTURE ValidationResult:
    is_valid: bool
    errors: list[ValidationError]
    warnings: list[string]
```

Example validations:
- Pattern templates must contain at least one entity placeholder
- SPARQL templates must be syntactically valid
- Entity types must exist in ontology
- Configuration profiles must have valid endpoints
- Cache entries must not exceed size limits