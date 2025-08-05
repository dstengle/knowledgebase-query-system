"""KB Query Interface - Natural language queries for RDF knowledge bases"""

from .query_engine import KBQueryEngine
from .exceptions import QueryParseError, OntologyError

__version__ = "0.1.0"
__all__ = ["KBQueryEngine", "QueryParseError", "OntologyError"]
