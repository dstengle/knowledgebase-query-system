"""Main CLI entry point for KB Query."""

import sys
import click
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List

from ..services.query import QueryService
from ..core.entities import QueryRequest
from ..infrastructure.sparql_client import SPARQLClient, EndpointManager
from ..formatters.result_formatter import FormatterFactory, RichFormatter


@click.command()
@click.argument('query', required=False)
@click.option('--ontology', '-o', 
              type=click.Path(exists=True),
              help='Path to OWL ontology file',
              envvar='KB_QUERY_ONTOLOGY')
@click.option('--show-sparql', '-s', 
              is_flag=True,
              help='Show generated SPARQL query')
@click.option('--debug', '-d',
              is_flag=True,
              help='Enable debug mode')
@click.option('--limit', '-l',
              type=int,
              help='Limit number of results')
@click.option('--interactive', '-i',
              is_flag=True,
              help='Start interactive mode')
@click.option('--list-patterns', 
              is_flag=True,
              help='List available query patterns')
@click.option('--endpoint', '-e',
              help='SPARQL endpoint URL')
@click.option('--execute', '-x',
              is_flag=True,
              help='Execute query against endpoint')
@click.option('--format', '-f',
              type=click.Choice(['json', 'csv', 'table', 'rich', 'turtle']),
              default='rich',
              help='Output format for results')
@click.option('--config', '-c',
              type=click.Path(exists=True),
              help='Configuration file path')
@click.option('--test-connection',
              is_flag=True,
              help='Test connection to SPARQL endpoint')
@click.option('--graph', '-g',
              multiple=True,
              help='Named graph(s) to query (can be specified multiple times)')
@click.option('--default-graph',
              help='Default graph URI')
def main(query: Optional[str], 
         ontology: Optional[str],
         show_sparql: bool,
         debug: bool,
         limit: Optional[int],
         interactive: bool,
         list_patterns: bool,
         endpoint: Optional[str],
         execute: bool,
         format: str,
         config: Optional[str],
         test_connection: bool,
         graph: tuple,
         default_graph: Optional[str]):
    """KB Query CLI - Natural language SPARQL queries.
    
    Examples:
        kb-query "meetings with John Smith"
        kb-query -i  # Interactive mode
        kb-query --list-patterns
        kb-query -x -e http://dbpedia.org/sparql "cities in France"
        kb-query -x -e http://localhost:3030/dataset/sparql -g http://example.org/graph1 "meetings"
        kb-query --test-connection -e http://localhost:3030/kb/sparql
    """
    
    # Check for ontology file
    if not ontology:
        # Try to find default ontology
        default_paths = [
            Path('data/kb-vocabulary.ttl'),
            Path('kb-vocabulary.ttl'),
            Path.home() / '.config/kb-query/ontology.ttl'
        ]
        
        for path in default_paths:
            if path.exists():
                ontology = str(path)
                break
        
        if not ontology:
            click.echo("Error: No ontology file specified. Use --ontology or set KB_QUERY_ONTOLOGY", err=True)
            sys.exit(1)
    
    # Load configuration if provided
    config_data = {}
    if config:
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)
    
    # Override endpoint if provided
    if endpoint:
        if 'sparql' not in config_data:
            config_data['sparql'] = {}
        config_data['sparql']['endpoint'] = endpoint
    
    # Add graph configuration
    if graph or default_graph:
        if 'sparql' not in config_data:
            config_data['sparql'] = {}
        if graph:
            config_data['sparql']['named_graphs'] = list(graph)
        if default_graph:
            config_data['sparql']['default_graph'] = default_graph
    
    # Test connection if requested
    if test_connection:
        test_endpoint_connection(config_data)
        return
    
    # Initialize query service
    try:
        service = QueryService(ontology_path=ontology, config=config_data)
    except Exception as e:
        click.echo(f"Error initializing service: {e}", err=True)
        sys.exit(1)
    
    # Handle list patterns
    if list_patterns:
        patterns = service.list_available_patterns()
        click.echo("Available query patterns:")
        click.echo("-" * 40)
        for pattern in patterns:
            click.echo(pattern)
        return
    
    # Handle interactive mode
    if interactive or not query:
        run_interactive_mode(service, show_sparql, debug, limit, execute, format, config_data, graph, default_graph)
        return
    
    # Process single query
    process_single_query(service, query, show_sparql, debug, limit, execute, format, config_data, graph, default_graph)


