# KB Query CLI - Natural Language SPARQL Interface

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-17%20passing-green.svg)](#testing)
[![Coverage](https://img.shields.io/badge/coverage-79%25-yellow.svg)](#testing)

A powerful command-line interface that converts natural language queries into SPARQL using OWL ontologies. Built with the SPARC methodology (Specification, Pseudocode, Architecture, Refinement, Completion) for systematic development.

## ✨ Features

- 🗣️ **Natural Language Queries**: "meetings with John Smith", "todos assigned to Sarah"
- 🧠 **Automatic Pattern Generation**: Creates query patterns from OWL ontology structure
- ⚡ **Interactive & Command Modes**: Both REPL and single-command execution
- 🎯 **No SPARQL Knowledge Required**: Users query in plain English
- 🔍 **Intelligent Suggestions**: Provides corrections for failed queries
- 📊 **Debug Mode**: Shows pattern matching and SPARQL generation details
- 🌐 **SPARQL Endpoint Execution**: Execute queries against any SPARQL endpoint
- 📂 **Named Graph Support**: Query specific graphs or datasets
- 📋 **Multiple Output Formats**: JSON, CSV, Table, Rich terminal, Turtle
- 🔐 **Authentication Support**: Basic and Digest authentication for secured endpoints
- 🏗️ **Extensible Architecture**: Clean separation of concerns, fully tested

## 🚀 Quick Start

### Installation

```bash
# Install directly from source
pip install -e .

# Or install required dependencies
pip install rdflib click
```

### Basic Usage

```bash
# Query with an ontology file
kb-query --ontology data/kb-vocabulary.ttl "meetings with John Smith"

# Show generated SPARQL
kb-query --ontology data/kb-vocabulary.ttl --show-sparql "todos with Sarah"

# Execute query against SPARQL endpoint
kb-query --ontology data/kb-vocabulary.ttl -x -e http://localhost:3030/kb/sparql "meetings with John"

# Query specific named graphs
kb-query -o data/kb-vocabulary.ttl -x -e http://localhost:3030/dataset/sparql \
  -g http://example.org/graph1 -g http://example.org/graph2 "meetings"

# Query with default graph
kb-query -o data/kb-vocabulary.ttl -x -e http://localhost:3030/dataset/sparql \
  --default-graph http://example.org/default "todos"

# Test endpoint connection
kb-query --test-connection -e http://dbpedia.org/sparql

# Different output formats
kb-query -o data/kb-vocabulary.ttl -x -e http://localhost:3030/kb/sparql -f json "meetings"
kb-query -o data/kb-vocabulary.ttl -x -e http://localhost:3030/kb/sparql -f csv "todos"

# Interactive mode
kb-query --ontology data/kb-vocabulary.ttl --interactive

# List available query patterns
kb-query --ontology data/kb-vocabulary.ttl --list-patterns
```

### Example Session

```bash
$ kb-query --ontology data/kb-vocabulary.ttl --interactive --show-sparql
KB Query Interactive Mode
Type 'help' for commands, 'exit' to quit
----------------------------------------
kb-query: meetings with John Smith
✓ Query understood

Generated SPARQL:
----------------------------------------
SELECT ?meeting ?person_name
WHERE {
  ?meeting <http://example.org/kb#hasAttendee> ?person .
  ?person <http://xmlns.com/foaf/0.1/name> ?person_name .
  FILTER (lcase(str(?person_name)) = lcase("John Smith"))
}
----------------------------------------

Execution time: 0.001s
kb-query: exit
Goodbye!
```

### Example with Graph Specification

```bash
$ kb-query -o data/kb-vocabulary.ttl --show-sparql -g http://example.org/mydata "meetings"
✓ Query understood

Generated SPARQL:
----------------------------------------
SELECT ?meeting ?person_name
WHERE {
  GRAPH <http://example.org/mydata> {
    ?meeting <http://example.org/kb#hasAttendee> ?person .
    ?person <http://xmlns.com/foaf/0.1/name> ?person_name .
  }
}
----------------------------------------
```

## 📋 Supported Query Patterns

The system automatically generates patterns from your OWL ontology. For example, with the included sample ontology:

| Query Pattern | Example |
|---------------|---------|
| `meetings with {person}` | "meetings with John Smith" |
| `{person}'s meetings` | "John's meetings" |
| `todos with {person}` | "todos with Sarah" |
| `{person}'s todos` | "Sarah's todos" |
| `notes with {person}` | "notes with John" |
| `meetings tagged {tag}` | "meetings tagged project" |

## 🏗️ Architecture

Built with a clean 4-layer architecture:

- **CLI Layer**: Interactive REPL + Command-line interface
- **Service Layer**: Query orchestration and business logic
- **Core Layer**: Grammar engine, pattern matching, SPARQL building
- **Infrastructure Layer**: OWL parsing, caching, HTTP clients

### Key Components

- **Grammar Engine**: Parses OWL ontologies and generates natural language patterns
- **Pattern Matcher**: Fuzzy matching of user queries to patterns with entity extraction
- **SPARQL Builder**: Template-based SPARQL generation with injection prevention
- **Query Service**: Orchestrates the complete query processing pipeline

## 🧪 Testing

The project follows Test-Driven Development with comprehensive test coverage:

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=kb_query

# Run specific test categories
python -m pytest tests/unit/        # Unit tests
python -m pytest tests/integration/ # Integration tests
python -m pytest tests/e2e/         # End-to-end tests
```

**Test Statistics**:
- **17 unit tests** (100% passing)
- **79% code coverage** (target: 80%+)
- **TDD approach** throughout development

## 📁 Project Structure

```
kb_query/
├── cli/                 # Command-line interface
│   └── main.py         # Main CLI entry point
├── core/               # Core business logic
│   ├── entities.py     # Data structures
│   ├── grammar.py      # OWL parsing & pattern generation
│   ├── matcher.py      # Query pattern matching
│   └── builder.py      # SPARQL query building
├── services/           # Service orchestration
│   └── query.py        # Main query service
└── exceptions.py       # Exception hierarchy

tests/
├── unit/               # Unit tests
├── integration/        # Integration tests
└── e2e/               # End-to-end tests

docs/
├── adr/               # Architecture Decision Records
├── sparc/             # SPARC methodology documentation
├── architecture.md    # System architecture
├── api-reference.md   # API documentation
└── examples.md        # Usage examples
```

## 🔧 Development

### SPARC Methodology

This project was developed using the SPARC methodology:

1. **✅ Specification**: Requirements, user stories, success criteria
2. **✅ Pseudocode**: High-level algorithmic design
3. **✅ Architecture**: System design, interfaces, diagrams
4. **✅ Refinement**: TDD implementation, iterative improvement
5. **✅ Completion**: Integration, testing, documentation

### Running Tests

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests with coverage
python -m pytest --cov=kb_query --cov-report=html

# Run specific component tests
python -m pytest tests/unit/test_grammar_engine.py -v
python -m pytest tests/unit/test_pattern_matcher.py -v
```

### Adding New Ontologies

1. Create your OWL ontology file in Turtle format
2. Ensure proper class and property definitions with domains/ranges
3. Use the CLI to see generated patterns: `kb-query --ontology your-file.ttl --list-patterns`

### Example Ontology Structure

```turtle
@prefix kb: <http://example.org/kb#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

# Classes
kb:Meeting a owl:Class .
kb:Person a owl:Class .

# Properties (generates patterns automatically)
kb:hasAttendee a owl:ObjectProperty ;
    rdfs:domain kb:Meeting ;
    rdfs:range foaf:Person .
```

## 📚 Documentation

- [**Architecture Overview**](docs/architecture.md) - System design and components
- [**API Reference**](docs/api-reference.md) - Detailed API documentation  
- [**Query Examples**](docs/examples.md) - Usage patterns and examples
- [**Architecture Decision Records**](docs/adr/) - Design decisions and rationale
- [**SPARC Documentation**](docs/sparc/) - Development methodology artifacts

## 🤝 Contributing

1. **Follow TDD**: Write tests first, then implement
2. **Update Documentation**: Keep docs current with changes
3. **Use Type Hints**: Full type annotations required
4. **Run Tests**: Ensure all tests pass before submitting

```bash
# Development setup
git clone <repository>
cd knowledgebase-query-system
pip install -e .[dev]

# Make changes, add tests
python -m pytest  # Ensure tests pass
```

## 🏆 Key Achievements

- **Systematic Development**: Complete SPARC methodology application
- **High Test Coverage**: 79% coverage with 17 comprehensive tests
- **Production Ready**: Clean architecture with proper error handling
- **User Friendly**: Natural language interface requires no SPARQL knowledge
- **Extensible**: Easy to add new ontologies and query patterns

## 🔮 Future Enhancements

- [ ] **Configuration Profiles**: Multiple endpoint support with authentication
- [ ] **Result Export**: CSV, JSON output formats
- [ ] **Query History**: Persistent query history and favorites
- [ ] **Advanced Patterns**: Support for aggregation and complex queries
- [ ] **Web Interface**: Browser-based query interface
- [ ] **Performance Optimization**: Caching and query optimization

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built using modern Python best practices:
- **rdflib** for OWL/RDF processing
- **click** for CLI interface
- **pytest** for testing framework
- **SPARC methodology** for systematic development
