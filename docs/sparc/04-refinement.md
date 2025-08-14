# SPARC Phase 4: Refinement

## TDD Implementation Strategy

This phase implements the KB Query CLI system using Test-Driven Development (TDD) methodology: **Red → Green → Refactor**.

### Implementation Order

1. **Core Data Structures** → **Business Logic** → **Services** → **CLI Interface**
2. **Infrastructure** → **Integration** → **End-to-End**

Each component follows strict TDD:
- ✅ Write failing test first
- ✅ Implement minimal code to pass
- ✅ Refactor while keeping tests green

## TDD Cycle 1: Core Data Structures

### Test: Pattern Data Structure
```python
# tests/test_core_structures.py
def test_pattern_creation():
    """Test Pattern dataclass creation and validation"""
    pattern = Pattern(
        id="test_001",
        template="meetings with {person}",
        sparql_template="SELECT ?meeting WHERE { ?meeting kb:hasAttendee ?person . ?person foaf:name \"{person}\" }",
        entity_types={"person": "foaf:Person"},
        examples=["meetings with John Smith"],
        confidence=0.95,
        domain_class="kb:Meeting",
        property="kb:hasAttendee"
    )
    
    assert pattern.id == "test_001"
    assert "person" in pattern.entity_types
    assert pattern.confidence > 0.9

def test_pattern_validation():
    """Test pattern validation rules"""
    # Should fail - no entity placeholders
    with pytest.raises(ValidationError):
        Pattern(
            id="invalid",
            template="meetings only",  # No {entity}
            sparql_template="SELECT * WHERE { ?s ?p ?o }",
            entity_types={},
            examples=[],
            confidence=0.5,
            domain_class="kb:Meeting",
            property="kb:hasAttendee"
        ).validate()
```

### Implementation: Pattern Structure
```python
# kb_query/core/entities.py
from dataclasses import dataclass, field
from typing import List, Dict
from .exceptions import ValidationError

@dataclass
class Pattern:
    id: str
    template: str
    sparql_template: str
    entity_types: Dict[str, str]
    examples: List[str]
    confidence: float
    domain_class: str
    property: str
    keywords: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.keywords = self._extract_keywords()
        self.validate()
    
    def validate(self) -> None:
        """Validate pattern structure"""
        if not self._has_entity_placeholders():
            raise ValidationError(f"Pattern {self.id} has no entity placeholders")
        
        if self.confidence < 0.0 or self.confidence > 1.0:
            raise ValidationError(f"Pattern {self.id} confidence must be 0.0-1.0")
            
        if not self.examples:
            raise ValidationError(f"Pattern {self.id} must have examples")
    
    def _has_entity_placeholders(self) -> bool:
        """Check if template contains {entity} placeholders"""
        import re
        return bool(re.search(r'\{[^}]+\}', self.template))
    
    def _extract_keywords(self) -> List[str]:
        """Extract keywords from template"""
        import re
        # Remove placeholders and extract words
        text = re.sub(r'\{[^}]+\}', '', self.template)
        return [word.lower().strip() for word in text.split() if word.strip()]
```

## TDD Cycle 2: Grammar Engine

### Test: OWL Parsing
```python
# tests/test_grammar_engine.py
def test_owl_parsing():
    """Test OWL vocabulary parsing"""
    engine = GrammarEngine(cache_manager=MockCacheManager())
    
    # Create test OWL content
    owl_content = """
    @prefix kb: <http://example.org/kb#> .
    @prefix foaf: <http://xmlns.com/foaf/0.1/> .
    
    kb:Meeting a owl:Class .
    kb:Person a owl:Class .
    kb:hasAttendee a owl:ObjectProperty ;
                   rdfs:domain kb:Meeting ;
                   rdfs:range foaf:Person .
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ttl', delete=False) as f:
        f.write(owl_content)
        ontology_path = f.name
    
    grammar = engine.load_grammar(ontology_path)
    
    assert len(grammar.patterns) > 0
    assert "kb:hasAttendee" in [p.property for p in grammar.patterns]
    assert grammar.ontology_hash is not None
    
    os.unlink(ontology_path)

def test_pattern_generation():
    """Test pattern generation from OWL properties"""
    engine = GrammarEngine(cache_manager=MockCacheManager())
    
    ontology_data = {
        'classes': ['kb:Meeting', 'foaf:Person'],
        'properties': [
            {
                'name': 'kb:hasAttendee',
                'domain': 'kb:Meeting', 
                'range': 'foaf:Person',
                'type': 'object_property'
            }
        ],
        'namespaces': {'kb': 'http://example.org/kb#'}
    }
    
    patterns = engine.generate_patterns(ontology_data)
    
    assert len(patterns) > 0
    attendee_patterns = [p for p in patterns if 'attendee' in p.template.lower()]
    assert len(attendee_patterns) > 0
    
    # Should generate multiple pattern variations
    templates = [p.template for p in attendee_patterns]
    assert any('with' in t for t in templates)
    assert any('Meeting' in t for t in templates)
```