def run_interactive_mode(service: QueryService, 
                        show_sparql: bool,
                        debug: bool,
                        limit: Optional[int],
                        execute: bool,
                        format: str,
                        config: Dict[str, Any],
                        graph: tuple,
                        default_graph: Optional[str]):
    """Run interactive REPL mode."""
    click.echo("KB Query Interactive Mode")
    click.echo("Type 'help' for commands, 'exit' to quit")
    click.echo("-" * 40)
    
    while True:
        try:
            # Get user input
            user_input = click.prompt('kb-query', default='', show_default=False)
            
            if not user_input:
                continue
                
            # Handle special commands
            if user_input.lower() == 'exit':
                break
            elif user_input.lower() == 'help':
                show_help()
                continue
            elif user_input.lower() == 'patterns':
                patterns = service.list_available_patterns()
                for pattern in patterns[:20]:  # Show first 20
                    click.echo(pattern)
                continue
            
            # Process query
            process_single_query(service, user_input, show_sparql, debug, limit, execute, format, config, graph, default_graph)
            
        except (KeyboardInterrupt, EOFError):
            click.echo("\nGoodbye!")
            break
        except Exception as e:
            click.echo(f"Error: {e}", err=True)


def process_single_query(service: QueryService,
                        query: str,
                        show_sparql: bool,
                        debug: bool,
                        limit: Optional[int],
                        execute: bool,
                        format: str,
                        config: Dict[str, Any],
                        graph: tuple,
                        default_graph: Optional[str]):
    """Process a single query."""
    # Create query request
    request = QueryRequest(
        input_text=query,
        show_sparql=show_sparql,
        debug=debug,
        limit=limit,
        named_graphs=list(graph) if graph else None,
        default_graph=default_graph
    )
    
    # Process query
    response = service.process_query(request)
    
    if response.success:
        click.echo(click.style("✓ Query understood", fg='green'))
        
        if response.sparql_query:
            click.echo("\nGenerated SPARQL:")
            click.echo("-" * 40)
            click.echo(response.sparql_query)
            click.echo("-" * 40)
        
        if response.debug_info:
            click.echo("\nDebug Information:")
            for key, value in response.debug_info.items():
                click.echo(f"  {key}: {value}")
        
        # Execute against endpoint if requested
        if execute and response.sparql_query:
            execute_sparql_query(response.sparql_query, format, config, graph, default_graph)
        
        click.echo(f"\nExecution time: {response.execution_time:.3f}s")
        
    else:
        click.echo(click.style(f"✗ {response.error_message}", fg='red'))
        
        if response.suggestions:
            click.echo("\nDid you mean:")
            for suggestion in response.suggestions:
                click.echo(f"  • {suggestion}")


def show_help():
    """Show interactive mode help."""
    help_text = """
Interactive Mode Commands:
  exit      - Exit the program
  help      - Show this help message
  patterns  - List available query patterns
  
Query Examples:
  meetings with John Smith
  todos assigned to Sarah
  John's meetings
  
Options can be set when starting interactive mode:
  kb-query -i --show-sparql  # Always show SPARQL
  kb-query -i --debug        # Enable debug mode
    """
    click.echo(help_text)


def test_endpoint_connection(config: Dict[str, Any]):
    """Test connection to SPARQL endpoint."""
    endpoint_url = config.get('sparql', {}).get('endpoint')
    
    if not endpoint_url:
        click.echo("Error: No endpoint specified", err=True)
        sys.exit(1)
    
    click.echo(f"Testing connection to {endpoint_url}...")
    
    try:
        client = SPARQLClient(
            endpoint=endpoint_url,
            timeout=config.get('sparql', {}).get('timeout', 30)
        )
        
        if client.test_connection():
            click.echo(click.style("✓ Connection successful!", fg='green'))
            
            # Try to get namespaces
            namespaces = client.get_namespaces()
            if namespaces:
                click.echo(f"Found {len(namespaces)} namespace(s)")
        else:
            click.echo(click.style("✗ Connection failed", fg='red'))
            sys.exit(1)
            
    except Exception as e:
        click.echo(click.style(f"✗ Connection error: {e}", fg='red'))
        sys.exit(1)


def execute_sparql_query(sparql: str, format_type: str, config: Dict[str, Any], 
                        graph: tuple = None, default_graph: Optional[str] = None):
    """Execute SPARQL query against endpoint."""
    endpoint_url = config.get('sparql', {}).get('endpoint')
    
    if not endpoint_url:
        click.echo("Error: No endpoint specified. Use --endpoint or config file", err=True)
        return
    
    click.echo(f"\nExecuting against {endpoint_url}...")
    
    try:
        client = SPARQLClient(
            endpoint=endpoint_url,
            timeout=config.get('sparql', {}).get('timeout', 30)
        )
        
        # Execute query (graph clauses are already added by the builder)
        results = client.execute_query(sparql)
        
        # Format and display results
        formatter = FormatterFactory.get_formatter(format_type)
        
        if format_type == 'rich' and isinstance(formatter, RichFormatter):
            formatter.print_results(results, title="Query Results")
        else:
            formatted = formatter.format(results)
            click.echo(formatted)
            
    except Exception as e:
        click.echo(click.style(f"✗ Execution error: {e}", fg='red'), err=True)


if __name__ == '__main__':
    main()