"""Grammar Engine for OWL ontology processing and pattern generation."""

import hashlib
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

try:
    import rdflib
    from rdflib import RDF, RDFS, OWL
except ImportError:
    raise ImportError("rdflib is required. Install with: pip install rdflib")

from ..core.entities import Pattern, Grammar
from ..exceptions import GrammarError


class GrammarEngine:
    """Engine for parsing OWL ontologies and generating query patterns."""
    
    def __init__(self, cache_manager: Optional[Any] = None):
        """Initialize grammar engine with optional cache manager."""
        self.cache_manager = cache_manager
    
    def load_grammar(self, ontology_path: str) -> Grammar:
        """Load or generate grammar from ontology file."""
        try:
            ontology_path = Path(ontology_path)
            
            if not ontology_path.exists():
                raise GrammarError(f"Ontology file not found: {ontology_path}", str(ontology_path))
            
            # Calculate hash for caching
            ontology_hash = self._calculate_hash(ontology_path)
            
            # Try to get from cache
            if self.cache_manager:
                cache_key = f"grammar_{ontology_hash}"
                cached_grammar = self.cache_manager.get(cache_key)
                if cached_grammar:
                    return Grammar(**cached_grammar)
            
            # Parse ontology and generate patterns
            ontology_data = self._parse_ontology(ontology_path)
            patterns = self.generate_patterns(ontology_data)
            
            # Create grammar object
            grammar = Grammar(
                patterns=patterns,
                ontology_hash=ontology_hash,
                namespaces=ontology_data['namespaces'],
                created_at=datetime.now().isoformat()
            )
            
            # Cache for future use
            if self.cache_manager:
                self.cache_manager.put(cache_key, grammar.__dict__)
            
            return grammar
            
        except Exception as e:
            if isinstance(e, GrammarError):
                raise
            raise GrammarError(f"Failed to load grammar: {str(e)}", str(ontology_path))
    
    def _parse_ontology(self, ontology_path: Path) -> Dict:
        """Parse OWL/RDF ontology file."""
        graph = rdflib.Graph()
        graph.parse(ontology_path, format='turtle')
        
        # Extract classes
        classes = []
        for subj in graph.subjects(RDF.type, OWL.Class):
            classes.append(str(subj))
        
        # Extract properties
        properties = []
        
        # Object properties
        for prop in graph.subjects(RDF.type, OWL.ObjectProperty):
            prop_info = {
                'name': str(prop),
                'type': 'object_property',
                'domain': None,
                'range': None,
                'label': None
            }
            
            # Get domain and range
            for domain in graph.objects(prop, RDFS.domain):
                prop_info['domain'] = str(domain)
            
            for range_obj in graph.objects(prop, RDFS.range):
                prop_info['range'] = str(range_obj)
            
            # Get label if available
            for label in graph.objects(prop, RDFS.label):
                prop_info['label'] = str(label)
            
            properties.append(prop_info)
        
        # Datatype properties
        for prop in graph.subjects(RDF.type, OWL.DatatypeProperty):
            prop_info = {
                'name': str(prop),
                'type': 'datatype_property',
                'domain': None,
                'range': None,
                'label': None
            }
            
            for domain in graph.objects(prop, RDFS.domain):
                prop_info['domain'] = str(domain)
            
            for range_obj in graph.objects(prop, RDFS.range):
                prop_info['range'] = str(range_obj)
            
            for label in graph.objects(prop, RDFS.label):
                prop_info['label'] = str(label)
            
            properties.append(prop_info)
        
        # Extract namespaces
        namespaces = {}
        for prefix, namespace in graph.namespaces():
            if prefix:  # Skip default namespace
                namespaces[prefix] = str(namespace)
        
        return {
            'classes': classes,
            'properties': properties,
            'namespaces': namespaces
        }
    
    def generate_patterns(self, ontology_data: Dict) -> List[Pattern]:
        """Generate query patterns from ontology structure."""
        patterns = []
        pattern_id_counter = 0
        
        for prop_info in ontology_data['properties']:
            prop_patterns = self._generate_property_patterns(prop_info)
            # Add unique IDs to patterns
            for pattern in prop_patterns:
                if not pattern.id or pattern.id.startswith('pattern_'):
                    pattern.id = f"pattern_{pattern_id_counter:03d}"
                    pattern_id_counter += 1
            patterns.extend(prop_patterns)
        
        return patterns
    
    def _generate_property_patterns(self, prop_info: Dict) -> List[Pattern]:
        """Generate patterns for a single property."""
        patterns = []
        prop_name = prop_info['name']
        domain = prop_info.get('domain', 'Entity')
        range_type = prop_info.get('range', 'Value')
        
        # Extract property base name
        base_name = self._extract_base_name(prop_name)
        
        # Simplify class names for templates
        domain_simple = self._simplify_class_name(domain).lower()
        range_simple = self._simplify_class_name(range_type).lower()
        
        if prop_info['type'] == 'object_property' and domain and range_type:
            # Pattern 1: "meetings with {person}"
            template1 = f"{domain_simple}s with {{{range_simple}}}"
            sparql1 = self._generate_sparql_template(
                template1, prop_info, domain_simple, range_simple
            )
            patterns.append(Pattern(
                id=f"pattern_{base_name}_with",
                template=template1,
                sparql_template=sparql1,
                entity_types={range_simple: range_type},
                examples=[f"{domain_simple}s with John Smith", f"{domain_simple}s with Sarah"],
                confidence=0.85,
                domain_class=domain,
                property=prop_name
            ))
            
            # Pattern 2: "{person}'s meetings"
            template2 = f"{{{range_simple}}}'s {domain_simple}s"
            sparql2 = self._generate_sparql_template(
                template2, prop_info, domain_simple, range_simple
            )
            patterns.append(Pattern(
                id=f"pattern_{base_name}_possessive",
                template=template2,
                sparql_template=sparql2,
                entity_types={range_simple: range_type},
                examples=[f"John's {domain_simple}s", f"Sarah's {domain_simple}s"],
                confidence=0.85,
                domain_class=domain,
                property=prop_name
            ))
        
        elif prop_info['type'] == 'datatype_property' and domain:
            # Pattern for datatype properties: "meetings tagged {tag}"
            template = f"{domain_simple}s tagged {{{base_name}}}"
            sparql = self._generate_sparql_datatype_template(
                template, prop_info, domain_simple, base_name
            )
            patterns.append(Pattern(
                id=f"pattern_{base_name}_tagged",
                template=template,
                sparql_template=sparql,
                entity_types={base_name: range_type},
                examples=[f"{domain_simple}s tagged project", f"{domain_simple}s tagged important"],
                confidence=0.80,
                domain_class=domain,
                property=prop_name
            ))
        
        return patterns
    
    def _generate_sparql_template(self, template: str, prop_info: Dict, 
                                   domain_simple: str, range_simple: str) -> str:
        """Generate SPARQL template for object property patterns."""
        prop_name = prop_info['name']
        
        # Extract namespace and local name
        if '#' in prop_name:
            namespace, local_name = prop_name.rsplit('#', 1)
            namespace += '#'
        elif '/' in prop_name:
            namespace, local_name = prop_name.rsplit('/', 1)
            namespace += '/'
        else:
            namespace = ''
            local_name = prop_name
        
        # Generate SPARQL with variable names based on domain
        sparql = f"""SELECT ?{domain_simple} ?{range_simple}_name
WHERE {{
  ?{domain_simple} <{prop_name}> ?{range_simple} .
  ?{range_simple} <http://xmlns.com/foaf/0.1/name> ?{range_simple}_name .
  FILTER (lcase(str(?{range_simple}_name)) = lcase("{{{range_simple}}}"))
}}"""
        
        return sparql
    
    def _generate_sparql_datatype_template(self, template: str, prop_info: Dict,
                                          domain_simple: str, value_name: str) -> str:
        """Generate SPARQL template for datatype property patterns."""
        prop_name = prop_info['name']
        
        sparql = f"""SELECT ?{domain_simple}
WHERE {{
  ?{domain_simple} <{prop_name}> ?{value_name} .
  FILTER (lcase(str(?{value_name})) = lcase("{{{value_name}}}"))
}}"""
        
        return sparql
    
    def _extract_base_name(self, property_name: str) -> str:
        """Extract base name from property URI."""
        # Get local name after # or /
        if '#' in property_name:
            local_name = property_name.split('#')[-1]
        elif '/' in property_name:
            local_name = property_name.split('/')[-1]
        elif ':' in property_name:
            # Handle prefixed names like kb:hasAttendee
            local_name = property_name.split(':')[-1]
        else:
            local_name = property_name
        
        # Handle camelCase prefixes
        if local_name.lower().startswith('has'):
            return local_name[3:].lower()
        elif local_name.lower().startswith('is'):
            return local_name[2:].lower()
        else:
            return local_name.lower()
    
    def _simplify_class_name(self, class_uri: str) -> str:
        """Extract simple class name from URI."""
        if not class_uri:
            return 'entity'
        
        # Handle URIs
        if '#' in class_uri:
            return class_uri.split('#')[-1]
        elif '/' in class_uri:
            return class_uri.split('/')[-1]
        else:
            # Handle prefixed names like "foaf:Person"
            if ':' in class_uri:
                return class_uri.split(':')[-1]
            return class_uri
    
    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate hash of ontology file for caching."""
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()[:12]