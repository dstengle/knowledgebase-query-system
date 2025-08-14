# SPARC Phase 3: Architecture

## System Overview

The KB Query CLI follows a **layered architecture** with clear separation of concerns, enabling testability, maintainability, and future extensibility.

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI Interface Layer                      │
│  ┌─────────────────┐  ┌──────────────────────────────────┐ │
│  │ Interactive CLI │  │        Command CLI               │ │
│  │   (REPL)       │  │     (Single Query)               │ │
│  └─────────────────┘  └──────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                 Application Service Layer                   │
│  ┌─────────────────┐  ┌─────────────────┐ ┌──────────────┐ │
│  │ Query Processor │  │ Config Manager  │ │ Result       │ │
│  │                 │  │                 │ │ Formatter    │ │
│  └─────────────────┘  └─────────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                    Core Business Layer                      │
│  ┌─────────────────┐  ┌─────────────────┐ ┌──────────────┐ │
│  │ Grammar Engine  │  │ Pattern Matcher │ │ SPARQL       │ │
│  │                 │  │                 │ │ Builder      │ │
│  └─────────────────┘  └─────────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                 Infrastructure Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐ ┌──────────────┐ │
│  │ Cache Manager   │  │ SPARQL Client   │ │ File System  │ │
│  │                 │  │                 │ │ Manager      │ │
│  └─────────────────┘  └─────────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. CLI Interface Layer

#### 1.1 Interactive CLI Component
**Responsibility**: Provide REPL interface for continuous querying
```python
class InteractiveCLI:
    def __init__(self, query_service: QueryService):
        self.query_service = query_service
        self.session = Session()
    
    def run(self) -> None:
        """Main REPL loop"""
    
    def process_command(self, input: str) -> None:
        """Handle user input and commands"""
    
    def display_results(self, result: QueryResult) -> None:
        """Format and display query results"""
```

#### 1.2 Command CLI Component
**Responsibility**: Handle single-command execution
```python
class CommandCLI:
    def __init__(self, query_service: QueryService):
        self.query_service = query_service
    
    def execute(self, args: CLIArgs) -> int:
        """Execute single query and return exit code"""
    
    def parse_arguments(self, argv: list[str]) -> CLIArgs:
        """Parse command line arguments"""
```

### 2. Application Service Layer

#### 2.1 Query Service
**Responsibility**: Orchestrate query processing pipeline
```python
class QueryService:
    def __init__(self, 
                 grammar_engine: GrammarEngine,
                 pattern_matcher: PatternMatcher,
                 sparql_builder: SPARQLBuilder,
                 sparql_client: SPARQLClient,
                 result_formatter: ResultFormatter):
        self.grammar_engine = grammar_engine
        self.pattern_matcher = pattern_matcher
        self.sparql_builder = sparql_builder
        self.sparql_client = sparql_client
        self.result_formatter = result_formatter
    
    def process_query(self, 
                     input_text: str, 
                     profile: str = None,
                     debug: bool = False) -> QueryResponse:
        """Main query processing pipeline"""
        
    def suggest_queries(self, partial_input: str) -> list[str]:
        """Generate query suggestions"""
```

#### 2.2 Configuration Manager
**Responsibility**: Manage profiles, credentials, and settings
```python
class ConfigurationManager:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.profiles: dict[str, Profile] = {}
        self.settings: GlobalSettings = None
    
    def load_configuration(self) -> None:
        """Load all configuration files"""
    
    def get_profile(self, name: str) -> Profile:
        """Get specific profile configuration"""
    
    def save_profile(self, profile: Profile) -> None:
        """Save profile to configuration"""
```

### 3. Core Business Layer

#### 3.1 Grammar Engine
**Responsibility**: Parse OWL and generate query patterns
```python
class GrammarEngine:
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.ontology_parser = OntologyParser()
        self.pattern_generator = PatternGenerator()
    
    def load_grammar(self, ontology_path: Path) -> Grammar:
        """Load or generate grammar from ontology"""
    
    def generate_patterns(self, ontology: Ontology) -> list[Pattern]:
        """Generate query patterns from ontology structure"""
```

