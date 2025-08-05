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