### Implementation: Grammar Engine
```python
# kb_query/core/grammar.py
import hashlib
import rdflib
from typing import List, Dict, Optional
from pathlib import Path
from .entities import Pattern, Grammar
from ..infrastructure.cache import ICacheManager

class GrammarEngine:
    def __init__(self, cache_manager: ICacheManager):
        self.cache_manager = cache_manager
    
    def load_grammar(self, ontology_path: str) -> Grammar:
        """Load or generate grammar from ontology file"""
        ontology_path = Path(ontology_path)
        ontology_hash = self._calculate_hash(ontology_path)
        
        # Try cache first
        cached_grammar = self.cache_manager.get(f"grammar_{ontology_hash}")
        if cached_grammar:
            return Grammar(**cached_grammar)
        
        # Parse ontology and generate patterns
        ontology_data = self._parse_ontology(ontology_path)
        patterns = self.generate_patterns(ontology_data)
        
        grammar = Grammar(
            patterns=patterns,
            ontology_hash=ontology_hash,
            namespaces=ontology_data['namespaces'],
            created_at=datetime.now().isoformat()
        )
        
        # Cache for future use
        self.cache_grammar(grammar, ontology_hash)
        
        return grammar
    
    def _parse_ontology(self, ontology_path: Path) -> Dict:
        """Parse OWL/RDF ontology file"""
        graph = rdflib.Graph()
        graph.parse(ontology_path)
        
        # Extract classes
        classes = []
        for subj, pred, obj in graph.triples((None, rdflib.RDF.type, rdflib.OWL.Class)):
            classes.append(str(subj))
        
        # Extract properties
        properties = []
        for prop in graph.subjects(rdflib.RDF.type, rdflib.OWL.ObjectProperty):
            prop_info = {
                'name': str(prop),
                'type': 'object_property',
                'domain': None,
                'range': None
            }
            
            # Get domain and range
            for domain in graph.objects(prop, rdflib.RDFS.domain):
                prop_info['domain'] = str(domain)
            
            for range_obj in graph.objects(prop, rdflib.RDFS.range):
                prop_info['range'] = str(range_obj)
                
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
        """Generate query patterns from ontology structure"""
        patterns = []
        
        for prop_info in ontology_data['properties']:
            prop_patterns = self._generate_property_patterns(prop_info)
            patterns.extend(prop_patterns)
        
        return patterns
    
    def _generate_property_patterns(self, prop_info: Dict) -> List[Pattern]:
        """Generate patterns for a single property"""
        patterns = []
        prop_name = prop_info['name']
        domain = prop_info.get('domain', 'Entity')
        range_type = prop_info.get('range', 'Value')
        
        # Extract property base name (e.g., hasAttendee -> attendee)
        base_name = self._extract_base_name(prop_name)
        
        # Generate pattern variations
        if domain and range_type:
            domain_simple = self._simplify_class_name(domain)
            range_simple = self._simplify_class_name(range_type)
            
            # Pattern 1: "meetings with {person}"
            template1 = f"{domain_simple.lower()}s with {{{range_simple.lower()}}}"
            patterns.append(self._create_pattern(
                template1, prop_info, f"pattern_{base_name}_with"
            ))
            
            # Pattern 2: "{person}'s meetings"  
            template2 = f"{{{range_simple.lower()}}}'s {domain_simple.lower()}s"
            patterns.append(self._create_pattern(
                template2, prop_info, f"pattern_{base_name}_possessive"
            ))
        
        return patterns
    
    def _extract_base_name(self, property_name: str) -> str:
        """Extract base name from property URI"""
        # Get local name after # or /
        local_name = property_name.split('#')[-1].split('/')[-1]
        
        # Handle camelCase (hasAttendee -> attendee)
        if local_name.startswith('has'):
            return local_name[3:].lower()
        elif local_name.startswith('is'):
            return local_name[2:].lower()
        else:
            return local_name.lower()
    
    def _simplify_class_name(self, class_uri: str) -> str:
        """Extract simple class name from URI"""
        return class_uri.split('#')[-1].split('/')[-1]
    
    def _create_pattern(self, template: str, prop_info: Dict, pattern_id: str) -> Pattern:
        """Create Pattern object from template and property info"""
        # Generate SPARQL template
        sparql_template = self._generate_sparql_template(template, prop_info)
        
        # Extract entity types
        entity_types = self._extract_entity_types(template, prop_info)
        
        # Generate examples
        examples = self._generate_examples(template)
        
        return Pattern(
            id=pattern_id,
            template=template,
            sparql_template=sparql_template,
            entity_types=entity_types,
            examples=examples,
            confidence=0.85,  # Base confidence
            domain_class=prop_info.get('domain', ''),
            property=prop_info['name']
        )
    
    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate hash of ontology file for caching"""
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()[:12]
```

