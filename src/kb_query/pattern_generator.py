"""Generate query patterns from ontology structure"""

import re
import logging
from typing import List, Dict, Set
from .interfaces import (
    IPatternGenerator, OntologyClass, OntologyProperty, QueryPattern
)

logger = logging.getLogger(__name__)

class AutomaticPatternGenerator(IPatternGenerator):
    """Automatically generate patterns from ontology structure"""
    
    def __init__(self):
        self.preposition_patterns = {
            'has': ['with', 'having', 'that has'],
            'is': ['that is', 'which is'],
            'was': ['that was', 'which was'],
            'in': ['in', 'within', 'inside'],
            'from': ['from', 'coming from'],
            'to': ['to', 'assigned to'],
            'by': ['by', 'created by', 'written by'],
            'at': ['at', 'located at'],
            'of': ['of', 'part of'],
            'for': ['for', 'intended for']
        }
        
        self.special_predicates = {
            'hasAttendee': ['with', 'attended by', 'including', 'with participant'],
            'assignedTo': ['assigned to', 'for', 'owned by'],
            'hasTag': ['tagged', 'tagged with', 'under', 'categorized as'],
            'mentionedIn': ['mentioned in', 'appears in', 'found in'],
            'describedBy': ['described by', 'documented in'],
            'hasAuthor': ['by', 'written by', 'authored by'],
            'locatedIn': ['in', 'at', 'located in'],
            'isCompleted': ['completed', 'done', 'finished'],
            'isStale': ['stale', 'inactive', 'dormant']
        }
    
    def generate_patterns(self, 
                         classes: Dict[str, OntologyClass],
                         properties: Dict[str, OntologyProperty]) -> List[QueryPattern]:
        """Generate all query patterns from ontology"""
        patterns = []
        
        # Generate patterns for each property
        for prop_uri, prop in properties.items():
            if not prop.domain or not prop.range:
                continue
            
            # Get the domain class
            domain_class = classes.get(prop.domain)
            if not domain_class:
                continue
            
            # Generate natural language patterns
            nl_patterns = self._infer_property_patterns(prop)
            
            # Create query patterns
            for nl_pattern in nl_patterns:
                pattern = self._create_query_pattern(
                    domain_class, prop, nl_pattern
                )
                patterns.append(pattern)
        
        # Add class-based patterns
        patterns.extend(self._generate_class_patterns(classes))
        
        logger.info(f"Generated {len(patterns)} query patterns")
        return patterns
    
    def _infer_property_patterns(self, prop: OntologyProperty) -> List[str]:
        """Infer natural language patterns from property name"""
        patterns = []
        prop_name = prop.local_name
        
        # Check special predicates first
        if prop_name in self.special_predicates:
            patterns.extend(self.special_predicates[prop_name])
        
        # Decompose camelCase
        words = self._decompose_camel_case(prop_name)
        
        if words:
            # Check first word for preposition patterns
            first_word = words[0].lower()
            if first_word in self.preposition_patterns:
                base_patterns = self.preposition_patterns[first_word]
                
                if len(words) > 1:
                    # Add noun to patterns
                    noun = ' '.join(words[1:]).lower()
                    for bp in base_patterns:
                        patterns.append(f"{bp} {noun}")
                else:
                    patterns.extend(base_patterns)
            
            # Handle "By" suffix
            if prop_name.endswith('By'):
                verb = prop_name[:-2].lower()
                patterns.extend([f"{verb} by", f"is {verb} by"])
            
            # Handle "To" suffix
            elif prop_name.endswith('To'):
                verb = prop_name[:-2].lower()
                patterns.extend([f"{verb} to", f"is {verb} to"])
            
            # Handle "In" suffix
            elif prop_name.endswith('In'):
                verb = prop_name[:-2].lower()
                patterns.extend([f"{verb} in", f"appears in", f"found in"])
        
        # Generate possessive patterns for person-related properties
        if prop.range and 'Person' in prop.range:
            patterns.append("{value}'s")
        
        return patterns if patterns else [prop_name.lower()]
    
    def _create_query_pattern(self, domain_class: OntologyClass, 
                            prop: OntologyProperty, 
                            nl_pattern: str) -> QueryPattern:
        """Create a query pattern object"""
        # Generate SPARQL template
        sparql_template = self._generate_sparql_template(
            domain_class, prop, nl_pattern
        )
        
        # Generate examples
        examples = self._generate_examples(
            domain_class.local_name, nl_pattern, prop.range
        )
        
        # Create pattern string
        class_name = self._to_plural(domain_class.local_name).lower()
        
        # Handle possessive patterns
        if nl_pattern == "{value}'s":
            pattern = f"{{value}}'s {class_name}"
        else:
            pattern = f"{class_name} {nl_pattern} {{value}}"
        
        return QueryPattern(
            pattern=pattern,
            sparql_template=sparql_template,
            required_class=domain_class.uri,
            required_property=prop.uri,
            examples=examples
        )
    
    def _generate_class_patterns(self, classes: Dict[str, OntologyClass]) -> List[QueryPattern]:
        """Generate patterns for querying classes directly"""
        patterns = []
        
        for class_uri, cls in classes.items():
            # Skip abstract classes
            if cls.local_name.startswith('_'):
                continue
            
            # Basic class query
            pattern = QueryPattern(
                pattern=self._to_plural(cls.local_name).lower(),
                sparql_template=f"?item a <{class_uri}>",
                required_class=class_uri,
                required_property=None,
                examples=[
                    self._to_plural(cls.local_name).lower(),
                    f"all {self._to_plural(cls.local_name).lower()}",
                    f"show {self._to_plural(cls.local_name).lower()}"
                ]
            )
            patterns.append(pattern)
        
        return patterns
    
    def _decompose_camel_case(self, name: str) -> List[str]:
        """Decompose camelCase into words"""
        # Handle acronyms and camelCase
        words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', name)
        return words
    
    def _to_plural(self, word: str) -> str:
        """Convert word to plural form"""
        if word.endswith('y'):
            return word[:-1] + 'ies'
        elif word.endswith('s') or word.endswith('x'):
            return word + 'es'
        else:
            return word + 's'
    
    def _to_singular(self, word: str) -> str:
        """Convert word to singular form"""
        if word.endswith('ies'):
            return word[:-3] + 'y'
        elif word.endswith('es'):
            return word[:-2]
        elif word.endswith('s'):
            return word[:-1]
        else:
            return word
    
    def _generate_sparql_template(self, domain_class: OntologyClass,
                                 prop: OntologyProperty,
                                 nl_pattern: str) -> str:
        """Generate SPARQL template for a pattern"""
        return f"""
        ?item a <{domain_class.uri}> .
        ?item <{prop.uri}> ?value .
        """
    
    def _generate_examples(self, class_name: str, pattern: str, range_type: str) -> List[str]:
        """Generate example queries"""
        examples = []
        
        # Generate example values based on range type
        if range_type and 'Person' in range_type:
            example_values = ['John Smith', 'Sarah Chen', 'me']
        elif range_type and 'Date' in range_type:
            example_values = ['today', 'last week', '2024-01-01']
        else:
            example_values = ['example']
        
        class_plural = self._to_plural(class_name).lower()
        
        for value in example_values:
            if pattern == "{value}'s":
                examples.append(f"{value}'s {class_plural}")
            else:
                examples.append(f"{class_plural} {pattern} {value}")
        
        return examples
