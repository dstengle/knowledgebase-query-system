#!/bin/bash
# setup-kb-query.sh
# KB Query Interface Project Setup Script
# This script creates the complete project structure with all files

set -e  # Exit on error

PROJECT_NAME="kb-query-interface"

echo "🚀 Setting up KB Query Interface project..."

# Create root directory
mkdir -p $PROJECT_NAME
cd $PROJECT_NAME

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p src/{kb_query,preprocessing}
mkdir -p tests/data
mkdir -p docs
mkdir -p examples
mkdir -p data

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.coverage
htmlcov/
.pytest_cache/
*.log

# Project specific
data/pattern_cache.json
data/generated_patterns.json
*.db

# OS
.DS_Store
Thumbs.db
EOF

# Create README.md
cat > README.md << 'EOF'
# KB Query Interface

A natural language query interface for RDF knowledge bases that automatically generates query patterns from OWL ontologies.

## Features

- 🔍 Natural language to SPARQL translation
- 🧠 Automatic pattern generation from ontology structure
- 📚 Support for standard vocabularies (FOAF, Schema.org, etc.)
- ⚡ No SPARQL knowledge required
- 🎯 Type-safe query generation

## Installation

```bash
pip install -r requirements.txt
python setup.py install
```

## Quick Start

```python
from kb_query import KBQueryEngine

# Initialize with your ontology
engine = KBQueryEngine('path/to/kb-vocabulary.ttl')

# Query using natural language
results = engine.query("meetings with John Smith")
results = engine.query("todos assigned to me")
results = engine.query("daily notes from last week")
```

## Documentation

- [Architecture Overview](docs/architecture.md)
- [API Reference](docs/api-reference.md)
- [Query Examples](docs/examples.md)

## Development

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=kb_query

