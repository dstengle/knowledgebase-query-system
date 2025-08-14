"""Tests for core data entities."""

import pytest
from kb_query.core.entities import (
    Pattern, Grammar, MatchResult, QueryRequest, QueryResponse,
    SPARQLQuery, Endpoint, Profile, GlobalSettings
)
from kb_query.exceptions import ValidationError


class TestPattern:
    """Test Pattern data structure."""
    
    def test_valid_pattern_creation(self):
        """Test creating a valid pattern."""
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
        
        assert pattern.id == "test_001"
        assert "person" in pattern.entity_types
        assert pattern.confidence == 0.95
        assert len(pattern.keywords) > 0
        assert "meetings" in pattern.keywords
    
    def test_pattern_validation_no_placeholders(self):
        """Test pattern validation fails without placeholders."""
        with pytest.raises(ValidationError, match="no entity placeholders"):
            Pattern(
                id="invalid",
                template="meetings only",  # No {entity}
                sparql_template="SELECT * WHERE { ?s ?p ?o }",
                entity_types={},
                examples=["meetings only"],
                confidence=0.5,
                domain_class="kb:Meeting",
                property="kb:hasAttendee"
            )
    
    def test_pattern_validation_invalid_confidence(self):
        """Test pattern validation fails with invalid confidence."""
        with pytest.raises(ValidationError, match="confidence must be"):
            Pattern(
                id="invalid",
                template="meetings with {person}",
                sparql_template="SELECT * WHERE { ?s ?p ?o }",
                entity_types={"person": "foaf:Person"},
                examples=["meetings with John"],
                confidence=1.5,  # Invalid confidence > 1.0
                domain_class="kb:Meeting",
                property="kb:hasAttendee"
            )
    
    def test_pattern_validation_no_examples(self):
        """Test pattern validation fails without examples."""
        with pytest.raises(ValidationError, match="must have at least one example"):
            Pattern(
                id="invalid",
                template="meetings with {person}",
                sparql_template="SELECT * WHERE { ?s ?p ?o }",
                entity_types={"person": "foaf:Person"},
                examples=[],  # No examples
                confidence=0.8,
                domain_class="kb:Meeting",
                property="kb:hasAttendee"
            )
    
    def test_keyword_extraction(self):
        """Test keyword extraction from template."""
        pattern = Pattern(
            id="test",
            template="find meetings with {person} about {topic}",
            sparql_template="SELECT * WHERE { ?s ?p ?o }",
            entity_types={"person": "foaf:Person", "topic": "xsd:string"},
            examples=["find meetings with John about AI"],
            confidence=0.8,
            domain_class="kb:Meeting",
            property="kb:hasAttendee"
        )
        
        # Should extract "find", "meetings", "about" (excluding short words like "with")
        assert "find" in pattern.keywords
        assert "meetings" in pattern.keywords
        assert "about" in pattern.keywords
        assert "with" not in pattern.keywords  # Short word filtered out


class TestGrammar:
    """Test Grammar data structure."""
    
    def test_valid_grammar_creation(self):
        """Test creating a valid grammar."""
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
            ontology_hash="test_hash_123",
            namespaces={"kb": "http://example.org/kb#"},
            created_at="2025-08-06T12:00:00"
        )
        
        assert len(grammar.patterns) == 1
        assert grammar.ontology_hash == "test_hash_123"
        assert "kb" in grammar.namespaces
    
    def test_grammar_validation_no_patterns(self):
        """Test grammar validation fails without patterns."""
        with pytest.raises(ValidationError, match="must contain at least one pattern"):
            Grammar(
                patterns=[],  # No patterns
                ontology_hash="test_hash",
                namespaces={"kb": "http://example.org/kb#"},
                created_at="2025-08-06"
            )
    
    def test_find_patterns_by_keyword(self):
        """Test finding patterns by keyword."""
        pattern1 = Pattern(
            id="meetings",
            template="meetings with {person}",
            sparql_template="SELECT ?meeting WHERE { ?meeting kb:hasAttendee ?person }",
            entity_types={"person": "foaf:Person"},
            examples=["meetings with John"],
            confidence=0.95,
            domain_class="kb:Meeting",
            property="kb:hasAttendee"
        )
        
        pattern2 = Pattern(
            id="todos",
            template="todos assigned to {person}",
            sparql_template="SELECT ?todo WHERE { ?todo kb:assignedTo ?person }",
            entity_types={"person": "foaf:Person"},
            examples=["todos assigned to Sarah"],
            confidence=0.9,
            domain_class="kb:Todo",
            property="kb:assignedTo"
        )
        
        grammar = Grammar(
            patterns=[pattern1, pattern2],
            ontology_hash="test_hash",
            namespaces={"kb": "http://example.org/kb#"},
            created_at="2025-08-06"
        )
        
        meeting_patterns = grammar.find_patterns_by_keyword("meetings")
        assert len(meeting_patterns) == 1
        assert meeting_patterns[0].id == "meetings"
        
        todo_patterns = grammar.find_patterns_by_keyword("todos")
        assert len(todo_patterns) == 1
        assert todo_patterns[0].id == "todos"


