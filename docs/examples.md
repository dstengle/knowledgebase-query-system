# KB Query Examples

## Basic Usage

```python
from kb_query import KBQueryEngine

# Initialize
engine = KBQueryEngine('path/to/ontology.ttl')

# Simple query
result = engine.query("meetings with John Smith")
print(result['sparql'])
```

## Query Patterns

### Meeting Queries

```python
# By attendee
engine.query("meetings with John Smith")
engine.query("meetings attended by Sarah Chen")

# By time
engine.query("meetings from last week")
engine.query("meetings today")

# By tag
engine.query("meetings tagged projects/web")
```

### Todo Queries

```python
# By assignee
engine.query("todos assigned to me")
engine.query("John's todos")

# By status
engine.query("incomplete todos")
engine.query("overdue todos")

# By date
engine.query("todos due tomorrow")
```

### Complex Queries

```python
# Multiple filters
engine.query("meetings with John from last week")
engine.query("incomplete todos assigned to Sarah")

# With limits
engine.query("top 5 recent meetings")
engine.query("latest 10 daily notes")
```

## Configuration

```yaml
kb_query:
  ontology:
    namespaces:
      kb: "http://example.org/kb/vocab#"
      
  patterns:
    cache_enabled: true
    enrichment:
      use_wordnet: true
      
  sparql:
    endpoint: "http://localhost:3030/kb/sparql"
    timeout: 30
```

## Error Handling

```python
try:
    result = engine.query("invalid query syntax")
except QueryParseError as e:
    print(f"Could not parse: {e}")
    print(f"Did you mean: {e.suggestions}")
```
