"""Exception classes for KB Query CLI."""

from typing import List, Optional


class KBQueryException(Exception):
    """Base exception for all KB Query errors."""
    pass


class ValidationError(KBQueryException):
    """Raised when validation fails."""
    pass


class ConfigurationError(KBQueryException):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str, config_file: Optional[str] = None):
        super().__init__(message)
        self.config_file = config_file


class GrammarError(KBQueryException):
    """Raised when grammar processing fails."""
    
    def __init__(self, message: str, ontology_file: Optional[str] = None):
        super().__init__(message)
        self.ontology_file = ontology_file


class QueryParseError(KBQueryException):
    """Raised when query parsing fails."""
    
    def __init__(self, message: str, query: str, suggestions: Optional[List[str]] = None):
        super().__init__(message)
        self.query = query
        self.suggestions = suggestions or []


class SPARQLError(KBQueryException):
    """Raised when SPARQL execution fails."""
    
    def __init__(self, message: str, sparql_query: Optional[str] = None, status_code: Optional[int] = None):
        super().__init__(message)
        self.sparql_query = sparql_query
        self.status_code = status_code


class EndpointConnectionError(KBQueryException):
    """Raised when endpoint connection fails."""
    
    def __init__(self, message: str, endpoint_url: str):
        super().__init__(message)
        self.endpoint_url = endpoint_url


class AuthenticationError(KBQueryException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str, endpoint_url: str):
        super().__init__(message)
        self.endpoint_url = endpoint_url


class CacheError(KBQueryException):
    """Raised when cache operations fail."""
    pass


class QueryTimeoutError(KBQueryException):
    """Raised when query execution times out."""
    
    def __init__(self, message: str, timeout_seconds: int):
        super().__init__(message)
        self.timeout_seconds = timeout_seconds