# SPARC Phase 3: Interface Specifications

## Core Service Interfaces

### 1. Query Service Interface
```python
from abc import ABC, abstractmethod
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class QueryRequest:
    input_text: str
    profile: Optional[str] = None
    debug: bool = False
    show_sparql: bool = False
    limit: Optional[int] = None

@dataclass  
class QueryResponse:
    success: bool
    sparql_query: Optional[str] = None
    results: Optional[List[dict]] = None
    execution_time: float = 0.0
    error_message: Optional[str] = None
    suggestions: List[str] = None
    debug_info: Optional[dict] = None

class IQueryService(ABC):
    """Main service interface for query processing"""
    
    @abstractmethod
    def process_query(self, request: QueryRequest) -> QueryResponse:
        """Process a natural language query"""
        pass
    
    @abstractmethod
    def suggest_queries(self, partial_input: str) -> List[str]:
        """Generate query suggestions for partial input"""
        pass
    
    @abstractmethod
    def list_available_patterns(self, class_filter: Optional[str] = None) -> List[str]:
        """List available query patterns"""
        pass
    
    @abstractmethod
    def validate_configuration(self) -> bool:
        """Validate current configuration"""
        pass
```

### 2. Grammar Engine Interface
```python
@dataclass
class Pattern:
    id: str
    template: str
    sparql_template: str
    entity_types: dict[str, str]
    examples: List[str]
    confidence: float
    domain_class: str
    property: str

@dataclass
class Grammar:
    patterns: List[Pattern]
    ontology_hash: str
    namespaces: dict[str, str]
    created_at: str

class IGrammarEngine(ABC):
    """Interface for grammar processing and pattern generation"""
    
    @abstractmethod
    def load_grammar(self, ontology_path: str) -> Grammar:
        """Load or generate grammar from ontology file"""
        pass
    
    @abstractmethod
    def generate_patterns(self, ontology_data: dict) -> List[Pattern]:
        """Generate query patterns from ontology structure"""
        pass
    
    @abstractmethod
    def cache_grammar(self, grammar: Grammar, cache_key: str) -> bool:
        """Cache grammar for future use"""
        pass
    
    @abstractmethod
    def invalidate_cache(self, ontology_path: str) -> None:
        """Invalidate cached grammar"""
        pass
```

### 3. Pattern Matcher Interface
```python
@dataclass
class MatchResult:
    pattern: Pattern
    confidence: float
    entities: dict[str, str]
    match_type: str  # "exact", "fuzzy", "partial"

class IPatternMatcher(ABC):
    """Interface for matching user input to query patterns"""
    
    @abstractmethod
    def find_matches(self, input_text: str, grammar: Grammar) -> List[MatchResult]:
        """Find matching patterns for user input"""
        pass
    
    @abstractmethod
    def extract_entities(self, input_text: str, pattern: Pattern) -> dict[str, str]:
        """Extract entity values from matched pattern"""
        pass
    
    @abstractmethod
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings"""
        pass
    
    @abstractmethod
    def suggest_corrections(self, input_text: str, grammar: Grammar) -> List[str]:
        """Suggest corrections for failed matches"""
        pass
```

### 4. SPARQL Builder Interface
```python
@dataclass
class SPARQLQuery:
    query_text: str
    variables: List[str]
    estimated_complexity: int
    optimization_applied: bool

class ISPARQLBuilder(ABC):
    """Interface for building SPARQL queries"""
    
    @abstractmethod
    def build_query(self, match_result: MatchResult, namespaces: dict[str, str]) -> SPARQLQuery:
        """Generate SPARQL query from pattern match"""
        pass
    
    @abstractmethod
    def optimize_query(self, sparql: str) -> str:
        """Apply query optimizations"""
        pass
    
    @abstractmethod
    def validate_sparql(self, sparql: str) -> bool:
        """Validate SPARQL syntax"""
        pass
    
    @abstractmethod
    def add_limit(self, sparql: str, limit: int) -> str:
        """Add LIMIT clause to SPARQL query"""
        pass
```