#### 3.2 Pattern Matcher
**Responsibility**: Match user input to query patterns
```python
class PatternMatcher:
    def __init__(self, similarity_threshold: float = 0.7):
        self.similarity_threshold = similarity_threshold
    
    def find_matches(self, input_text: str, grammar: Grammar) -> list[MatchResult]:
        """Find matching patterns for user input"""
    
    def extract_entities(self, input_text: str, pattern: Pattern) -> dict[str, str]:
        """Extract entity values from matched pattern"""
```

#### 3.3 SPARQL Builder
**Responsibility**: Generate SPARQL from matched patterns
```python
class SPARQLBuilder:
    def __init__(self, namespaces: dict[str, str]):
        self.namespaces = namespaces
    
    def build_query(self, match_result: MatchResult) -> str:
        """Generate SPARQL from pattern match"""
    
    def optimize_query(self, sparql: str) -> str:
        """Apply SPARQL optimizations"""
```

### 4. Infrastructure Layer

#### 4.1 SPARQL Client
**Responsibility**: Execute queries against SPARQL endpoints
```python
class SPARQLClient:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
    
    def execute(self, 
               sparql_query: str, 
               endpoint: Endpoint) -> QueryResult:
        """Execute SPARQL query against endpoint"""
    
    def test_connection(self, endpoint: Endpoint) -> bool:
        """Test endpoint connectivity"""
```

#### 4.2 Cache Manager
**Responsibility**: Manage grammar and result caching
```python
class CacheManager:
    def __init__(self, cache_dir: Path, max_size: int = 50_000_000):
        self.cache_dir = cache_dir
        self.max_size = max_size
        self.current_size = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve cached item"""
    
    def put(self, key: str, value: Any, ttl: int = None) -> None:
        """Store item in cache"""
    
    def evict_lru(self) -> None:
        """Evict least recently used items"""
```

## Data Flow Architecture

### Query Processing Pipeline
```
User Input
    │
    ▼
┌─────────────────┐
│  Input          │
│  Validation     │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Pattern        │  ──► Grammar Cache
│  Matching       │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Entity         │
│  Extraction     │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  SPARQL         │
│  Generation     │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Query          │  ──► SPARQL Endpoint
│  Execution      │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Result         │
│  Formatting     │
└─────────────────┘
    │
    ▼
Display to User
```

### Configuration Loading Flow
```
Application Start
    │
    ▼
┌─────────────────┐
│  Detect XDG     │
│  Directories    │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Load Global    │  ──► config.yaml
│  Configuration  │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Load Profile   │  ──► profiles/*.yaml
│  Configurations │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Substitute     │  ──► Environment Variables
│  Variables      │
└─────────────────┘
    │
    ▼
Configuration Ready
```

## Module Dependencies

### Dependency Graph
```
kb_query.cli
├── kb_query.services.query
├── kb_query.services.config
└── kb_query.formatters.result

kb_query.services.query
├── kb_query.core.grammar
├── kb_query.core.matcher
├── kb_query.core.builder
└── kb_query.infrastructure.sparql

kb_query.core.grammar
├── kb_query.parsers.ontology
├── kb_query.generators.pattern
└── kb_query.infrastructure.cache

kb_query.infrastructure.sparql
└── kb_query.infrastructure.cache
```

### Package Structure
```
kb_query/
├── __init__.py
├── cli/
│   ├── __init__.py
│   ├── interactive.py
│   ├── command.py
│   └── args.py
├── services/
│   ├── __init__.py
│   ├── query.py
│   ├── config.py
│   └── suggestion.py
├── core/
│   ├── __init__.py
│   ├── grammar.py
│   ├── matcher.py
│   ├── builder.py
│   └── entities.py
├── infrastructure/
│   ├── __init__.py
│   ├── sparql.py
│   ├── cache.py
│   └── filesystem.py
├── formatters/
│   ├── __init__.py
│   ├── table.py
│   ├── json.py
│   └── debug.py
├── parsers/
│   ├── __init__.py
│   ├── ontology.py
│   └── query.py
├── generators/
│   ├── __init__.py
│   └── pattern.py
└── exceptions.py
```

