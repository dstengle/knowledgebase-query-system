# Graph Query Support

The KB Query CLI supports querying specific named graphs in SPARQL endpoints that host multiple RDF datasets.

## Overview

Many SPARQL endpoints organize data into multiple named graphs, allowing for better data organization and access control. The KB Query CLI provides options to specify which graphs to query.

## Command-Line Options

### Named Graphs (`--graph` / `-g`)

Specify one or more named graphs to query using the `FROM NAMED` clause:

```bash
# Query a single named graph
kb-query -o ontology.ttl -x -e http://localhost:3030/dataset/sparql \
  -g http://example.org/graph1 "meetings"

# Query multiple named graphs
kb-query -o ontology.ttl -x -e http://localhost:3030/dataset/sparql \
  -g http://example.org/graph1 -g http://example.org/graph2 "todos"
```

### Default Graph (`--default-graph`)

Specify the default graph using the `FROM` clause:

```bash
kb-query -o ontology.ttl -x -e http://localhost:3030/dataset/sparql \
  --default-graph http://example.org/default "notes"
```

### Combining Default and Named Graphs

You can combine both default and named graphs in a single query:

```bash
kb-query -o ontology.ttl -x -e http://localhost:3030/dataset/sparql \
  --default-graph http://example.org/default \
  -g http://example.org/graph1 \
  -g http://example.org/graph2 \
  "meetings with John"
```

## Generated SPARQL

When graph options are specified, the CLI uses `GRAPH` blocks inside the WHERE clause, which is compatible with Apache Fuseki and other triple stores:

### Single Graph

For a single graph, the query patterns are wrapped in a GRAPH block:

```sparql
SELECT ?meeting ?person_name
WHERE {
  GRAPH <http://example.org/graph1> {
    ?meeting <http://example.org/kb#hasAttendee> ?person .
    ?person <http://xmlns.com/foaf/0.1/name> ?person_name .
    FILTER (lcase(str(?person_name)) = lcase("John"))
  }
}
```

### Multiple Graphs

For multiple graphs, the CLI uses UNION to query across all specified graphs:

```sparql
SELECT ?meeting ?person_name
WHERE {
  {
    GRAPH <http://example.org/graph1> {
      ?meeting <http://example.org/kb#hasAttendee> ?person .
      ?person <http://xmlns.com/foaf/0.1/name> ?person_name .
      FILTER (lcase(str(?person_name)) = lcase("John"))
    }
  }
  UNION
  {
    GRAPH <http://example.org/graph2> {
      ?meeting <http://example.org/kb#hasAttendee> ?person .
      ?person <http://xmlns.com/foaf/0.1/name> ?person_name .
      FILTER (lcase(str(?person_name)) = lcase("John"))
    }
  }
}
```

## Common Use Cases

### 1. Querying Versioned Data

Different versions of data stored in separate graphs:

```bash
# Query the latest version
kb-query -x -e http://localhost:3030/sparql \
  -g http://example.org/data/v2.0 "all meetings"

# Query a specific historical version
kb-query -x -e http://localhost:3030/sparql \
  -g http://example.org/data/v1.0 "all meetings"
```

### 2. Querying Department-Specific Data

Data organized by organizational units:

```bash
# Query engineering department data
kb-query -x -e http://localhost:3030/sparql \
  -g http://example.org/dept/engineering "team meetings"

# Query multiple departments
kb-query -x -e http://localhost:3030/sparql \
  -g http://example.org/dept/engineering \
  -g http://example.org/dept/product \
  "cross-team meetings"
```

### 3. Querying Time-Based Graphs

Data organized by time periods:

```bash
# Query Q1 2024 data
kb-query -x -e http://localhost:3030/sparql \
  -g http://example.org/2024/Q1 "quarterly meetings"

# Query entire year
kb-query -x -e http://localhost:3030/sparql \
  -g http://example.org/2024/Q1 \
  -g http://example.org/2024/Q2 \
  -g http://example.org/2024/Q3 \
  -g http://example.org/2024/Q4 \
  "annual review meetings"
```

## Configuration File Support

You can also specify graphs in the configuration file:

```yaml
kb_query:
  sparql:
    endpoint: "http://localhost:3030/dataset/sparql"
    default_graph: "http://example.org/default"
    named_graphs:
      - "http://example.org/graph1"
      - "http://example.org/graph2"
```

Then use the configuration:

```bash
kb-query -c config.yaml -x "meetings"
```

## Endpoint Examples

### Apache Jena Fuseki

Fuseki supports dataset endpoints with multiple graphs:

```bash
# Query specific graph in dataset
kb-query -x -e http://localhost:3030/myDataset/sparql \
  -g http://example.org/myGraph "all data"
```

### Virtuoso

Virtuoso organizes data in named graphs:

```bash
# Query DBpedia's named graph
kb-query -x -e http://dbpedia.org/sparql \
  -g http://dbpedia.org "cities in France"
```

### GraphDB

GraphDB supports repository-based graph organization:

```bash
# Query specific repository graph
kb-query -x -e http://localhost:7200/repositories/myRepo \
  -g http://example.org/ontology \
  -g http://example.org/instances \
  "all classes"
```

## Best Practices

1. **Know Your Endpoint Structure**: Different endpoints organize graphs differently. Check your endpoint's documentation.

2. **Use Default Graph for Common Data**: Put frequently accessed data in the default graph for simpler queries.

3. **Use Named Graphs for Isolation**: Keep different datasets, versions, or access levels in separate named graphs.

4. **Combine Graphs Carefully**: When querying multiple graphs, be aware of potential data conflicts or duplicates.

5. **Test Graph Availability**: Use the test connection feature to verify graph accessibility:
   ```bash
   kb-query --test-connection -e http://localhost:3030/dataset/sparql
   ```

## Troubleshooting

### No Results Returned

If your query returns no results when using graphs:
- Verify the graph URIs are correct
- Check if the graphs contain the expected data
- Try querying without graph restrictions first

### Permission Errors

Some endpoints restrict access to certain graphs:
- Verify you have permission to access the specified graphs
- Check if authentication is required
- Contact the endpoint administrator if needed

### Performance Issues

Querying multiple large graphs can be slow:
- Limit the number of graphs when possible
- Use more specific queries to reduce the search space
- Consider using LIMIT clause for initial testing