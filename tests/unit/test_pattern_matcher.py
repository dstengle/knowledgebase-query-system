"""Tests for Pattern Matcher."""

import pytest
from kb_query.core.matcher import PatternMatcher
from kb_query.core.entities import Pattern, Grammar, MatchResult


class TestPatternMatcher:
    """Test Pattern Matcher functionality."""
    
    @pytest.fixture
    def sample_patterns(self):
        """Create sample patterns for testing."""
        pattern1 = Pattern(
            id="test_001",
            template="meetings with {person}",
            sparql_template="SELECT ?meeting WHERE { ?meeting kb:hasAttendee ?person }",
            entity_types={"person": "foaf:Person"},
            examples=["meetings with John Smith"],
            confidence=0.95,
            domain_class="kb:Meeting",
            property="kb:hasAttendee"
        )
        
        pattern2 = Pattern(
            id="test_002",
            template="{person}'s meetings",
            sparql_template="SELECT ?meeting WHERE { ?meeting kb:hasAttendee ?person }",
            entity_types={"person": "foaf:Person"},
            examples=["John's meetings"],
            confidence=0.90,
            domain_class="kb:Meeting",
            property="kb:hasAttendee"
        )
        
        pattern3 = Pattern(
            id="test_003",
            template="todos assigned to {person}",
            sparql_template="SELECT ?todo WHERE { ?todo kb:assignedTo ?person }",
            entity_types={"person": "foaf:Person"},
            examples=["todos assigned to Sarah"],
            confidence=0.85,
            domain_class="kb:Todo",
            property="kb:assignedTo"
        )
        
        return [pattern1, pattern2, pattern3]
    
    @pytest.fixture
    def sample_grammar(self, sample_patterns):
        """Create sample grammar for testing."""
        return Grammar(
            patterns=sample_patterns,
            ontology_hash="test_hash",
            namespaces={"kb": "http://example.org/kb#"},
            created_at="2025-08-06T12:00:00"
        )
    
    def test_exact_match(self, sample_grammar):
        """Test exact pattern matching."""
        matcher = PatternMatcher()
        
        matches = matcher.find_matches("meetings with John Smith", sample_grammar)
        
        assert len(matches) == 1
        assert matches[0].confidence == 1.0
        assert matches[0].match_type == "exact"
        assert matches[0].entities["person"] == "John Smith"
        assert matches[0].pattern.id == "test_001"
    
    def test_fuzzy_match_with_typo(self, sample_grammar):
        """Test fuzzy matching with typos."""
        matcher = PatternMatcher(similarity_threshold=0.7)
        
        # "meetigns" instead of "meetings"
        matches = matcher.find_matches("meetigns with John Smith", sample_grammar)
        
        assert len(matches) >= 1
        assert matches[0].confidence > 0.7
        assert matches[0].match_type == "fuzzy"
        assert "person" in matches[0].entities
    
    def test_possessive_pattern_match(self, sample_grammar):
        """Test matching possessive patterns."""
        matcher = PatternMatcher()
        
        matches = matcher.find_matches("Sarah's meetings", sample_grammar)
        
        assert len(matches) == 1
        assert matches[0].entities["person"] == "Sarah"
        assert matches[0].pattern.id == "test_002"
    
    def test_todo_pattern_match(self, sample_grammar):
        """Test matching todo patterns."""
        matcher = PatternMatcher()
        
        matches = matcher.find_matches("todos assigned to John Smith", sample_grammar)
        
        assert len(matches) == 1
        assert matches[0].entities["person"] == "John Smith"
        assert matches[0].pattern.id == "test_003"
    
    def test_no_match(self, sample_grammar):
        """Test when no patterns match."""
        matcher = PatternMatcher()
        
        matches = matcher.find_matches("completely unrelated query", sample_grammar)
        
        assert len(matches) == 0
    
    def test_entity_extraction_multiple_words(self, sample_grammar):
        """Test entity extraction with multiple word entities."""
        matcher = PatternMatcher()
        
        matches = matcher.find_matches("meetings with John Paul Smith Jr.", sample_grammar)
        
        assert len(matches) == 1
        assert matches[0].entities["person"] == "John Paul Smith Jr."
    
    def test_case_insensitive_matching(self, sample_grammar):
        """Test case insensitive pattern matching."""
        matcher = PatternMatcher()
        
        matches = matcher.find_matches("MEETINGS WITH john smith", sample_grammar)
        
        assert len(matches) == 1
        assert matches[0].entities["person"] == "john smith"
    
    def test_similarity_threshold(self, sample_grammar):
        """Test that similarity threshold filters matches."""
        matcher = PatternMatcher(similarity_threshold=0.9)
        
        # This should not match due to high threshold
        matches = matcher.find_matches("meeting with John", sample_grammar)
        
        # With high threshold, partial match should be filtered
        assert len(matches) == 0 or all(m.confidence >= 0.9 for m in matches)
    
    def test_suggest_corrections(self, sample_grammar):
        """Test query suggestion generation for failed matches."""
        matcher = PatternMatcher()
        
        suggestions = matcher.suggest_corrections("meting with person", sample_grammar)
        
        assert len(suggestions) > 0
        assert any("meetings with" in s.lower() for s in suggestions)
    
    def test_extract_entities_from_template(self):
        """Test entity extraction from a template."""
        matcher = PatternMatcher()
        
        pattern = Pattern(
            id="test",
            template="meetings with {person} about {topic}",
            sparql_template="SELECT * WHERE { ?s ?p ?o }",
            entity_types={"person": "foaf:Person", "topic": "xsd:string"},
            examples=["meetings with John about AI"],
            confidence=0.8,
            domain_class="kb:Meeting",
            property="kb:hasAttendee"
        )
        
        entities = matcher.extract_entities(
            "meetings with Sarah Chen about project planning",
            pattern
        )
        
        assert entities["person"] == "Sarah Chen"
        assert entities["topic"] == "project planning"