"""Result formatters for SPARQL query results."""

import json
import csv
import io
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich.panel import Panel
from rich.text import Text


class ResultFormatter:
    """Base class for result formatters."""
    
    def format(self, results: Dict[str, Any], **kwargs) -> str:
        """Format results to string."""
        raise NotImplementedError


class JSONFormatter(ResultFormatter):
    """Format results as JSON."""
    
    def format(self, results: Dict[str, Any], pretty: bool = True, **kwargs) -> str:
        """
        Format results as JSON.
        
        Args:
            results: Query results
            pretty: Whether to pretty-print JSON
            
        Returns:
            JSON string
        """
        if pretty:
            return json.dumps(results, indent=2, ensure_ascii=False)
        else:
            return json.dumps(results, ensure_ascii=False)


class CSVFormatter(ResultFormatter):
    """Format results as CSV."""
    
    def format(self, results: Dict[str, Any], **kwargs) -> str:
        """
        Format results as CSV.
        
        Args:
            results: Query results
            
        Returns:
            CSV string
        """
        output = io.StringIO()
        
        # Extract bindings
        bindings = results.get('results', {}).get('bindings', [])
        if not bindings:
            return ""
        
        # Get column headers from first result
        headers = list(bindings[0].keys())
        
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        
        for binding in bindings:
            writer.writerow(binding)
        
        return output.getvalue()


class TableFormatter(ResultFormatter):
    """Format results as ASCII table."""
    
    def format(self, results: Dict[str, Any], max_width: Optional[int] = None, **kwargs) -> str:
        """
        Format results as ASCII table.
        
        Args:
            results: Query results
            max_width: Maximum column width
            
        Returns:
            ASCII table string
        """
        bindings = results.get('results', {}).get('bindings', [])
        if not bindings:
            return "No results found."
        
        # Get headers
        headers = list(bindings[0].keys())
        
        # Build table rows
        rows = []
        for binding in bindings:
            row = []
            for header in headers:
                value = str(binding.get(header, ''))
                if max_width and len(value) > max_width:
                    value = value[:max_width-3] + '...'
                row.append(value)
            rows.append(row)
        
        # Calculate column widths
        col_widths = []
        for i, header in enumerate(headers):
            width = len(header)
            for row in rows:
                width = max(width, len(row[i]))
            col_widths.append(width)
        
        # Build table
        lines = []
        
        # Header
        header_line = '| ' + ' | '.join(h.ljust(w) for h, w in zip(headers, col_widths)) + ' |'
        separator = '|-' + '-|-'.join('-' * w for w in col_widths) + '-|'
        
        lines.append(separator)
        lines.append(header_line)
        lines.append(separator)
        
        # Rows
        for row in rows:
            row_line = '| ' + ' | '.join(v.ljust(w) for v, w in zip(row, col_widths)) + ' |'
            lines.append(row_line)
        
        lines.append(separator)
        
        return '\n'.join(lines)


class RichFormatter(ResultFormatter):
    """Format results using Rich library for terminal display."""
    
    def format(self, results: Dict[str, Any], title: str = "Query Results", **kwargs) -> str:
        """
        Format results using Rich.
        
        Args:
            results: Query results
            title: Table title
            
        Returns:
            Formatted string (for non-terminal output)
        """
        console = Console()
        
        bindings = results.get('results', {}).get('bindings', [])
        
        if not bindings:
            panel = Panel("No results found", title=title, border_style="yellow")
            with console.capture() as capture:
                console.print(panel)
            return capture.get()
        
        # Create table
        table = Table(title=title, show_header=True, header_style="bold magenta")
        
        # Add columns
        headers = list(bindings[0].keys())
        for header in headers:
            table.add_column(header, style="cyan", no_wrap=False)
        
        # Add rows
        for binding in bindings:
            row = [str(binding.get(h, '')) for h in headers]
            table.add_row(*row)
        
        # Capture output
        with console.capture() as capture:
            console.print(table)
        
        return capture.get()
    
    def print_results(self, results: Dict[str, Any], title: str = "Query Results"):
        """
        Print results directly to console.
        
        Args:
            results: Query results
            title: Table title
        """
        console = Console()
        
        bindings = results.get('results', {}).get('bindings', [])
        
        if not bindings:
            panel = Panel("No results found", title=title, border_style="yellow")
            console.print(panel)
            return
        
        # Create table
        table = Table(title=title, show_header=True, header_style="bold magenta")
        
        # Add columns
        headers = list(bindings[0].keys())
        for header in headers:
            table.add_column(header, style="cyan", no_wrap=False)
        
        # Add rows with alternating colors
        for i, binding in enumerate(bindings):
            style = "white" if i % 2 == 0 else "bright_white"
            row = [str(binding.get(h, '')) for h in headers]
            table.add_row(*row, style=style)
        
        console.print(table)
        
        # Print summary
        count_text = Text(f"\n{len(bindings)} result(s) found", style="bold green")
        console.print(count_text)


class TurtleFormatter(ResultFormatter):
    """Format results as Turtle RDF."""
    
    def format(self, results: Dict[str, Any], **kwargs) -> str:
        """
        Format results as Turtle.
        
        Args:
            results: Query results
            
        Returns:
            Turtle string
        """
        # For CONSTRUCT queries, results might already be in RDF format
        if isinstance(results, str):
            return results
        
        # For SELECT queries, create simple triples
        bindings = results.get('results', {}).get('bindings', [])
        if not bindings:
            return ""
        
        lines = ["@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> ."]
        lines.append("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .")
        lines.append("")
        
        for i, binding in enumerate(bindings):
            subject = f"_:result{i}"
            for key, value in binding.items():
                # Simple literal representation
                if value.startswith("http://") or value.startswith("https://"):
                    lines.append(f'{subject} rdfs:label "{key}" .')
                    lines.append(f'{subject} <{value}> "{key}" .')
                else:
                    lines.append(f'{subject} rdfs:label "{key}" .')
                    lines.append(f'{subject} rdfs:comment "{value}" .')
            lines.append("")
        
        return '\n'.join(lines)


class FormatterFactory:
    """Factory for creating result formatters."""
    
    FORMATTERS = {
        'json': JSONFormatter,
        'csv': CSVFormatter,
        'table': TableFormatter,
        'rich': RichFormatter,
        'turtle': TurtleFormatter,
        'ttl': TurtleFormatter
    }
    
    @classmethod
    def get_formatter(cls, format_type: str) -> ResultFormatter:
        """
        Get a formatter instance.
        
        Args:
            format_type: Type of formatter
            
        Returns:
            Formatter instance
            
        Raises:
            ValueError: If format type is unknown
        """
        formatter_class = cls.FORMATTERS.get(format_type.lower())
        if not formatter_class:
            raise ValueError(f"Unknown format type: {format_type}")
        
        return formatter_class()
    
    @classmethod
    def list_formats(cls) -> List[str]:
        """
        List available format types.
        
        Returns:
            List of format type names
        """
        return list(cls.FORMATTERS.keys())