### 5. SPARQL Client Interface
```python
@dataclass
class Endpoint:
    name: str
    url: str
    auth_type: str
    credentials: dict
    timeout: int
    verify_ssl: bool

@dataclass
class ExecutionResult:
    success: bool
    data: Optional[dict] = None
    execution_time: float = 0.0
    status_code: Optional[int] = None
    error_message: Optional[str] = None

class ISPARQLClient(ABC):
    """Interface for SPARQL endpoint communication"""
    
    @abstractmethod
    def execute_query(self, sparql: str, endpoint: Endpoint) -> ExecutionResult:
        """Execute SPARQL query against endpoint"""
        pass
    
    @abstractmethod
    def test_connection(self, endpoint: Endpoint) -> bool:
        """Test connectivity to SPARQL endpoint"""
        pass
    
    @abstractmethod
    def get_endpoint_info(self, endpoint: Endpoint) -> dict:
        """Get endpoint metadata and capabilities"""
        pass
```

### 6. Configuration Manager Interface
```python
@dataclass
class Profile:
    name: str
    endpoint_url: str
    auth_type: str
    credentials: dict
    timeout: int
    verify_ssl: bool
    description: Optional[str] = None

@dataclass
class GlobalSettings:
    default_profile: str
    debug: bool
    cache_enabled: bool
    timeout: int
    max_results: int

class IConfigurationManager(ABC):
    """Interface for configuration management"""
    
    @abstractmethod
    def load_configuration(self) -> GlobalSettings:
        """Load global configuration"""
        pass
    
    @abstractmethod
    def get_profile(self, name: str) -> Profile:
        """Get specific profile configuration"""
        pass
    
    @abstractmethod
    def list_profiles(self) -> List[str]:
        """List all available profiles"""
        pass
    
    @abstractmethod
    def save_profile(self, profile: Profile) -> bool:
        """Save profile configuration"""
        pass
    
    @abstractmethod
    def delete_profile(self, name: str) -> bool:
        """Delete profile configuration"""
        pass
    
    @abstractmethod
    def validate_profile(self, profile: Profile) -> List[str]:
        """Validate profile configuration, return error messages"""
        pass
```

### 7. Cache Manager Interface
```python
@dataclass
class CacheStats:
    total_entries: int
    total_size_bytes: int
    hit_rate: float
    miss_rate: float
    evictions: int

class ICacheManager(ABC):
    """Interface for caching functionality"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[any]:
        """Retrieve cached value"""
        pass
    
    @abstractmethod
    def put(self, key: str, value: any, ttl: Optional[int] = None) -> bool:
        """Store value in cache"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Remove value from cache"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cached values"""
        pass
    
    @abstractmethod
    def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        pass
    
    @abstractmethod
    def evict_lru(self, count: int) -> List[str]:
        """Evict least recently used entries"""
        pass
```

### 8. Result Formatter Interface
```python
@dataclass
class FormattingOptions:
    format_type: str  # "table", "json", "csv"
    max_width: int
    show_headers: bool
    truncate_long_values: bool
    max_rows: Optional[int] = None

class IResultFormatter(ABC):
    """Interface for formatting query results"""
    
    @abstractmethod
    def format_results(self, results: List[dict], options: FormattingOptions) -> str:
        """Format query results for display"""
        pass
    
    @abstractmethod
    def format_error(self, error_message: str, suggestions: List[str]) -> str:
        """Format error message with suggestions"""
        pass
    
    @abstractmethod
    def format_debug_info(self, debug_data: dict) -> str:
        """Format debug information"""
        pass
    
    @abstractmethod
    def calculate_column_widths(self, data: List[dict], max_width: int) -> dict[str, int]:
        """Calculate optimal column widths for table display"""
        pass
```

## CLI Interfaces

### 9. CLI Base Interface
```python
from enum import Enum

class ExitCode(Enum):
    SUCCESS = 0
    CONFIGURATION_ERROR = 1
    QUERY_ERROR = 2
    NETWORK_ERROR = 3
    AUTHENTICATION_ERROR = 4
    UNKNOWN_ERROR = 5

@dataclass
class CLIArguments:
    query: Optional[str] = None
    profile: Optional[str] = None
    show_sparql: bool = False
    debug: bool = False
    interactive: bool = False
    init: bool = False
    list_profiles: bool = False
    test_connection: bool = False

class ICLIInterface(ABC):
    """Base interface for CLI implementations"""
    
    @abstractmethod
    def run(self, args: CLIArguments) -> ExitCode:
        """Main entry point for CLI execution"""
        pass
    
    @abstractmethod
    def display_results(self, response: QueryResponse) -> None:
        """Display query results to user"""
        pass
    
    @abstractmethod
    def display_error(self, error: str, suggestions: List[str]) -> None:
        """Display error message with suggestions"""
        pass
```