## TDD Cycle 3: Pattern Matcher

### Test: Pattern Matching
```python
# tests/test_pattern_matcher.py
def test_exact_match():
    """Test exact pattern matching"""
    matcher = PatternMatcher()
    
    pattern = Pattern(
        id="test_001",
        template="meetings with {person}",
        sparql_template="SELECT ?meeting WHERE { ?meeting kb:hasAttendee ?person }",
        entity_types={"person": "foaf:Person"},
        examples=["meetings with John Smith"],
        confidence=0.95,
        domain_class="kb:Meeting",
        property="kb:hasAttendee"
    )
    
    grammar = Grammar(
        patterns=[pattern],
        ontology_hash="test_hash",
        namespaces={"kb": "http://example.org/kb#"},
        created_at="2025-08-06"
    )
    
    matches = matcher.find_matches("meetings with John Smith", grammar)
    
    assert len(matches) == 1
    assert matches[0].confidence == 1.0  # Exact match
    assert matches[0].match_type == "exact"
    assert "person" in matches[0].entities
    assert matches[0].entities["person"] == "John Smith"

def test_fuzzy_match():
    """Test fuzzy pattern matching with typos"""
    matcher = PatternMatcher()
    
    # Same pattern as above
    matches = matcher.find_matches("meetigns with John Smith", grammar)
    
    assert len(matches) >= 1
    assert matches[0].confidence > 0.7  # Should still match despite typo
    assert matches[0].match_type == "fuzzy"

def test_entity_extraction():
    """Test entity extraction from matched patterns"""
    matcher = PatternMatcher()
    
    pattern = Pattern(
        template="meetings with {person} about {topic}",
        # ... other fields
    )
    
    entities = matcher.extract_entities(
        "meetings with Sarah Chen about project planning", 
        pattern
    )
    
    assert entities["person"] == "Sarah Chen"
    assert entities["topic"] == "project planning"
```

