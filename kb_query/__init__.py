"""KB Query CLI - Natural Language SPARQL Interface."""

__version__ = "0.1.0"
__author__ = "KB Query Team"

from .core.entities import Pattern, Grammar, MatchResult, QueryRequest, QueryResponse

__all__ = [
    "Pattern",
    "Grammar", 
    "MatchResult",
    "QueryRequest",
    "QueryResponse",
]