# Generate patterns from ontology
python -m kb_query.preprocessing.generate_patterns data/kb-vocabulary.ttl
```

## License

MIT
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
# Core dependencies
rdflib>=6.2.0
SPARQLWrapper>=2.0.0
pyyaml>=6.0

# Natural language processing
nltk>=3.8
spacy>=3.5.0

# Development dependencies
pytest>=7.2.0
pytest-cov>=4.0.0
black>=23.0.0
mypy>=1.0.0
flake8>=6.0.0

# Optional dependencies for pattern enrichment
wordnet>=0.1.0
gensim>=4.3.0  # For word embeddings

# API dependencies (optional)
fastapi>=0.95.0
uvicorn>=0.21.0
EOF

# Create setup.py
cat > setup.py << 'EOF'
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kb-query-interface",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Natural language query interface for RDF knowledge bases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/kb-query-interface",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "rdflib>=6.2.0",
        "SPARQLWrapper>=2.0.0",
        "pyyaml>=6.0",
        "nltk>=3.8",
    ],
    extras_require={
        "dev": [
            "pytest>=7.2.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
        "nlp": [
            "spacy>=3.5.0",
            "wordnet>=0.1.0",
            "gensim>=4.3.0",
        ],
        "api": [
            "fastapi>=0.95.0",
            "uvicorn>=0.21.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "kb-query=kb_query.cli:main",
        ],
    },
)
EOF

# Create config.yaml
cat > config.yaml << 'EOF'
kb_query:
  ontology:
    path: "data/kb-vocabulary.ttl"
    namespaces:
      kb: "http://example.org/kb/vocab#"
      foaf: "http://xmlns.com/foaf/0.1/"
      schema: "http://schema.org/"
      dcterms: "http://purl.org/dc/terms/"
      skos: "http://www.w3.org/2004/02/skos/core#"
  
  patterns:
    cache_enabled: true
    cache_path: "data/pattern_cache.json"
    enrichment:
      use_wordnet: true
      use_embeddings: false
      embedding_model: "word2vec-google-news-300"
  
  query:
    max_query_length: 200
    enable_suggestions: true
    suggestion_threshold: 0.8
    graphs:
      - "original"
      - "inferred" 
      - "entities"
    
  sparql:
    endpoint: "http://localhost:3030/kb/sparql"
    timeout: 30
    limit_default: 100
    
  logging:
    level: "INFO"
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
EOF

# Create src/kb_query/__init__.py
cat > src/kb_query/__init__.py << 'EOF'
"""KB Query Interface - Natural language queries for RDF knowledge bases"""

from .query_engine import KBQueryEngine
from .exceptions import QueryParseError, OntologyError

__version__ = "0.1.0"
__all__ = ["KBQueryEngine", "QueryParseError", "OntologyError"]
EOF

# Create src/kb_query/interfaces.py
cat > src/kb_query/interfaces.py << 'EOF'
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
EOF

# Create src/kb_query/exceptions.py
cat > src/kb_query/exceptions.py << 'EOF'
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
EOF

# Create src/kb_query/ontology_parser.py
cat > src/kb_query/ontology_parser.py << 'EOF'
"""Parse OWL/RDF ontologies to extract structure"""

import logging
from typing import Dict, List, Optional
from rdflib import Graph, Namespace, RDF, RDFS, OWL
from .interfaces import IOntologyParser, OntologyClass, OntologyProperty
from .exceptions import OntologyError

logger = logging.getLogger(__name__)

class OntologyParser(IOntologyParser):
    """Parse RDF/OWL ontologies using rdflib"""
    
    def __init__(self):
        self.graph = Graph()
        self.classes: Dict[str, OntologyClass] = {}
        self.properties: Dict[str, OntologyProperty] = {}
        self.namespaces: Dict[str, str] = {}
        
    def parse(self, ontology_path: str) -> Dict[str, OntologyClass]:
        """Parse ontology file and extract classes"""
        try:
            self.graph.parse(ontology_path, format='turtle')
            logger.info(f"Loaded ontology with {len(self.graph)} triples")
            
            # Extract namespaces
            for prefix, namespace in self.graph.namespaces():
                self.namespaces[prefix] = str(namespace)
            
            # Extract classes
            self._extract_classes()
            
            # Extract properties
            self._extract_properties()
            
            # Link properties to classes
            self._link_properties_to_classes()
            
            return self.classes
            
        except Exception as e:
            raise OntologyError(f"Failed to parse ontology: {e}")
    
    def get_properties(self) -> Dict[str, OntologyProperty]:
        """Get all extracted properties"""
        return self.properties
    
    def get_namespaces(self) -> Dict[str, str]:
        """Get namespace mappings"""
        return self.namespaces
    
    def _extract_classes(self):
        """Extract all classes from the ontology"""
        for class_uri in self.graph.subjects(RDF.type, OWL.Class):
            if isinstance(class_uri, str):
                continue  # Skip blank nodes
                
            local_name = self._get_local_name(class_uri)
            label = self.graph.value(class_uri, RDFS.label) or local_name
            comment = self.graph.value(class_uri, RDFS.comment)
            
            # Get parent classes
            parents = []
            for parent in self.graph.objects(class_uri, RDFS.subClassOf):
                if parent != OWL.Thing:
                    parents.append(str(parent))
            
            self.classes[str(class_uri)] = OntologyClass(
                uri=str(class_uri),
                local_name=local_name,
                label=str(label),
                comment=str(comment) if comment else None,
                parents=parents,
                properties=[]
            )
    
    def _extract_properties(self):
        """Extract all properties from the ontology"""
        # Extract object properties
        for prop_uri in self.graph.subjects(RDF.type, OWL.ObjectProperty):
            self._extract_property(prop_uri)
        
        # Extract datatype properties  
        for prop_uri in self.graph.subjects(RDF.type, OWL.DatatypeProperty):
            self._extract_property(prop_uri)
    
    def _extract_property(self, prop_uri):
        """Extract a single property"""
        local_name = self._get_local_name(prop_uri)
        domain = self.graph.value(prop_uri, RDFS.domain)
        range_val = self.graph.value(prop_uri, RDFS.range)
        comment = self.graph.value(prop_uri, RDFS.comment)
        
        self.properties[str(prop_uri)] = OntologyProperty(
            uri=str(prop_uri),
            local_name=local_name,
            domain=str(domain) if domain else None,
            range=str(range_val) if range_val else None,
            comment=str(comment) if comment else None,
            patterns=[]  # Will be filled by pattern generator
        )
    
    def _link_properties_to_classes(self):
        """Link properties to their domain classes"""
        for prop in self.properties.values():
            if prop.domain and prop.domain in self.classes:
                self.classes[prop.domain].properties.append(prop.uri)
    
    def _get_local_name(self, uri) -> str:
        """Extract local name from URI"""
        uri_str = str(uri)
        if '#' in uri_str:
            return uri_str.split('#')[-1]
        else:
            return uri_str.split('/')[-1]
EOF

# Create src/kb_query/pattern_generator.py
cat > src/kb_query/pattern_generator.py << 'EOF'
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
EOF

# Create src/kb_query/query_parser.py
cat > src/kb_query/query_parser.py << 'EOF'
"""Parse natural language queries into structured form"""

import re
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from .interfaces import IQueryParser, QueryPattern, ParsedQuery
from .exceptions import QueryParseError

logger = logging.getLogger(__name__)

class NaturalLanguageQueryParser(IQueryParser):
    """Parse natural language queries using patterns"""
    
    def __init__(self):
        self.temporal_patterns = {
            'today': lambda: datetime.now().date(),
            'yesterday': lambda: (datetime.now() - timedelta(days=1)).date(),
            'tomorrow': lambda: (datetime.now() + timedelta(days=1)).date(),
            'this week': lambda: self._get_week_range(0),
            'last week': lambda: self._get_week_range(-1),
            'this month': lambda: self._get_month_range(0),
            'last month': lambda: self._get_month_range(-1)
        }
    
    def parse(self, query: str, patterns: List[QueryPattern]) -> ParsedQuery:
        """Parse natural language query using available patterns"""
        query = query.strip().lower()
        
        # Find matching pattern
        matched_pattern, extracted = self._match_pattern(query, patterns)
        
        if not matched_pattern:
            # Try to find similar patterns for suggestions
            suggestions = self._find_similar_patterns(query, patterns)
            raise QueryParseError(
                f"Could not parse query: '{query}'",
                suggestions=suggestions
            )
        
        # Extract components
        entity_type = self._extract_entity_type(matched_pattern)
        filters = self._extract_filters(matched_pattern, extracted)
        temporal = self._extract_temporal_constraints(query)
        
        return ParsedQuery(
            entity_type=entity_type,
            filters=filters,
            temporal_constraints=temporal,
            limit=self._extract_limit(query),
            order_by=self._extract_ordering(query)
        )
    
    def suggest_queries(self, partial: str, patterns: List[QueryPattern]) -> List[str]:
        """Suggest query completions"""
        partial = partial.strip().lower()
        suggestions = []
        
        for pattern in patterns:
            for example in pattern.examples:
                if example.startswith(partial):
                    suggestions.append(example)
        
        # Sort by relevance (length, then alphabetically)
        suggestions.sort(key=lambda x: (len(x), x))
        return suggestions[:10]  # Return top 10
    
    def _match_pattern(self, query: str, patterns: List[QueryPattern]) -> Tuple[Optional[QueryPattern], Dict]:
        """Find pattern that matches the query"""
        for pattern in patterns:
            # Convert pattern to regex
            regex_pattern = self._pattern_to_regex(pattern.pattern)
            match = re.match(regex_pattern, query)
            
            if match:
                return pattern, match.groupdict()
        
        return None, {}
    
    def _pattern_to_regex(self, pattern: str) -> str:
        """Convert pattern template to regex"""
        # Escape special regex characters except {}
        pattern = re.escape(pattern)
        pattern = pattern.replace(r'\{', '{').replace(r'\}', '}')
        
        # Replace {value} with capturing group
        pattern = pattern.replace('{value}', r'(?P<value>[\w\s]+)')
        
        # Make pattern more flexible
        pattern = pattern.replace(' ', r'\s+')
        
        return f'^{pattern}$'
    
    def _extract_entity_type(self, pattern: QueryPattern) -> str:
        """Extract entity type from pattern"""
        # Get local name from class URI
        class_uri = pattern.required_class
        if '#' in class_uri:
            return class_uri.split('#')[-1]
        else:
            return class_uri.split('/')[-1]
    
    def _extract_filters(self, pattern: QueryPattern, extracted: Dict) -> Dict[str, str]:
        """Extract filter values"""
        filters = {}
        
        if pattern.required_property and 'value' in extracted:
            prop_name = pattern.required_property.split('#')[-1]
            filters[prop_name] = extracted['value'].strip()
        
        return filters
    
    def _extract_temporal_constraints(self, query: str) -> Optional[Dict[str, str]]:
        """Extract temporal constraints from query"""
        for temporal_key, date_func in self.temporal_patterns.items():
            if temporal_key in query:
                date_range = date_func()
                if isinstance(date_range, tuple):
                    return {
                        'start': date_range[0].isoformat(),
                        'end': date_range[1].isoformat()
                    }
                else:
                    return {'date': date_range.isoformat()}
        
        # Check for explicit dates
        date_pattern = r'\d{4}-\d{2}-\d{2}'
        date_match = re.search(date_pattern, query)
        if date_match:
            return {'date': date_match.group()}
        
        return None
    
    def _extract_limit(self, query: str) -> Optional[int]:
        """Extract limit from query"""
        limit_patterns = [
            (r'top (\d+)', 1),
            (r'first (\d+)', 1),
            (r'last (\d+)', 1),
            (r'(\d+) results?', 1)
        ]
        
        for pattern, group in limit_patterns:
            match = re.search(pattern, query)
            if match:
                return int(match.group(group))
        
        return None
    
    def _extract_ordering(self, query: str) -> Optional[Tuple[str, str]]:
        """Extract ordering from query"""
        if 'latest' in query or 'most recent' in query:
            return ('created', 'DESC')
        elif 'oldest' in query:
            return ('created', 'ASC')
        elif 'alphabetical' in query:
            return ('title', 'ASC')
        
        return None
    
    def _find_similar_patterns(self, query: str, patterns: List[QueryPattern]) -> List[str]:
        """Find patterns similar to the query"""
        suggestions = []
        query_words = set(query.split())
        
        for pattern in patterns:
            for example in pattern.examples:
                example_words = set(example.split())
                # Calculate word overlap
                overlap = len(query_words & example_words)
                if overlap > 0:
                    suggestions.append((overlap, example))
        
        # Sort by overlap and return top suggestions
        suggestions.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in suggestions[:5]]
    
    def _get_week_range(self, week_offset: int) -> Tuple[datetime, datetime]:
        """Get date range for a week"""
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_target_week = start_of_week + timedelta(weeks=week_offset)
        end_of_target_week = start_of_target_week + timedelta(days=6)
        return (start_of_target_week, end_of_target_week)
    
    def _get_month_range(self, month_offset: int) -> Tuple[datetime, datetime]:
        """Get date range for a month"""
        today = datetime.now().date()
        if month_offset == 0:
            start = today.replace(day=1)
        else:
            # Handle month boundaries
            month = today.month + month_offset
            year = today.year
            if month < 1:
                month = 12
                year -= 1
            elif month > 12:
                month = 1
                year += 1
            start = today.replace(year=year, month=month, day=1)
        
        # Get last day of month
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = start.replace(month=start.month + 1, day=1) - timedelta(days=1)
        
        return (start, end)
EOF

# Create src/kb_query/sparql_builder.py
cat > src/kb_query/sparql_builder.py << 'EOF'
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
EOF

# Create src/kb_query/query_engine.py
cat > src/kb_query/query_engine.py << 'EOF'
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
EOF

# Create test files
cat > tests/test_ontology_parser.py << 'EOF'
"""Tests for ontology parser"""

import pytest
from kb_query.ontology_parser import OntologyParser
from kb_query.exceptions import OntologyError

class TestOntologyParser:
    
    @pytest.fixture
    def parser(self):
        return OntologyParser()
    
    def test_parse_valid_ontology(self, parser, tmp_path):
        """Test parsing a valid ontology"""
        # Create test ontology
        ontology_content = """
        @prefix kb: <http://example.org/kb/vocab#> .
        @prefix owl: <http://www.w3.org/2002/07/owl#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        
        kb:Meeting a owl:Class ;
            rdfs:comment "A meeting document" .
            
        kb:hasAttendee a owl:ObjectProperty ;
            rdfs:domain kb:Meeting ;
            rdfs:range kb:Person .
        """
        
        ontology_file = tmp_path / "test.ttl"
        ontology_file.write_text(ontology_content)
        
        # Parse
        classes = parser.parse(str(ontology_file))
        
        # Verify
        assert len(classes) > 0
        assert any('Meeting' in uri for uri in classes.keys())
    
    def test_parse_invalid_file(self, parser):
        """Test parsing non-existent file"""
        with pytest.raises(OntologyError):
            parser.parse("non_existent.ttl")
EOF

# Create example files
cat > examples/basic_usage.py << 'EOF'
#!/usr/bin/env python3
"""Basic usage examples for KB Query Interface"""

from kb_query import KBQueryEngine

def main():
    # Initialize with your ontology
    engine = KBQueryEngine('data/kb-vocabulary.ttl')
    
    print("KB Query Interface - Examples\n")
    
    # Example 1: Simple queries
    print("1. Simple Queries:")
    queries = [
        "meetings with John Smith",
        "todos assigned to me",
        "daily notes from last week",
        "books by Douglas Adams",
        "stale relationships"
    ]
    
    for q in queries:
        print(f"\nQuery: {q}")
        try:
            result = engine.query(q)
            print(f"SPARQL: {result['sparql'][:100]}...")
        except Exception as e:
            print(f"Error: {e}")
    
    # Example 2: Get patterns for a class
    print("\n\n2. Available patterns for 'Meeting':")
    patterns = engine.get_patterns_for_class("Meeting")
    for p in patterns[:5]:
        print(f"  - {p}")
    
    # Example 3: Query suggestions
    print("\n\n3. Query suggestions for 'meet':")
    suggestions = engine.suggest_queries("meet")
    for s in suggestions:
        print(f"  - {s}")

if __name__ == "__main__":
    main()
EOF

cat > examples/example_queries.txt << 'EOF'
# Example Natural Language Queries for KB

## Meeting Queries
- meetings with John Smith
- meetings attended by Sarah Chen
- meetings from last week
- meetings tagged projects/web
- John Smith's meetings
- meetings at Cafe Allegro
- team meetings from 2024

## Todo Queries  
- todos assigned to me
- incomplete todos
- overdue todos
- todos due tomorrow
- todos from meetings with Sarah
- John's todos

## Document Queries
- daily notes from this week
- daily notes tagged urgent
- documents mentioning Project X
- recent project documents

## People Queries
- people who work with John
- people I haven't met in 6 months
- frequent collaborators
- people at Acme Corp

## Relationship Queries
- stale relationships
- John's relationships
- my professional relationships

## Book Queries
- books by Douglas Adams
- completed books
- books rated 5 stars
- reading list

## Complex Queries
- meetings with John from last month tagged important
- overdue todos assigned to Sarah
- daily notes mentioning Project X from Q1 2024
EOF

# Create documentation files
cat > docs/architecture.md << 'EOF'
# KB Query Interface Architecture

## Overview

The KB Query Interface is designed as a modular system that converts natural language queries into SPARQL by leveraging the structure of an OWL ontology.

## Components

### 1. Ontology Parser
- Parses OWL/RDF ontologies using rdflib
- Extracts classes, properties, domains, and ranges
- Builds a navigable structure of the ontology

### 2. Pattern Generator
- Automatically generates query patterns from ontology structure
- Infers natural language patterns from property names
- Uses domain/range information to create valid combinations

### 3. Query Parser
- Matches natural language input against generated patterns
- Extracts entities, filters, and constraints
- Provides suggestions for incomplete queries

### 4. SPARQL Builder
- Converts parsed queries into valid SPARQL
- Handles namespaces and URI construction
- Optimizes queries for the target triple store

## Data Flow

```
Natural Language Query
        ↓
  Query Parser
        ↓ (matches against)
