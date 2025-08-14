"""Query Service for orchestrating query processing."""

import time
from typing import List, Optional, Dict, Any
from pathlib import Path

from ..core.entities import QueryRequest, QueryResponse, Grammar
from ..core.grammar import GrammarEngine
from ..core.matcher import PatternMatcher
from ..core.builder import SPARQLBuilder
from ..exceptions import KBQueryException, QueryParseError


class QueryService:
    """Main service for processing natural language queries."""
    
    def __init__(self, 
                 ontology_path: str,
                 namespaces: Optional[Dict[str, str]] = None,
                 cache_manager: Optional[Any] = None,
                 config: Optional[Dict[str, Any]] = None):
        """Initialize query service with ontology."""
        self.ontology_path = Path(ontology_path)
        self.namespaces = namespaces or {}
        self.config = config or {}
        
        # Initialize components
        self.grammar_engine = GrammarEngine(cache_manager=cache_manager)
        self.pattern_matcher = PatternMatcher(similarity_threshold=0.7)
        self.sparql_builder = SPARQLBuilder(namespaces=self.namespaces)
        
        # Load grammar
        self.grammar: Optional[Grammar] = None
        self._load_grammar()
    
    def process_query(self, request: QueryRequest) -> QueryResponse:
        """Process a natural language query."""
        start_time = time.time()
        
        try:
            # Find matching patterns
            matches = self.pattern_matcher.find_matches(request.input_text, self.grammar)
            
            if not matches:
                # No matches found - generate suggestions
                suggestions = self.pattern_matcher.suggest_corrections(
                    request.input_text, 
                    self.grammar
                )
                
                return QueryResponse(
                    success=False,
                    error_message=f"Could not understand query: {request.input_text}",
                    suggestions=suggestions,
                    execution_time=time.time() - start_time
                )
            
            # Use best match
            best_match = matches[0]
            
            # Build SPARQL query with graph specifications
            sparql_query = self.sparql_builder.build_query(
                best_match,
                named_graphs=request.named_graphs,
                default_graph=request.default_graph
            )
            
            # Apply limit if requested
            if request.limit:
                sparql_query.query_text = self.sparql_builder.add_limit(
                    sparql_query.query_text, 
                    request.limit
                )
            
            # Prepare debug info if requested
            debug_info = None
            if request.debug:
                debug_info = {
                    'matched_pattern': best_match.pattern.template,
                    'confidence': best_match.confidence,
                    'match_type': best_match.match_type,
                    'extracted_entities': best_match.entities,
                    'pattern_id': best_match.pattern.id,
                    'sparql_complexity': sparql_query.estimated_complexity
                }
            
            return QueryResponse(
                success=True,
                sparql_query=sparql_query.query_text if request.show_sparql or request.debug else None,
                execution_time=time.time() - start_time,
                debug_info=debug_info
            )
            
        except Exception as e:
            return QueryResponse(
                success=False,
                error_message=str(e),
                execution_time=time.time() - start_time
            )
    
    def suggest_queries(self, partial_input: str) -> List[str]:
        """Generate query suggestions for partial input."""
        suggestions = []
        
        # Find patterns with matching keywords
        input_lower = partial_input.lower()
        for pattern in self.grammar.patterns:
            # Check if any keyword starts with the input
            for keyword in pattern.keywords:
                if keyword.startswith(input_lower) or input_lower in keyword:
                    suggestions.extend(pattern.examples[:1])
                    break
        
        # Remove duplicates
        seen = set()
        unique_suggestions = []
        for s in suggestions:
            if s not in seen:
                seen.add(s)
                unique_suggestions.append(s)
        
        return unique_suggestions[:10]
    
    def list_available_patterns(self, class_filter: Optional[str] = None) -> List[str]:
        """List available query patterns."""
        patterns = []
        
        for pattern in self.grammar.patterns:
            if class_filter:
                if class_filter.lower() not in pattern.domain_class.lower():
                    continue
            
            # Add pattern template and examples
            patterns.append(f"Pattern: {pattern.template}")
            for example in pattern.examples[:2]:
                patterns.append(f"  Example: {example}")
        
        return patterns
    
    def validate_configuration(self) -> bool:
        """Validate current configuration."""
        try:
            # Check ontology file exists
            if not self.ontology_path.exists():
                return False
            
            # Check grammar is loaded
            if not self.grammar or not self.grammar.patterns:
                return False
            
            return True
        except Exception:
            return False
    
    def _load_grammar(self):
        """Load grammar from ontology."""
        try:
            self.grammar = self.grammar_engine.load_grammar(str(self.ontology_path))
        except Exception as e:
            raise KBQueryException(f"Failed to load grammar: {str(e)}")