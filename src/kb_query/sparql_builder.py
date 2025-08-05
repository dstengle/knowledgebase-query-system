"""Build SPARQL queries from parsed queries"""

import logging
from typing import Dict, Optional
from .interfaces import ISPARQLBuilder, ParsedQuery

logger = logging.getLogger(__name__)

class SPARQLBuilder(ISPARQLBuilder):
    """Build SPARQL queries from parsed natural language"""
    
    def __init__(self, default_limit: int = 100):
        self.default_limit = default_limit
    
    def build(self, parsed_query: ParsedQuery, namespaces: Dict[str, str]) -> str:
        """Build SPARQL query from parsed components"""
        # Build prefix declarations
        prefixes = self._build_prefixes(namespaces)
        
        # Build SELECT clause
        select_clause = self._build_select(parsed_query)
        
        # Build WHERE clause
        where_clause = self._build_where(parsed_query, namespaces)
        
        # Build ORDER BY clause
        order_clause = self._build_order_by(parsed_query)
        
        # Build LIMIT clause
        limit_clause = self._build_limit(parsed_query)
        
        # Combine all parts
        sparql = f"""
{prefixes}
{select_clause}
WHERE {{
{where_clause}
}}
{order_clause}
{limit_clause}
        """.strip()
        
        logger.debug(f"Generated SPARQL:\n{sparql}")
        return sparql
    
    def _build_prefixes(self, namespaces: Dict[str, str]) -> str:
        """Build prefix declarations"""
        prefixes = []
        for prefix, uri in namespaces.items():
            if prefix:  # Skip empty prefix
                prefixes.append(f"PREFIX {prefix}: <{uri}>")
        return '\n'.join(prefixes)
    
    def _build_select(self, parsed_query: ParsedQuery) -> str:
        """Build SELECT clause"""
        # Determine what to select based on entity type
        variables = ['?item']
        
        # Add common properties
        if parsed_query.entity_type in ['Meeting', 'DailyNote', 'Document']:
            variables.extend(['?title', '?created'])
        elif parsed_query.entity_type == 'Person':
            variables.extend(['?name', '?email'])
        elif parsed_query.entity_type == 'Todo':
            variables.extend(['?description', '?due', '?completed'])
        
        return f"SELECT DISTINCT {' '.join(variables)}"
    
    def _build_where(self, parsed_query: ParsedQuery, namespaces: Dict[str, str]) -> str:
        """Build WHERE clause"""
        where_parts = []
        
        # Add type constraint
        entity_type_uri = self._get_full_uri(parsed_query.entity_type, namespaces)
        where_parts.append(f"  ?item a {entity_type_uri} .")
        
        # Add property constraints from filters
        for prop, value in parsed_query.filters.items():
            prop_uri = self._get_full_uri(prop, namespaces)
            
            # Handle special cases
            if prop == 'hasAttendee' or prop == 'assignedTo':
                # Person reference
                person_uri = self._get_person_uri(value, namespaces)
                where_parts.append(f"  ?item {prop_uri} {person_uri} .")
            else:
                # Literal value
                where_parts.append(f"  ?item {prop_uri} \"{value}\" .")
        
        # Add temporal constraints
        if parsed_query.temporal_constraints:
            temporal_where = self._build_temporal_constraints(
                parsed_query.temporal_constraints
            )
            where_parts.extend(temporal_where)
        
        # Add optional properties based on entity type
        optional_parts = self._build_optional_properties(parsed_query.entity_type)
        if optional_parts:
            where_parts.append(f"  OPTIONAL {{\n{optional_parts}\n  }}")
        
        return '\n'.join(where_parts)
    
    def _build_temporal_constraints(self, temporal: Dict[str, str]) -> list:
        """Build temporal filter constraints"""
        constraints = []
        
        if 'date' in temporal:
            constraints.append(
                f'  ?item dcterms:created ?created .\n'
                f'  FILTER(DATE(?created) = "{temporal["date"]}"^^xsd:date)'
            )
        elif 'start' in temporal and 'end' in temporal:
            constraints.append(
                f'  ?item dcterms:created ?created .\n'
                f'  FILTER(?created >= "{temporal["start"]}"^^xsd:date && '
                f'?created <= "{temporal["end"]}"^^xsd:date)'
            )
        
        return constraints
    
    def _build_optional_properties(self, entity_type: str) -> str:
        """Build OPTIONAL properties based on entity type"""
        optional_parts = []
        
        if entity_type in ['Meeting', 'DailyNote', 'Document']:
            optional_parts.append('    ?item dcterms:title ?title .')
            optional_parts.append('    ?item dcterms:created ?created .')
        elif entity_type == 'Person':
            optional_parts.append('    ?item foaf:name ?name .')
            optional_parts.append('    ?item foaf:mbox ?email .')
        elif entity_type == 'Todo':
            optional_parts.append('    ?item kb:description ?description .')
            optional_parts.append('    ?item kb:due ?due .')
            optional_parts.append('    ?item kb:isCompleted ?completed .')
        
        return '\n'.join(optional_parts)
    
    def _build_order_by(self, parsed_query: ParsedQuery) -> str:
        """Build ORDER BY clause"""
        if parsed_query.order_by:
            prop, direction = parsed_query.order_by
            return f"ORDER BY {direction}(?{prop})"
        elif parsed_query.entity_type in ['Meeting', 'DailyNote']:
            # Default to newest first for time-based entities
            return "ORDER BY DESC(?created)"
        return ""
    
    def _build_limit(self, parsed_query: ParsedQuery) -> str:
        """Build LIMIT clause"""
        limit = parsed_query.limit or self.default_limit
        return f"LIMIT {limit}"
    
    def _get_full_uri(self, local_name: str, namespaces: Dict[str, str]) -> str:
        """Convert local name to full URI or prefixed name"""
        # Check if it's already a full URI
        if local_name.startswith('http'):
            return f"<{local_name}>"
        
        # Try to find in kb namespace
        if 'kb' in namespaces:
            return f"kb:{local_name}"
        
        # Default to unprefixed
        return local_name
    
    def _get_person_uri(self, person_name: str, namespaces: Dict[str, str]) -> str:
        """Convert person name to URI"""
        # Handle special case "me"
        if person_name.lower() == 'me':
            return "kb:person/Me"
        
        # Convert name to URI format
        uri_name = person_name.replace(' ', '_')
        return f"kb:person/{uri_name}"