Generated Patterns
        ↓
  Parsed Query
        ↓
 SPARQL Builder
        ↓
  SPARQL Query
        ↓
  Triple Store
```

## Pattern Generation

Patterns are generated by analyzing:
1. Property names (camelCase decomposition)
2. Domain and range constraints
3. Parent class semantics
4. Common linguistic patterns

Example:
- Property: `kb:hasAttendee`
- Domain: `kb:Meeting`
- Range: `kb:Person`
- Generated patterns:
  - "meetings with {Person}"
  - "meetings attended by {Person}"
  - "{Person}'s meetings"
EOF

cat > docs/api-reference.md << 'EOF'
# KB Query Interface API Reference

## KBQueryEngine

Main class for natural language to SPARQL conversion.

### Constructor

```python
KBQueryEngine(ontology_path: str, config_path: Optional[str] = None)
```

**Parameters:**
- `ontology_path`: Path to OWL/RDF ontology file (Turtle format)
- `config_path`: Optional path to YAML configuration file

### Methods

#### query(natural_language_query: str) -> Dict

Convert natural language query to SPARQL.

**Parameters:**
- `natural_language_query`: Query in natural language

**Returns:**
Dictionary containing:
- `sparql`: Generated SPARQL query
- `parsed`: Parsed query components
- `results`: Query results (if endpoint configured)

**Example:**
```python
result = engine.query("meetings with John Smith")
print(result['sparql'])
```

#### get_patterns_for_class(class_name: str) -> List[str]

Get all query patterns available for a class.

**Parameters:**
- `class_name`: Name of the ontology class

**Returns:**
List of example queries for the class

#### suggest_queries(partial: str) -> List[str]

Get query suggestions for partial input.

**Parameters:**
- `partial`: Partial query string

**Returns:**
List of suggested complete queries

## Exceptions

### KBQueryError
Base exception for all KB Query errors.

### OntologyError
Raised when ontology parsing fails.

### QueryParseError
Raised when natural language query cannot be parsed.

**Attributes:**
- `suggestions`: List of similar valid queries
EOF

cat > docs/examples.md << 'EOF'
# KB Query Examples

## Basic Usage

```python
from kb_query import KBQueryEngine

