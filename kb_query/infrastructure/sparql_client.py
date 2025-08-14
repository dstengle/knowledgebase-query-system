"""SPARQL endpoint client for query execution."""

import json
import logging
from typing import Dict, List, Optional, Any
from SPARQLWrapper import SPARQLWrapper, JSON, JSONLD, XML, TURTLE, N3
from SPARQLWrapper.SPARQLExceptions import SPARQLWrapperException, EndPointNotFound
import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth

from ..exceptions import SPARQLError, EndpointConnectionError

logger = logging.getLogger(__name__)


class SPARQLClient:
    """Client for executing SPARQL queries against endpoints."""
    
    RESULT_FORMATS = {
        'json': JSON,
        'jsonld': JSONLD,
        'xml': XML,
        'turtle': TURTLE,
        'n3': N3
    }
    
    def __init__(self, 
                 endpoint: str,
                 timeout: int = 30,
                 auth_type: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 headers: Optional[Dict[str, str]] = None):
        """
        Initialize SPARQL client.
        
        Args:
            endpoint: SPARQL endpoint URL
            timeout: Query timeout in seconds
            auth_type: Authentication type ('basic', 'digest', or None)
            username: Username for authentication
            password: Password for authentication
            headers: Additional HTTP headers
        """
        self.endpoint = endpoint
        self.timeout = timeout
        self.auth_type = auth_type
        self.username = username
        self.password = password
        self.headers = headers or {}
        
        # Initialize SPARQLWrapper
        self.sparql = SPARQLWrapper(endpoint)
        self.sparql.setTimeout(timeout)
        
        # Set authentication if provided
        if auth_type and username and password:
            if auth_type == 'basic':
                self.sparql.setHTTPAuth('BASIC')
                self.sparql.setCredentials(username, password)
            elif auth_type == 'digest':
                self.sparql.setHTTPAuth('DIGEST')
                self.sparql.setCredentials(username, password)
        
        # Set custom headers
        for key, value in self.headers.items():
            self.sparql.addCustomHttpHeader(key, value)
    
    def execute_query(self, 
                     query: str, 
                     result_format: str = 'json') -> Any:
        """
        Execute a SPARQL SELECT/ASK query.
        
        Args:
            query: SPARQL query string
            result_format: Desired result format
            
        Returns:
            Query results in specified format
            
        Raises:
            SPARQLError: If query execution fails
            ConnectionError: If endpoint is unreachable
        """
        try:
            # Set query and return format
            self.sparql.setQuery(query)
            
            if result_format in self.RESULT_FORMATS:
                self.sparql.setReturnFormat(self.RESULT_FORMATS[result_format])
            else:
                self.sparql.setReturnFormat(JSON)
            
            # Execute query
            logger.debug(f"Executing query against {self.endpoint}")
            results = self.sparql.query().convert()
            
            # Process results based on format
            if result_format == 'json':
                return self._process_json_results(results)
            else:
                return results
                
        except EndPointNotFound as e:
            logger.error(f"Endpoint not found: {self.endpoint}")
            raise EndpointConnectionError(f"SPARQL endpoint not found: {self.endpoint}", self.endpoint) from e
        except SPARQLWrapperException as e:
            logger.error(f"SPARQL query failed: {e}")
            raise SPARQLError(f"Query execution failed: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise SPARQLError(f"Unexpected error during query execution: {str(e)}") from e
    
    def execute_update(self, update: str) -> bool:
        """
        Execute a SPARQL UPDATE query (INSERT/DELETE).
        
        Args:
            update: SPARQL UPDATE string
            
        Returns:
            True if successful
            
        Raises:
            SPARQLError: If update fails
        """
        try:
            # Use requests for UPDATE queries as SPARQLWrapper has limited support
            response = requests.post(
                self.endpoint,
                data={'update': update},
                headers={'Content-Type': 'application/sparql-update'},
                timeout=self.timeout,
                auth=self._get_auth()
            )
            
            response.raise_for_status()
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"UPDATE query failed: {e}")
            raise SPARQLError(f"UPDATE query failed: {str(e)}") from e
    
    def test_connection(self) -> bool:
        """
        Test connection to SPARQL endpoint.
        
        Returns:
            True if endpoint is reachable
        """
        try:
            # Simple ASK query to test connection
            test_query = "ASK WHERE { ?s ?p ?o }"
            self.sparql.setQuery(test_query)
            self.sparql.setReturnFormat(JSON)
            result = self.sparql.query().convert()
            return True
        except Exception as e:
            logger.warning(f"Connection test failed: {e}")
            return False
    
    def get_namespaces(self) -> Dict[str, str]:
        """
        Retrieve namespaces from the endpoint.
        
        Returns:
            Dictionary of prefix: namespace mappings
        """
        try:
            query = """
            SELECT DISTINCT ?prefix ?namespace
            WHERE {
                ?s ?p ?o .
                BIND(REPLACE(STR(?p), "^([^#/]*[#/]).*", "$1") AS ?namespace)
                BIND(REPLACE(STR(?namespace), "^.*/([^#/]+)[#/]?$", "$1") AS ?prefix)
            }
            LIMIT 100
            """
            
            results = self.execute_query(query)
            namespaces = {}
            
            for binding in results.get('results', {}).get('bindings', []):
                if 'prefix' in binding and 'namespace' in binding:
                    prefix = binding['prefix']['value']
                    namespace = binding['namespace']['value']
                    if prefix and namespace:
                        namespaces[prefix] = namespace
            
            return namespaces
            
        except Exception as e:
            logger.warning(f"Could not retrieve namespaces: {e}")
            return {}
    
    def _process_json_results(self, results: Dict) -> Dict:
        """
        Process JSON results to a cleaner format.
        
        Args:
            results: Raw JSON results from SPARQL endpoint
            
        Returns:
            Processed results dictionary
        """
        if not isinstance(results, dict):
            return {'results': results}
        
        # For SELECT queries
        if 'results' in results and 'bindings' in results['results']:
            processed_bindings = []
            
            for binding in results['results']['bindings']:
                processed_binding = {}
                for var, value_obj in binding.items():
                    # Extract just the value, not the full object
                    if isinstance(value_obj, dict) and 'value' in value_obj:
                        processed_binding[var] = value_obj['value']
                    else:
                        processed_binding[var] = value_obj
                processed_bindings.append(processed_binding)
            
            return {
                'head': results.get('head', {}),
                'results': {
                    'bindings': processed_bindings
                }
            }
        
        # For ASK queries
        if 'boolean' in results:
            return {'boolean': results['boolean']}
        
        # Return as-is if structure is unknown
        return results
    
    def _get_auth(self) -> Optional[Any]:
        """
        Get authentication object for requests.
        
        Returns:
            Authentication object or None
        """
        if not self.auth_type or not self.username or not self.password:
            return None
        
        if self.auth_type == 'basic':
            return HTTPBasicAuth(self.username, self.password)
        elif self.auth_type == 'digest':
            return HTTPDigestAuth(self.username, self.password)
        
        return None