### Implementation: Pattern Matcher
```python
# kb_query/core/matcher.py
import re
from typing import List, Dict
from difflib import SequenceMatcher
from .entities import Pattern, Grammar, MatchResult

class PatternMatcher:
    def __init__(self, similarity_threshold: float = 0.7):
        self.similarity_threshold = similarity_threshold
    
    def find_matches(self, input_text: str, grammar: Grammar) -> List[MatchResult]:
        """Find matching patterns for user input"""
        input_text = self._normalize_text(input_text)
        matches = []
        
        for pattern in grammar.patterns:
            match_result = self._match_pattern(input_text, pattern)
            if match_result and match_result.confidence >= self.similarity_threshold:
                matches.append(match_result)
        
        # Sort by confidence, highest first
        matches.sort(key=lambda m: m.confidence, reverse=True)
        return matches
    
    def _match_pattern(self, input_text: str, pattern: Pattern) -> Optional[MatchResult]:
        """Match input against a single pattern"""
        normalized_template = self._normalize_text(pattern.template)
        
        # Try exact match first (fastest path)
        exact_match = self._try_exact_match(input_text, pattern)
        if exact_match:
            return exact_match
        
        # Try fuzzy match
        fuzzy_match = self._try_fuzzy_match(input_text, pattern)
        if fuzzy_match:
            return fuzzy_match
        
        return None
    
    def _try_exact_match(self, input_text: str, pattern: Pattern) -> Optional[MatchResult]:
        """Try exact pattern matching"""
        # Convert template to regex pattern
        regex_pattern = self._template_to_regex(pattern.template)
        
        match = re.match(regex_pattern, input_text, re.IGNORECASE)
        if match:
            entities = self._extract_entities_from_match(match, pattern)
            return MatchResult(
                pattern=pattern,
                confidence=1.0,
                entities=entities,
                match_type="exact"
            )
        
        return None
    
    def _try_fuzzy_match(self, input_text: str, pattern: Pattern) -> Optional[MatchResult]:
        """Try fuzzy pattern matching"""
        # Tokenize input and pattern
        input_tokens = self._tokenize(input_text)
        pattern_tokens = self._tokenize_template(pattern.template)
        
        # Calculate similarity
        similarity = self._calculate_token_similarity(input_tokens, pattern_tokens)
        
        if similarity >= self.similarity_threshold:
            entities = self._extract_entities_fuzzy(input_tokens, pattern_tokens, pattern)
            return MatchResult(
                pattern=pattern,
                confidence=similarity,
                entities=entities,
                match_type="fuzzy"
            )
        
        return None
    
    def _template_to_regex(self, template: str) -> str:
        """Convert pattern template to regex"""
        # Escape special regex characters
        regex = re.escape(template)
        
        # Replace escaped placeholders with capture groups
        # \{person\} becomes (.+?)
        regex = re.sub(r'\\{([^}]+)\\}', r'(.+?)', regex)
        
        return f"^{regex}$"
    
    def _extract_entities_from_match(self, match: re.Match, pattern: Pattern) -> Dict[str, str]:
        """Extract entities from regex match"""
        entities = {}
        
        # Find all placeholders in template
        placeholders = re.findall(r'{([^}]+)}', pattern.template)
        
        # Map captured groups to placeholders
        for i, placeholder in enumerate(placeholders):
            if i < len(match.groups()):
                entities[placeholder] = match.group(i + 1).strip()
        
        return entities
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        return [token.lower().strip() for token in text.split() if token.strip()]
    
    def _tokenize_template(self, template: str) -> List[Dict]:
        """Tokenize template preserving placeholders"""
        tokens = []
        parts = re.split(r'({[^}]+})', template)
        
        for part in parts:
            if part.strip():
                if part.startswith('{') and part.endswith('}'):
                    # Placeholder
                    tokens.append({
                        'type': 'placeholder',
                        'name': part[1:-1],
                        'text': part
                    })
                else:
                    # Regular words
                    for word in part.split():
                        if word.strip():
                            tokens.append({
                                'type': 'word',
                                'text': word.lower().strip()
                            })
        
        return tokens
    
    def _calculate_token_similarity(self, input_tokens: List[str], pattern_tokens: List[Dict]) -> float:
        """Calculate similarity between tokenized input and pattern"""
        # Extract just the word tokens for comparison
        pattern_words = [t['text'] for t in pattern_tokens if t['type'] == 'word']
        
        if not pattern_words:
            return 0.0
        
        # Use sequence matcher for similarity
        matcher = SequenceMatcher(None, input_tokens, pattern_words)
        return matcher.ratio()
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for matching"""
        return text.lower().strip()
```

Let me continue with the next TDD cycles...

## TDD Cycle 4: SPARQL Builder

### Test: SPARQL Generation
```python
# tests/test_sparql_builder.py
def test_basic_sparql_generation():
    """Test basic SPARQL query generation"""
    builder = SPARQLBuilder({
        "kb": "http://example.org/kb#",
        "foaf": "http://xmlns.com/foaf/0.1/"
    })
    
    match_result = MatchResult(
        pattern=Pattern(
            template="meetings with {person}",
            sparql_template="SELECT ?meeting WHERE { ?meeting kb:hasAttendee ?person . ?person foaf:name \"{person}\" }",
            entity_types={"person": "foaf:Person"},
            # ... other fields
        ),
        confidence=1.0,
        entities={"person": "John Smith"},
        match_type="exact"
    )
    
    sparql_query = builder.build_query(match_result)
    
    assert "PREFIX kb:" in sparql_query.query_text
    assert "PREFIX foaf:" in sparql_query.query_text
    assert "John Smith" in sparql_query.query_text
    assert sparql_query.variables == ["meeting"]

def test_sparql_injection_prevention():
    """Test SPARQL injection attack prevention"""
    builder = SPARQLBuilder({})
    
    # Malicious input with SPARQL injection
    malicious_input = "John'; DELETE WHERE {?s ?p ?o}; SELECT ?x WHERE {?x"
    
    match_result = MatchResult(
        entities={"person": malicious_input},
        # ... other fields
    )
    
    sparql_query = builder.build_query(match_result)
    
    # Should be escaped/sanitized
    assert "DELETE" not in sparql_query.query_text
    assert malicious_input not in sparql_query.query_text
```

This approach continues through all components, ensuring each is thoroughly tested before implementation. Would you like me to continue with the complete TDD implementation, or would you prefer to see the summary of Phase 4 artifacts?