# KB Query Interface

A natural language query interface for RDF knowledge bases that automatically generates query patterns from OWL ontologies.

## Features

- 🔍 Natural language to SPARQL translation
- 🧠 Automatic pattern generation from ontology structure
- 📚 Support for standard vocabularies (FOAF, Schema.org, etc.)
- ⚡ No SPARQL knowledge required
- 🎯 Type-safe query generation

## Installation

```bash
pip install -r requirements.txt
python setup.py install
```

## Quick Start

```python
from kb_query import KBQueryEngine

# Initialize with your ontology
engine = KBQueryEngine('path/to/kb-vocabulary.ttl')

# Query using natural language
results = engine.query("meetings with John Smith")
results = engine.query("todos assigned to me")
results = engine.query("daily notes from last week")
```

## Documentation

- [Architecture Overview](docs/architecture.md)
- [API Reference](docs/api-reference.md)
- [Query Examples](docs/examples.md)

## Development

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=kb_query

# Generate patterns from ontology
python -m kb_query.preprocessing.generate_patterns data/kb-vocabulary.ttl
```

## License

MIT