# Initialize
engine = KBQueryEngine('path/to/ontology.ttl')

# Simple query
result = engine.query("meetings with John Smith")
print(result['sparql'])
```

## Query Patterns

### Meeting Queries

```python
# By attendee
engine.query("meetings with John Smith")
engine.query("meetings attended by Sarah Chen")

# By time
engine.query("meetings from last week")
engine.query("meetings today")

# By tag
engine.query("meetings tagged projects/web")
```

### Todo Queries

```python
# By assignee
engine.query("todos assigned to me")
engine.query("John's todos")

# By status
engine.query("incomplete todos")
engine.query("overdue todos")

# By date
engine.query("todos due tomorrow")
```

### Complex Queries

```python
# Multiple filters
engine.query("meetings with John from last week")
engine.query("incomplete todos assigned to Sarah")

# With limits
engine.query("top 5 recent meetings")
engine.query("latest 10 daily notes")
```

## Configuration

```yaml
kb_query:
  ontology:
    namespaces:
      kb: "http://example.org/kb/vocab#"
      
  patterns:
    cache_enabled: true
    enrichment:
      use_wordnet: true
      
  sparql:
    endpoint: "http://localhost:3030/kb/sparql"
    timeout: 30
```

## Error Handling

```python
try:
    result = engine.query("invalid query syntax")
