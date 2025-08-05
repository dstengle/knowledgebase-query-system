"""Core interfaces for the query system"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class OntologyClass:
    """Represents a class in the ontology"""
    uri: str
    local_name: str
    label: str
    comment: Optional[str]
    parents: List[str]
    properties: List[str]

@dataclass
class OntologyProperty:
    """Represents a property in the ontology"""
    uri: str
    local_name: str
    domain: Optional[str]
    range: Optional[str]
    comment: Optional[str]
    patterns: List[str]

@dataclass
class QueryPattern:
    """A natural language query pattern"""
    pattern: str  # e.g., "{class} with {value}"
    sparql_template: str
    required_class: str
    required_property: str
    examples: List[str]

@dataclass
class ParsedQuery:
    """Result of parsing a natural language query"""
    entity_type: str
    filters: Dict[str, str]
    temporal_constraints: Optional[Dict[str, str]]
    limit: Optional[int]
    order_by: Optional[Tuple[str, str]]  # (property, direction)

class IOntologyParser(ABC):
    """Interface for parsing ontologies"""
    
    @abstractmethod
    def parse(self, ontology_path: str) -> Dict[str, OntologyClass]:
        """Parse ontology and return classes"""
        pass
    
    @abstractmethod
    def get_properties(self) -> Dict[str, OntologyProperty]:
        """Get all properties from ontology"""
        pass
    
    @abstractmethod
    def get_namespaces(self) -> Dict[str, str]:
        """Get namespace mappings"""
        pass

class IPatternGenerator(ABC):
    """Interface for generating query patterns"""
    
    @abstractmethod
    def generate_patterns(self, 
                         classes: Dict[str, OntologyClass],
                         properties: Dict[str, OntologyProperty]) -> List[QueryPattern]:
        """Generate query patterns from ontology"""
        pass

class IQueryParser(ABC):
    """Interface for parsing natural language queries"""
    
    @abstractmethod
    def parse(self, query: str, patterns: List[QueryPattern]) -> ParsedQuery:
        """Parse natural language query"""
        pass
    
    @abstractmethod
    def suggest_queries(self, partial: str, patterns: List[QueryPattern]) -> List[str]:
        """Suggest completions for partial query"""
        pass

class ISPARQLBuilder(ABC):
    """Interface for building SPARQL queries"""
    
    @abstractmethod
    def build(self, parsed_query: ParsedQuery, namespaces: Dict[str, str]) -> str:
        """Build SPARQL from parsed query"""
        pass