class TestMatchResult:
    """Test MatchResult data structure."""
    
    def test_valid_match_result(self):
        """Test creating a valid match result."""
        pattern = Pattern(
            id="test",
            template="meetings with {person}",
            sparql_template="SELECT * WHERE { ?s ?p ?o }",
            entity_types={"person": "foaf:Person"},
            examples=["meetings with John"],
            confidence=0.8,
            domain_class="kb:Meeting",
            property="kb:hasAttendee"
        )
        
        match = MatchResult(
            pattern=pattern,
            confidence=0.95,
            entities={"person": "John Smith"},
            match_type="exact"
        )
        
        assert match.confidence == 0.95
        assert match.entities["person"] == "John Smith"
        assert match.match_type == "exact"
    
    def test_match_result_invalid_confidence(self):
        """Test match result validation with invalid confidence."""
        pattern = Pattern(
            id="test",
            template="meetings with {person}",
            sparql_template="SELECT * WHERE { ?s ?p ?o }",
            entity_types={"person": "foaf:Person"},
            examples=["meetings with John"],
            confidence=0.8,
            domain_class="kb:Meeting",
            property="kb:hasAttendee"
        )
        
        with pytest.raises(ValidationError, match="confidence must be"):
            MatchResult(
                pattern=pattern,
                confidence=1.5,  # Invalid
                entities={"person": "John Smith"},
                match_type="exact"
            )
    
    def test_match_result_invalid_type(self):
        """Test match result validation with invalid type."""
        pattern = Pattern(
            id="test",
            template="meetings with {person}",
            sparql_template="SELECT * WHERE { ?s ?p ?o }",
            entity_types={"person": "foaf:Person"},
            examples=["meetings with John"],
            confidence=0.8,
            domain_class="kb:Meeting",
            property="kb:hasAttendee"
        )
        
        with pytest.raises(ValidationError, match="Invalid match type"):
            MatchResult(
                pattern=pattern,
                confidence=0.95,
                entities={"person": "John Smith"},
                match_type="invalid_type"
            )


class TestQueryRequest:
    """Test QueryRequest data structure."""
    
    def test_valid_query_request(self):
        """Test creating a valid query request."""
        request = QueryRequest(
            input_text="meetings with John Smith",
            profile="dev",
            debug=True,
            show_sparql=False,
            limit=50
        )
        
        assert request.input_text == "meetings with John Smith"
        assert request.profile == "dev"
        assert request.debug is True
        assert request.limit == 50
    
    def test_query_request_empty_input(self):
        """Test query request validation with empty input."""
        with pytest.raises(ValidationError, match="Query input cannot be empty"):
            QueryRequest(input_text="   ")  # Only whitespace
    
    def test_query_request_invalid_limit(self):
        """Test query request validation with invalid limit."""
        with pytest.raises(ValidationError, match="Limit must be positive"):
            QueryRequest(
                input_text="meetings with John",
                limit=0  # Invalid limit
            )


class TestEndpoint:
    """Test Endpoint data structure."""
    
    def test_valid_endpoint_basic_auth(self):
        """Test creating endpoint with basic auth."""
        endpoint = Endpoint(
            name="test",
            url="http://localhost:3030/test",
            auth_type="basic",
            credentials={"username": "user", "password": "pass"},
            timeout=30,
            verify_ssl=False
        )
        
        assert endpoint.name == "test"
        assert endpoint.auth_type == "basic"
        assert "username" in endpoint.credentials
    
    def test_endpoint_invalid_auth_type(self):
        """Test endpoint validation with invalid auth type."""
        with pytest.raises(ValidationError, match="Invalid auth type"):
            Endpoint(
                name="test",
                url="http://localhost:3030/test",
                auth_type="invalid",
                credentials={}
            )
    
    def test_endpoint_missing_basic_credentials(self):
        """Test endpoint validation with missing basic auth credentials."""
        with pytest.raises(ValidationError, match="Basic auth requires"):
            Endpoint(
                name="test",
                url="http://localhost:3030/test",
                auth_type="basic",
                credentials={"username": "user"}  # Missing password
            )