except QueryParseError as e:
    print(f"Could not parse: {e}")
    print(f"Did you mean: {e.suggestions}")
```
EOF

# Create a simple test ontology
cat > data/kb-vocabulary.ttl << 'EOF'
@prefix kb: <http://example.org/kb/vocab#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Sample KB vocabulary for testing
kb: a owl:Ontology ;
    rdfs:comment "Personal Knowledge Base Vocabulary" .

# Classes
kb:Document a owl:Class ;
    rdfs:comment "A markdown document" .

kb:Meeting a owl:Class ;
    rdfs:subClassOf kb:Document ;
    rdfs:comment "Meeting notes" .

kb:Person a owl:Class ;
    rdfs:comment "A person" .

kb:Todo a owl:Class ;
    rdfs:comment "A todo item" .

# Properties
kb:hasAttendee a owl:ObjectProperty ;
    rdfs:domain kb:Meeting ;
    rdfs:range kb:Person ;
    rdfs:comment "Person who attended meeting" .

kb:assignedTo a owl:ObjectProperty ;
    rdfs:domain kb:Todo ;
    rdfs:range kb:Person ;
    rdfs:comment "Person responsible for todo" .
EOF

# Create preprocessing scripts
cat > src/preprocessing/__init__.py << 'EOF'
"""Preprocessing tools for pattern enrichment"""
EOF

cat > src/preprocessing/pattern_enrichment.py << 'EOF'
"""Enrich patterns with NLP and semantic analysis"""

import logging
from typing import List, Dict, Set

logger = logging.getLogger(__name__)

class PatternEnricher:
    """Enrich patterns using NLP and external resources"""
    
    def __init__(self, use_wordnet: bool = True, use_embeddings: bool = False):
        self.use_wordnet = use_wordnet
        self.use_embeddings = use_embeddings
        
        if use_wordnet:
            self._init_wordnet()
        if use_embeddings:
            self._init_embeddings()
    
    def enrich_patterns(self, patterns: List) -> List:
        """Add synonyms and related terms to patterns"""
        enriched = []
        
        for pattern in patterns:
            # Add synonyms
            if self.use_wordnet:
                pattern.synonyms = self._get_synonyms(pattern.pattern)
            
            # Add similar phrases
            if self.use_embeddings:
                pattern.similar = self._get_similar_phrases(pattern.pattern)
            
            enriched.append(pattern)
        
        return enriched
    
    def _init_wordnet(self):
        """Initialize WordNet"""
        try:
            import nltk
            nltk.download('wordnet', quiet=True)
            from nltk.corpus import wordnet
            self.wordnet = wordnet
        except ImportError:
            logger.warning("WordNet not available")
            self.use_wordnet = False
    
    def _init_embeddings(self):
        """Initialize word embeddings"""
        # TODO: Implement embedding initialization
        pass
    
    def _get_synonyms(self, phrase: str) -> List[str]:
        """Get synonyms for a phrase"""
        # TODO: Implement synonym extraction
        return []
    
    def _get_similar_phrases(self, phrase: str) -> List[str]:
        """Get semantically similar phrases"""
        # TODO: Implement similarity search
        return []
EOF

# Make scripts executable
chmod +x examples/basic_usage.py

echo "✅ KB Query Interface project structure created successfully!"
echo ""
echo "📁 Project created in: $PROJECT_NAME/"
echo ""
echo "🚀 Next steps:"
echo "1. cd $PROJECT_NAME"
echo "2. python -m venv venv"
echo "3. source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "4. pip install -r requirements.txt"
echo "5. pip install -e ."
echo "6. python examples/basic_usage.py"
echo ""
echo "📚 Documentation:"
echo "- Architecture: docs/architecture.md"
echo "- API Reference: docs/api-reference.md"
echo "- Examples: docs/examples.md"