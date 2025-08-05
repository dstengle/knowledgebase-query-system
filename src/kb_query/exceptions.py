"""Custom exceptions for KB Query Interface"""

class KBQueryError(Exception):
    """Base exception for KB Query Interface"""
    pass

class OntologyError(KBQueryError):
    """Raised when there's an error parsing the ontology"""
    pass

class QueryParseError(KBQueryError):
    """Raised when a query cannot be parsed"""
    def __init__(self, message: str, suggestions: list = None):
        super().__init__(message)
        self.suggestions = suggestions or []
