"""Main query engine that coordinates all components"""

import logging
import yaml
from typing import List, Dict, Optional
from pathlib import Path

from .ontology_parser import OntologyParser
from .pattern_generator import AutomaticPatternGenerator
from .query_parser import NaturalLanguageQueryParser
from .sparql_builder import SPARQLBuilder
from .interfaces import QueryPattern
from .exceptions import KBQueryError

logger = logging.getLogger(__name__)

class KBQueryEngine:
    """Main engine for natural language to SPARQL conversion"""
    
    def __init__(self, ontology_path: str, config_path: Optional[str] = None):
        """
        Initialize query engine with ontology
        
        Args:
            ontology_path: Path to OWL/RDF ontology file
            config_path: Optional path to configuration file
        """
        self.config = self._load_config(config_path)
        
        # Initialize components
        self.ontology_parser = OntologyParser()
        self.pattern_generator = AutomaticPatternGenerator()
        self.query_parser = NaturalLanguageQueryParser()
        self.sparql_builder = SPARQLBuilder(
            default_limit=self.config.get('query', {}).get('limit_default', 100)
        )
        
        # Parse ontology and generate patterns
        self._initialize(ontology_path)
    
    def query(self, natural_language_query: str) -> Dict:
        """
        Convert natural language query to SPARQL and optionally execute
        
        Args:
            natural_language_query: Query in natural language
            
        Returns:
            Dict with 'sparql' and optionally 'results'
        """
        try:
            # Parse the natural language query
            parsed = self.query_parser.parse(
                natural_language_query, 
                self.patterns
            )
            
            # Build SPARQL
            sparql = self.sparql_builder.build(
                parsed,
                self.namespaces
            )
            
            result = {
                'sparql': sparql,
                'parsed': {
                    'entity_type': parsed.entity_type,
                    'filters': parsed.filters,
                    'temporal': parsed.temporal_constraints
                }
            }
            
            # Execute if endpoint configured
            if self.config.get('sparql', {}).get('endpoint'):
                result['results'] = self._execute_sparql(sparql)
            
            return result
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise
    
    def get_patterns_for_class(self, class_name: str) -> List[str]:
        """Get all query patterns for a specific class"""
        patterns = []
        for pattern in self.patterns:
            if class_name.lower() in pattern.pattern.lower():
                patterns.extend(pattern.examples)
        return patterns
    
    def suggest_queries(self, partial: str) -> List[str]:
        """Get query suggestions for partial input"""
        return self.query_parser.suggest_queries(partial, self.patterns)
    
    def _initialize(self, ontology_path: str):
        """Initialize engine by parsing ontology and generating patterns"""
        logger.info(f"Initializing KB Query Engine with {ontology_path}")
        
        # Parse ontology
        self.classes = self.ontology_parser.parse(ontology_path)
        self.properties = self.ontology_parser.get_properties()
        self.namespaces = self.ontology_parser.get_namespaces()
        
        # Check for cached patterns
        cache_path = self.config.get('patterns', {}).get('cache_path')
        if cache_path and Path(cache_path).exists():
            self.patterns = self._load_cached_patterns(cache_path)
        else:
            # Generate patterns
            self.patterns = self.pattern_generator.generate_patterns(
                self.classes,
                self.properties
            )
            
            # Cache if enabled
            if cache_path:
                self._cache_patterns(self.patterns, cache_path)
        
        logger.info(f"Initialized with {len(self.classes)} classes, "
                   f"{len(self.properties)} properties, "
                   f"{len(self.patterns)} patterns")
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file or use defaults"""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f).get('kb_query', {})
        
        # Default configuration
        return {
            'query': {
                'limit_default': 100,
                'enable_suggestions': True
            },
            'patterns': {
                'cache_enabled': True
            }
        }
    
    def _load_cached_patterns(self, cache_path: str) -> List[QueryPattern]:
        """Load patterns from cache"""
        # Implementation depends on serialization format
        logger.info(f"Loading cached patterns from {cache_path}")
        # TODO: Implement pattern deserialization
        return []
    
    def _cache_patterns(self, patterns: List[QueryPattern], cache_path: str):
        """Cache generated patterns"""
        # Implementation depends on serialization format
        logger.info(f"Caching {len(patterns)} patterns to {cache_path}")
        # TODO: Implement pattern serialization
    
    def _execute_sparql(self, sparql: str) -> List[Dict]:
        """Execute SPARQL query against endpoint"""
        # TODO: Implement SPARQL execution
        endpoint = self.config.get('sparql', {}).get('endpoint')
        logger.info(f"Would execute against {endpoint}")
        return []
