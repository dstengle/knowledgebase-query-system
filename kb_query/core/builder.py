"""SPARQL Builder for query generation from patterns."""

import re
from typing import Dict, List, Optional
from ..core.entities import MatchResult, SPARQLQuery
from ..exceptions import SPARQLError


class SPARQLBuilder:
    """Builds SPARQL queries from matched patterns."""
    
    def __init__(self, namespaces: Optional[Dict[str, str]] = None):
        """Initialize SPARQL builder with namespaces."""
        self.namespaces = namespaces or {}
    
    def build_query(self, match_result: MatchResult, named_graphs: Optional[List[str]] = None, 
                    default_graph: Optional[str] = None) -> SPARQLQuery:
        """Generate SPARQL query from pattern match."""
        try:
            pattern = match_result.pattern
            entities = match_result.entities
            
            # Start with the SPARQL template
            sparql = pattern.sparql_template
            
            # Replace entity placeholders with actual values
            for entity_name, entity_value in entities.items():
                # Escape special characters in entity value
                escaped_value = self._escape_sparql_string(entity_value)
                # Replace {entity} placeholders in the SPARQL template
                sparql = sparql.replace(f"{{{entity_name}}}", escaped_value)
            
            # Add namespace prefixes if not already present
            sparql = self._add_namespaces(sparql)
            
            # Add graph clauses if specified
            if named_graphs or default_graph:
                sparql = self._add_graph_clauses(sparql, named_graphs, default_graph)
            
            # Extract variables from SELECT clause
            variables = self._extract_variables(sparql)
            
            # Validate the generated SPARQL
            if not self.validate_sparql(sparql):
                raise SPARQLError(f"Invalid SPARQL generated: {sparql[:100]}...")
            
            return SPARQLQuery(
                query_text=sparql,
                variables=variables,
                estimated_complexity=self._estimate_complexity(sparql),
                optimization_applied=False
            )
            
        except Exception as e:
            if isinstance(e, SPARQLError):
                raise
            raise SPARQLError(f"Failed to build SPARQL query: {str(e)}")
    
    def optimize_query(self, sparql: str) -> str:
        """Apply query optimizations to SPARQL."""
        # Basic optimization: ensure FILTER comes after triple patterns
        lines = sparql.split('\n')
        filters = []
        patterns = []
        other = []
        
        in_where = False
        for line in lines:
            line_stripped = line.strip()
            if 'WHERE' in line_stripped:
                in_where = True
                other.append(line)
            elif in_where and line_stripped.startswith('FILTER'):
                filters.append(line)
            elif in_where and (line_stripped.startswith('?') or line_stripped.startswith('<')):
                patterns.append(line)
            else:
                other.append(line)
        
        # Reconstruct with patterns before filters
        if filters and patterns:
            # Find WHERE clause position
            where_idx = next(i for i, line in enumerate(other) if 'WHERE' in line)
            result = other[:where_idx+1] + patterns + filters
            
            # Add remaining lines
            remaining_start = where_idx + 1
            while remaining_start < len(other) and other[remaining_start].strip() in ['', '}']:
                remaining_start += 1
            
            if remaining_start < len(other):
                result.extend(other[remaining_start:])
            
            return '\n'.join(result)
        
        return sparql
    
    def validate_sparql(self, sparql: str) -> bool:
        """Validate SPARQL syntax (basic validation)."""
        # Basic checks for valid SPARQL structure
        sparql_upper = sparql.upper()
        
        # Must have SELECT or other query form
        if not any(keyword in sparql_upper for keyword in ['SELECT', 'CONSTRUCT', 'ASK', 'DESCRIBE']):
            return False
        
        # Must have WHERE clause for SELECT
        if 'SELECT' in sparql_upper and 'WHERE' not in sparql_upper:
            return False
        
        # Check for balanced braces
        if sparql.count('{') != sparql.count('}'):
            return False
        
        # Check for balanced parentheses
        if sparql.count('(') != sparql.count(')'):
            return False
        
        return True
    
    def add_limit(self, sparql: str, limit: int) -> str:
        """Add LIMIT clause to SPARQL query."""
        # Remove existing LIMIT if present
        sparql = re.sub(r'\s+LIMIT\s+\d+\s*$', '', sparql, flags=re.IGNORECASE)
        
        # Add new LIMIT
        sparql = sparql.rstrip()
        if not sparql.endswith('}'):
            # Find the last closing brace
            last_brace = sparql.rfind('}')
            if last_brace != -1:
                sparql = sparql[:last_brace+1]
        
        return f"{sparql}\nLIMIT {limit}"
    
    def _escape_sparql_string(self, value: str) -> str:
        """Escape special characters in SPARQL string literals."""
        # Escape backslashes first
        value = value.replace('\\', '\\\\')
        # Escape quotes
        value = value.replace('"', '\\"')
        # Escape newlines and tabs
        value = value.replace('\n', '\\n')
        value = value.replace('\r', '\\r')
        value = value.replace('\t', '\\t')
        return value
    
    def _add_namespaces(self, sparql: str) -> str:
        """Add namespace prefixes to SPARQL query."""
        if not self.namespaces:
            return sparql
        
        # Check if prefixes already exist
        has_prefixes = 'PREFIX' in sparql.upper()
        
        if not has_prefixes:
            # Add prefixes at the beginning
            prefix_lines = []
            for prefix, uri in self.namespaces.items():
                prefix_lines.append(f"PREFIX {prefix}: <{uri}>")
            
            if prefix_lines:
                return '\n'.join(prefix_lines) + '\n' + sparql
        
        return sparql
    
    def _extract_variables(self, sparql: str) -> List[str]:
        """Extract variable names from SELECT clause."""
        variables = []
        
        # Find SELECT clause
        select_match = re.search(r'SELECT\s+(.*?)\s+WHERE', sparql, re.IGNORECASE | re.DOTALL)
        if select_match:
            select_clause = select_match.group(1)
            
            # Handle SELECT *
            if '*' in select_clause:
                # Extract all variables from WHERE clause
                where_vars = re.findall(r'\?(\w+)', sparql)
                # Unique variables
                seen = set()
                for var in where_vars:
                    if var not in seen:
                        variables.append(var)
                        seen.add(var)
            else:
                # Extract variables from SELECT clause
                var_matches = re.findall(r'\?(\w+)', select_clause)
                variables = list(dict.fromkeys(var_matches))  # Preserve order, remove duplicates
        
        return variables
    
    def _add_graph_clauses(self, sparql: str, named_graphs: Optional[List[str]], 
                           default_graph: Optional[str]) -> str:
        """Add GRAPH blocks inside WHERE clause for graph-specific queries."""
        if not named_graphs and not default_graph:
            return sparql
        
        # Find the WHERE clause content
        import re
        where_match = re.search(r'WHERE\s*\{(.*)\}', sparql, re.DOTALL | re.IGNORECASE)
        if not where_match:
            return sparql
        
        where_content = where_match.group(1).strip()
        
        # Determine which graphs to query
        graphs_to_query = []
        if default_graph:
            graphs_to_query.append(default_graph)
        if named_graphs:
            graphs_to_query.extend(named_graphs)
        
        # If only one graph, wrap content in GRAPH block
        if len(graphs_to_query) == 1:
            new_where = f"\n  GRAPH <{graphs_to_query[0]}> {{\n    {where_content}\n  }}\n"
        # If multiple graphs, use UNION
        elif len(graphs_to_query) > 1:
            graph_blocks = []
            for graph in graphs_to_query:
                # Indent the where_content properly for each GRAPH block
                indented_content = '\n    '.join(where_content.split('\n'))
                graph_blocks.append(f"  {{\n    GRAPH <{graph}> {{\n      {indented_content}\n    }}\n  }}")
            new_where = "\n" + "\n  UNION\n".join(graph_blocks) + "\n"
        else:
            return sparql
        
        # Replace the WHERE clause content
        new_sparql = sparql[:where_match.start()] + f"WHERE {{{new_where}}}" + sparql[where_match.end():]
        
        return new_sparql
    
    def _estimate_complexity(self, sparql: str) -> int:
        """Estimate query complexity (1=simple, 5=complex)."""
        complexity = 1
        
        # Count triple patterns
        triple_count = len(re.findall(r'\?[\w]+\s+[\w:]+\s+\?[\w]+', sparql))
        if triple_count > 3:
            complexity += 1
        if triple_count > 5:
            complexity += 1
        
        # Check for FILTER
        if 'FILTER' in sparql.upper():
            complexity += 1
        
        # Check for OPTIONAL
        if 'OPTIONAL' in sparql.upper():
            complexity += 1
        
        # Check for aggregation
        if any(func in sparql.upper() for func in ['COUNT', 'SUM', 'AVG', 'MIN', 'MAX']):
            complexity += 1
        
        return min(complexity, 5)