### 10. Interactive CLI Interface
```python
@dataclass
class SessionState:
    current_profile: str
    debug_mode: bool
    show_sparql: bool
    history: List[str]

class IInteractiveCLI(ICLIInterface):
    """Interface for interactive CLI mode"""
    
    @abstractmethod
    def start_repl(self) -> ExitCode:
        """Start interactive REPL loop"""
        pass
    
    @abstractmethod
    def process_input(self, user_input: str, session: SessionState) -> None:
        """Process user input in interactive mode"""
        pass
    
    @abstractmethod
    def handle_command(self, command: str, session: SessionState) -> bool:
        """Handle special commands (e.g., .help, .debug)"""
        pass
    
    @abstractmethod
    def show_help(self) -> None:
        """Display interactive mode help"""
        pass
```

## Factory Interfaces

### 11. Service Factory Interface
```python
class IServiceFactory(ABC):
    """Factory for creating service instances"""
    
    @abstractmethod
    def create_query_service(self, config_path: Optional[str] = None) -> IQueryService:
        """Create configured query service instance"""
        pass
    
    @abstractmethod
    def create_grammar_engine(self, cache_dir: str) -> IGrammarEngine:
        """Create grammar engine instance"""
        pass
    
    @abstractmethod
    def create_pattern_matcher(self, similarity_threshold: float = 0.7) -> IPatternMatcher:
        """Create pattern matcher instance"""
        pass
    
    @abstractmethod
    def create_sparql_builder(self, namespaces: dict[str, str]) -> ISPARQLBuilder:
        """Create SPARQL builder instance"""
        pass
```

## Error Interfaces

### 12. Error Handler Interface
```python
@dataclass
class ErrorContext:
    original_input: str
    error_type: str
    component: str
    timestamp: str
    debug_info: dict

class IErrorHandler(ABC):
    """Interface for error handling and recovery"""
    
    @abstractmethod
    def handle_error(self, error: Exception, context: ErrorContext) -> QueryResponse:
        """Handle and recover from errors"""
        pass
    
    @abstractmethod
    def generate_suggestions(self, error: Exception, context: ErrorContext) -> List[str]:
        """Generate helpful suggestions for errors"""
        pass
    
    @abstractmethod
    def classify_error(self, error: Exception) -> str:
        """Classify error type for appropriate handling"""
        pass
```

## Validation Interfaces

### 13. Input Validator Interface
```python
@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    sanitized_input: Optional[str] = None

class IInputValidator(ABC):
    """Interface for input validation and sanitization"""
    
    @abstractmethod
    def validate_query_input(self, input_text: str) -> ValidationResult:
        """Validate user query input"""
        pass
    
    @abstractmethod
    def validate_sparql(self, sparql: str) -> ValidationResult:
        """Validate generated SPARQL"""
        pass
    
    @abstractmethod
    def sanitize_input(self, input_text: str) -> str:
        """Sanitize input to prevent injection attacks"""
        pass
```

## Plugin Interfaces (Future Extension)

### 14. Plugin Interface
```python
class IPlugin(ABC):
    """Base interface for plugins"""
    
    @abstractmethod
    def get_name(self) -> str:
        """Get plugin name"""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Get plugin version"""
        pass
    
    @abstractmethod
    def initialize(self, config: dict) -> bool:
        """Initialize plugin"""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup plugin resources"""
        pass

class IFormatterPlugin(IPlugin):
    """Interface for custom result formatters"""
    
    @abstractmethod
    def format_results(self, results: List[dict], options: dict) -> str:
        """Format results using custom formatter"""
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Get list of supported format types"""
        pass
```

These interfaces provide clear contracts between components, enabling:
- **Testability**: Easy mocking and stubbing
- **Extensibility**: Plugin architecture support
- **Maintainability**: Clear separation of concerns
- **Type Safety**: Strong typing with dataclasses
- **Documentation**: Self-documenting interface contracts