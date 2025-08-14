"""Core data structures for KB Query CLI."""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from ..exceptions import ValidationError


@dataclass
class Pattern:
    """Represents a query pattern with template and SPARQL mapping."""
    
    id: str
    template: str
    sparql_template: str
    entity_types: Dict[str, str]
    examples: List[str]
    confidence: float
    domain_class: str
    property: str
    keywords: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize derived fields and validate."""
        self.keywords = self._extract_keywords()
        self.validate()
    
    def validate(self) -> None:
        """Validate pattern structure."""
        if not self.id:
            raise ValidationError("Pattern ID cannot be empty")
        
        if not self._has_entity_placeholders():
            raise ValidationError(f"Pattern {self.id} has no entity placeholders")
        
        if not (0.0 <= self.confidence <= 1.0):
            raise ValidationError(f"Pattern {self.id} confidence must be between 0.0 and 1.0")
        
        if not self.examples:
            raise ValidationError(f"Pattern {self.id} must have at least one example")
        
        if not self.sparql_template.strip():
            raise ValidationError(f"Pattern {self.id} must have SPARQL template")
    
    def _has_entity_placeholders(self) -> bool:
        """Check if template contains {entity} placeholders."""
        return bool(re.search(r'\{[^}]+\}', self.template))
    
    def _extract_keywords(self) -> List[str]:
        """Extract keywords from template (excluding placeholders)."""
        # Remove placeholders and extract words
        text = re.sub(r'\{[^}]+\}', '', self.template)
        words = [word.lower().strip() for word in text.split() if word.strip()]
        # Filter out common stop words and short words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an'}
        return [word for word in words if len(word) > 2 and word not in stop_words]


@dataclass
class Grammar:
    """Collection of patterns with metadata."""
    
    patterns: List[Pattern]
    ontology_hash: str
    namespaces: Dict[str, str]
    created_at: str
    
    def __post_init__(self):
        """Validate grammar after creation."""
        self.validate()
    
    def validate(self) -> None:
        """Validate grammar structure."""
        if not self.patterns:
            raise ValidationError("Grammar must contain at least one pattern")
        
        if not self.ontology_hash:
            raise ValidationError("Grammar must have ontology hash")
        
        # Check for duplicate pattern IDs
        pattern_ids = [p.id for p in self.patterns]
        if len(pattern_ids) != len(set(pattern_ids)):
            raise ValidationError("Grammar contains duplicate pattern IDs")
    
    def find_patterns_by_keyword(self, keyword: str) -> List[Pattern]:
        """Find patterns containing the specified keyword."""
        keyword = keyword.lower()
        return [p for p in self.patterns if keyword in p.keywords]
    
    def get_pattern_by_id(self, pattern_id: str) -> Optional[Pattern]:
        """Get pattern by ID."""
        for pattern in self.patterns:
            if pattern.id == pattern_id:
                return pattern
        return None


@dataclass
class MatchResult:
    """Result of matching user input to a pattern."""
    
    pattern: Pattern
    confidence: float
    entities: Dict[str, str]
    match_type: str  # "exact", "fuzzy", "partial"
    
    def __post_init__(self):
        """Validate match result."""
        if not (0.0 <= self.confidence <= 1.0):
            raise ValidationError("Match confidence must be between 0.0 and 1.0")
        
        if self.match_type not in ["exact", "fuzzy", "partial"]:
            raise ValidationError(f"Invalid match type: {self.match_type}")


@dataclass
class QueryRequest:
    """Request for query processing."""
    
    input_text: str
    profile: Optional[str] = None
    debug: bool = False
    show_sparql: bool = False
    limit: Optional[int] = None
    named_graphs: Optional[List[str]] = None
    default_graph: Optional[str] = None
    
    def __post_init__(self):
        """Validate request."""
        if not self.input_text.strip():
            raise ValidationError("Query input cannot be empty")
        
        if self.limit is not None and self.limit <= 0:
            raise ValidationError("Limit must be positive")


@dataclass
class QueryResponse:
    """Response from query processing."""
    
    success: bool
    sparql_query: Optional[str] = None
    results: Optional[List[Dict[str, Any]]] = None
    execution_time: float = 0.0
    error_message: Optional[str] = None
    suggestions: Optional[List[str]] = None
    debug_info: Optional[Dict[str, Any]] = None
    
    @property
    def result_count(self) -> int:
        """Get number of results."""
        return len(self.results) if self.results else 0


@dataclass
class SPARQLQuery:
    """Generated SPARQL query with metadata."""
    
    query_text: str
    variables: List[str]
    estimated_complexity: int = 1
    optimization_applied: bool = False
    
    def __post_init__(self):
        """Validate SPARQL query."""
        if not self.query_text.strip():
            raise ValidationError("SPARQL query text cannot be empty")


@dataclass
class Endpoint:
    """SPARQL endpoint configuration."""
    
    name: str
    url: str
    auth_type: str  # "none", "basic", "bearer"
    credentials: Dict[str, str]
    timeout: int = 30
    verify_ssl: bool = True
    
    def __post_init__(self):
        """Validate endpoint configuration."""
        if not self.name:
            raise ValidationError("Endpoint name cannot be empty")
        
        if not self.url:
            raise ValidationError("Endpoint URL cannot be empty")
        
        if self.auth_type not in ["none", "basic", "bearer"]:
            raise ValidationError(f"Invalid auth type: {self.auth_type}")
        
        if self.timeout <= 0:
            raise ValidationError("Timeout must be positive")
        
        # Validate required credentials based on auth type
        if self.auth_type == "basic":
            required = {"username", "password"}
            if not required.issubset(self.credentials.keys()):
                raise ValidationError(f"Basic auth requires: {required}")
        
        elif self.auth_type == "bearer":
            if "token" not in self.credentials:
                raise ValidationError("Bearer auth requires token")


@dataclass
class Profile:
    """User profile with endpoint and preferences."""
    
    name: str
    endpoint_url: str
    auth_type: str
    credentials: Dict[str, str]
    timeout: int = 30
    verify_ssl: bool = True
    description: Optional[str] = None
    
    def to_endpoint(self) -> Endpoint:
        """Convert profile to endpoint configuration."""
        return Endpoint(
            name=self.name,
            url=self.endpoint_url,
            auth_type=self.auth_type,
            credentials=self.credentials,
            timeout=self.timeout,
            verify_ssl=self.verify_ssl
        )


@dataclass
class GlobalSettings:
    """Global application settings."""
    
    default_profile: str
    debug: bool = False
    cache_enabled: bool = True
    timeout: int = 30
    max_results: int = 100
    
    def __post_init__(self):
        """Validate settings."""
        if not self.default_profile:
            raise ValidationError("Default profile must be specified")
        
        if self.timeout <= 0:
            raise ValidationError("Timeout must be positive")
        
        if self.max_results <= 0:
            raise ValidationError("Max results must be positive")