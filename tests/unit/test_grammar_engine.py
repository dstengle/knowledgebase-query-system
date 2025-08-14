"""Tests for Grammar Engine."""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock
from kb_query.core.grammar import GrammarEngine
from kb_query.core.entities import Pattern, Grammar
from kb_query.exceptions import GrammarError


class TestGrammarEngine:
    """Test Grammar Engine functionality."""
    
    @pytest.fixture
    def mock_cache_manager(self):
        """Create mock cache manager."""
        cache = Mock()
        cache.get.return_value = None
        cache.put.return_value = True
        return cache
    
    @pytest.fixture
    def sample_owl_content(self):
        """Sample OWL content for testing."""
        return """
        @prefix kb: <http://example.org/kb#> .
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix owl: <http://www.w3.org/2002/07/owl#> .
        @prefix foaf: <http://xmlns.com/foaf/0.1/> .
        
        kb:Meeting a owl:Class ;
            rdfs:label "Meeting" .
        
        kb:Person a owl:Class ;
            rdfs:label "Person" .
            
        kb:Todo a owl:Class ;
            rdfs:label "Todo" .
        
        kb:hasAttendee a owl:ObjectProperty ;
            rdfs:domain kb:Meeting ;
            rdfs:range foaf:Person ;
            rdfs:label "has attendee" .
            
        kb:assignedTo a owl:ObjectProperty ;
            rdfs:domain kb:Todo ;
            rdfs:range foaf:Person ;
            rdfs:label "assigned to" .
            
        kb:hasTag a owl:DatatypeProperty ;
            rdfs:domain kb:Meeting ;
            rdfs:range <http://www.w3.org/2001/XMLSchema#string> ;
            rdfs:label "has tag" .
        """
    
    def test_parse_owl_file(self, mock_cache_manager, sample_owl_content):
        """Test parsing OWL ontology file."""
        engine = GrammarEngine(cache_manager=mock_cache_manager)
        
        # Create temporary OWL file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ttl', delete=False) as f:
            f.write(sample_owl_content)
            owl_path = f.name
        
        try:
            # Parse and generate grammar
            grammar = engine.load_grammar(owl_path)
            
            # Verify grammar structure
            assert isinstance(grammar, Grammar)
            assert len(grammar.patterns) > 0
            assert grammar.ontology_hash is not None
            assert 'kb' in grammar.namespaces
            
            # Check that patterns were generated for properties
            property_names = [p.property for p in grammar.patterns]
            assert any('hasAttendee' in prop for prop in property_names)
            assert any('assignedTo' in prop for prop in property_names)
            
        finally:
            os.unlink(owl_path)
    
    def test_pattern_generation_from_properties(self, mock_cache_manager):
        """Test pattern generation from ontology properties."""
        engine = GrammarEngine(cache_manager=mock_cache_manager)
        
        ontology_data = {
            'classes': ['kb:Meeting', 'kb:Person', 'kb:Todo'],
            'properties': [
                {
                    'name': 'kb:hasAttendee',
                    'domain': 'kb:Meeting',
                    'range': 'foaf:Person',
                    'type': 'object_property'
                },
                {
                    'name': 'kb:assignedTo',
                    'domain': 'kb:Todo',
                    'range': 'foaf:Person',
                    'type': 'object_property'
                }
            ],
            'namespaces': {
                'kb': 'http://example.org/kb#',
                'foaf': 'http://xmlns.com/foaf/0.1/'
            }
        }
        
        patterns = engine.generate_patterns(ontology_data)
        
        # Should generate multiple patterns per property
        assert len(patterns) >= 4  # At least 2 patterns per property
        
        # Check for meeting patterns
        meeting_patterns = [p for p in patterns if 'meeting' in p.template.lower()]
        assert len(meeting_patterns) > 0
        
        # Check for todo patterns
        todo_patterns = [p for p in patterns if 'todo' in p.template.lower()]
        assert len(todo_patterns) > 0
        
        # Verify pattern structure
        for pattern in patterns:
            assert pattern.sparql_template
            assert pattern.entity_types
            assert pattern.examples
            assert pattern.confidence > 0
    
    def test_cache_usage(self, mock_cache_manager, sample_owl_content):
        """Test that grammar is cached after generation."""
        engine = GrammarEngine(cache_manager=mock_cache_manager)
        
        # Create temporary OWL file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ttl', delete=False) as f:
            f.write(sample_owl_content)
            owl_path = f.name
        
        try:
            # First load - should generate and cache
            grammar1 = engine.load_grammar(owl_path)
            
            # Verify cache was called
            assert mock_cache_manager.put.called
            cache_key = mock_cache_manager.put.call_args[0][0]
            assert 'grammar_' in cache_key
            
            # Second load - should use cache
            mock_cache_manager.get.return_value = grammar1.__dict__
            grammar2 = engine.load_grammar(owl_path)
            
            # Should get from cache
            assert mock_cache_manager.get.called
            
        finally:
            os.unlink(owl_path)
    
    def test_pattern_template_generation(self, mock_cache_manager):
        """Test SPARQL template generation for patterns."""
        engine = GrammarEngine(cache_manager=mock_cache_manager)
        
        prop_info = {
            'name': 'kb:hasAttendee',
            'domain': 'kb:Meeting',
            'range': 'foaf:Person',
            'type': 'object_property'
        }
        
        patterns = engine._generate_property_patterns(prop_info)
        
        for pattern in patterns:
            # Check SPARQL template includes necessary components
            assert 'SELECT' in pattern.sparql_template
            assert '?meeting' in pattern.sparql_template.lower() or '?entity' in pattern.sparql_template.lower()
            assert 'hasAttendee' in pattern.sparql_template
            
            # Check template has placeholder
            assert '{' in pattern.template and '}' in pattern.template
    
    def test_error_handling_invalid_file(self, mock_cache_manager):
        """Test error handling for invalid OWL file."""
        engine = GrammarEngine(cache_manager=mock_cache_manager)
        
        with pytest.raises(GrammarError):
            engine.load_grammar('/nonexistent/file.ttl')
    
    def test_extract_base_name(self, mock_cache_manager):
        """Test property base name extraction."""
        engine = GrammarEngine(cache_manager=mock_cache_manager)
        
        assert engine._extract_base_name('kb:hasAttendee') == 'attendee'
        assert engine._extract_base_name('kb:assignedTo') == 'assignedto'
        assert engine._extract_base_name('kb:isPartOf') == 'partof'
        assert engine._extract_base_name('kb:belongsTo') == 'belongsto'
        assert engine._extract_base_name('http://example.org/kb#hasTag') == 'tag'