class EndpointManager:
    """Manages multiple SPARQL endpoints and configurations."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize endpoint manager with configuration.
        
        Args:
            config: Configuration dictionary with endpoint settings
        """
        self.config = config
        self.clients: Dict[str, SPARQLClient] = {}
        self.default_endpoint = config.get('sparql', {}).get('endpoint')
    
    def get_client(self, endpoint_name: Optional[str] = None) -> SPARQLClient:
        """
        Get or create a SPARQL client for the specified endpoint.
        
        Args:
            endpoint_name: Name of the endpoint or None for default
            
        Returns:
            SPARQLClient instance
        """
        if not endpoint_name:
            endpoint_name = 'default'
        
        if endpoint_name not in self.clients:
            endpoint_config = self._get_endpoint_config(endpoint_name)
            self.clients[endpoint_name] = SPARQLClient(
                endpoint=endpoint_config['url'],
                timeout=endpoint_config.get('timeout', 30),
                auth_type=endpoint_config.get('auth_type'),
                username=endpoint_config.get('username'),
                password=endpoint_config.get('password'),
                headers=endpoint_config.get('headers', {})
            )
        
        return self.clients[endpoint_name]
    
    def _get_endpoint_config(self, endpoint_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific endpoint.
        
        Args:
            endpoint_name: Name of the endpoint
            
        Returns:
            Endpoint configuration dictionary
        """
        if endpoint_name == 'default':
            return {
                'url': self.config.get('sparql', {}).get('endpoint'),
                'timeout': self.config.get('sparql', {}).get('timeout', 30)
            }
        
        # Look for named endpoints in config
        endpoints = self.config.get('sparql', {}).get('endpoints', {})
        if endpoint_name in endpoints:
            return endpoints[endpoint_name]
        
        raise ValueError(f"Unknown endpoint: {endpoint_name}")