## Interface Contracts

### Core Service Interface
```python
class QueryServiceInterface(Protocol):
    def process_query(self, 
                     input_text: str, 
                     profile: str = None,
                     debug: bool = False) -> QueryResponse:
        """Process natural language query"""
        ...
    
    def suggest_queries(self, partial_input: str) -> list[str]:
        """Generate query suggestions"""
        ...
    
    def list_patterns(self, class_filter: str = None) -> list[Pattern]:
        """List available query patterns"""
        ...
```

### Configuration Interface
```python
class ConfigurationInterface(Protocol):
    def get_profile(self, name: str) -> Profile:
        """Get profile configuration"""
        ...
    
    def list_profiles(self) -> list[str]:
        """List available profiles"""
        ...
    
    def validate_configuration(self) -> ValidationResult:
        """Validate configuration files"""
        ...
```

## Error Handling Architecture

### Error Flow
```
Component Error
    │
    ▼
┌─────────────────┐
│  Error          │
│  Classification │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Context        │
│  Enhancement    │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Suggestion     │
│  Generation     │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  User-Friendly  │
│  Message        │
└─────────────────┘
```

### Exception Hierarchy
```python
class KBQueryException(Exception):
    """Base exception"""

class ConfigurationError(KBQueryException):
    """Configuration-related errors"""

class GrammarError(KBQueryException):
    """Grammar processing errors"""

class QueryParseError(KBQueryException):
    """Query parsing errors"""
    def __init__(self, message: str, suggestions: list[str] = None):
        super().__init__(message)
        self.suggestions = suggestions or []

class SPARQLError(KBQueryException):
    """SPARQL execution errors"""

class EndpointError(KBQueryException):
    """Endpoint connectivity errors"""
```

## Performance Architecture

### Caching Strategy
- **Grammar Cache**: Persistent, LRU eviction, 50MB limit
- **Result Cache**: Optional, in-memory, TTL-based
- **Pattern Cache**: In-memory, loaded at startup

### Async Architecture
```python
# For concurrent endpoint querying (future enhancement)
class AsyncSPARQLClient:
    async def execute_concurrent(self, 
                               sparql_query: str, 
                               endpoints: list[Endpoint]) -> dict[str, QueryResult]:
        """Execute query against multiple endpoints"""
```

## Security Architecture

### Credential Management
- Credentials encrypted at rest using system keyring
- Environment variable substitution
- No plain-text passwords in memory longer than necessary

### Input Validation
- SPARQL injection prevention
- Input sanitization
- Query complexity limits

## Testing Architecture

### Test Strategy
```python
# Unit Tests
class TestPatternMatcher:
    def test_exact_match(self): ...
    def test_fuzzy_match(self): ...
    def test_entity_extraction(self): ...

# Integration Tests  
class TestQueryService:
    def test_end_to_end_flow(self): ...
    def test_error_handling(self): ...

# E2E Tests
class TestCLI:
    def test_interactive_mode(self): ...
    def test_command_mode(self): ...
```

### Mock Strategy
- Mock SPARQL endpoints for testing
- In-memory configuration for tests
- Deterministic pattern generation

## Deployment Architecture

### Entry Points
```python
# setup.py entry points
entry_points={
    'console_scripts': [
        'kb-query=kb_query.cli.main:main',
    ],
}
```

### Configuration Initialization
```bash
# First run initialization
kb-query --init
# Creates ~/.config/kb-query/ structure
```

This architecture provides a solid foundation for the MVP while maintaining extensibility for future enhancements.