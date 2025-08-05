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
