# SPARC Phase 2: Pseudocode

## Overview
High-level algorithmic design for the KB Query CLI system, showing logical flow without implementation details.

## Component 1: Grammar Processor

### 1.1 OWL Vocabulary Parser
```
FUNCTION parse_owl_vocabulary(owl_file_path):
    IF cache_exists(owl_file_path):
        RETURN load_from_cache()
    
    graph = load_rdf_graph(owl_file_path)
    ontology = {
        classes: [],
        properties: [],
        namespaces: {}
    }
    
    FOR each triple in graph:
        IF triple is class_definition:
            ontology.classes.append(extract_class_info(triple))
        ELSE IF triple is property_definition:
            property = {
                name: extract_property_name(triple),
                domain: extract_domain(triple),
                range: extract_range(triple),
                type: object_property OR data_property
            }
            ontology.properties.append(property)
    
    save_to_cache(ontology)
    RETURN ontology
```

### 1.2 Pattern Generator
```
FUNCTION generate_patterns(ontology):
    patterns = []
    
    FOR each property in ontology.properties:
        base_patterns = decompose_property_name(property.name)
        # e.g., "hasAttendee" -> ["has", "attendee"]
        
        FOR each base_pattern in base_patterns:
            IF property.domain AND property.range:
                patterns.append({
                    pattern: create_nl_pattern(property.domain, base_pattern, property.range),
                    sparql_template: create_sparql_template(property),
                    examples: generate_examples(property)
                })
    
    RETURN patterns

FUNCTION create_nl_pattern(domain, verb_phrase, range):
    patterns = []
    # Generate multiple variations
    patterns.append(f"{domain} {verb_phrase} {{range}}")
    patterns.append(f"{{range}}'s {domain}")
    patterns.append(f"{domain} with {range} {{value}}")
    RETURN patterns
```

### 1.3 Grammar Cache Manager
```
FUNCTION cache_grammar(grammar, ontology_hash):
    cache_dir = get_xdg_cache_dir() + "/kb-query/grammar/"
    cache_file = cache_dir + ontology_hash + ".json"
    
    IF NOT exists(cache_dir):
        create_directory(cache_dir)
    
    save_json(cache_file, {
        'hash': ontology_hash,
        'timestamp': current_time(),
        'grammar': grammar
    })

FUNCTION load_cached_grammar(ontology_path):
    ontology_hash = calculate_hash(ontology_path)
    cache_file = get_cache_path(ontology_hash)
    
    IF exists(cache_file):
        cached = load_json(cache_file)
        IF cached.hash == ontology_hash:
            RETURN cached.grammar
    
    RETURN None
```

## Component 2: Query Parser

### 2.1 Natural Language Parser
```
FUNCTION parse_query(user_input, grammar):
    user_input = normalize_text(user_input)
    matches = []
    
    FOR each pattern in grammar:
        match_score = calculate_match_score(user_input, pattern)
        IF match_score > THRESHOLD:
            extracted_values = extract_entities(user_input, pattern)
            matches.append({
                pattern: pattern,
                score: match_score,
                values: extracted_values
            })
    
    IF len(matches) == 0:
        suggestions = find_similar_patterns(user_input, grammar)
        RAISE QueryParseError("No matching pattern", suggestions)
    
    best_match = select_best_match(matches)
    RETURN build_query_structure(best_match)

FUNCTION extract_entities(input_text, pattern):
    entities = {}
    tokens = tokenize(input_text)
    pattern_tokens = tokenize(pattern.pattern)
    
    FOR i, token in pattern_tokens:
        IF token.is_placeholder:
            entities[token.name] = tokens[i]
    
    RETURN entities
```

### 2.2 SPARQL Builder
```
FUNCTION build_sparql(parsed_query, namespaces):
    sparql = "PREFIX " + format_namespaces(namespaces) + "\n"
    sparql += "SELECT "
    
    IF parsed_query.select_vars:
        sparql += join(parsed_query.select_vars)
    ELSE:
        sparql += "*"
    
    sparql += "\nWHERE {\n"
    
    FOR each triple_pattern in parsed_query.patterns:
        sparql += format_triple(triple_pattern) + "\n"
    
    IF parsed_query.filters:
        FOR each filter in parsed_query.filters:
            sparql += "FILTER(" + format_filter(filter) + ")\n"
    
    sparql += "}"
    
    IF parsed_query.limit:
        sparql += f"\nLIMIT {parsed_query.limit}"
    
    RETURN sparql
```

## Component 3: Core Service

### 3.1 SPARQL Executor
```
CLASS SPARQLService:
    FUNCTION __init__(config):
        self.endpoints = load_endpoints(config)
        self.current_profile = config.default_profile
        self.timeout = config.timeout
    
    FUNCTION execute_query(sparql_query, profile=None):
        endpoint = self.get_endpoint(profile OR self.current_profile)
        
        headers = {
            'Accept': 'application/sparql-results+json',
            'Content-Type': 'application/sparql-query'
        }
        
        IF endpoint.auth_required:
            headers['Authorization'] = get_auth_header(endpoint)
        
        TRY:
            response = http_post(
                endpoint.url,
                data=sparql_query,
                headers=headers,
                timeout=self.timeout
            )
            
            IF response.status == 200:
                RETURN parse_sparql_results(response.json())
            ELSE:
                RAISE SPARQLError(response.status, response.text)
        
        CATCH timeout_error:
            RAISE QueryTimeoutError(self.timeout)
        CATCH connection_error:
            RAISE EndpointConnectionError(endpoint.url)
```

### 3.2 Result Formatter
```
FUNCTION format_results(sparql_results, format_type='table'):
    IF format_type == 'table':
        RETURN format_as_table(sparql_results)
    ELSE IF format_type == 'json':
        RETURN format_as_json(sparql_results)
    ELSE IF format_type == 'csv':
        RETURN format_as_csv(sparql_results)

FUNCTION format_as_table(results):
    IF results.is_empty:
        RETURN "No results found"
    
    headers = results.variables
    rows = []
    
    FOR each binding in results.bindings:
        row = []
        FOR each var in headers:
            value = binding.get(var, '')
            row.append(format_value(value))
        rows.append(row)
    
    RETURN create_ascii_table(headers, rows)

FUNCTION create_ascii_table(headers, rows):
    column_widths = calculate_column_widths(headers, rows)
    
    table = draw_horizontal_line(column_widths)
    table += format_row(headers, column_widths)
    table += draw_horizontal_line(column_widths)
    
    FOR each row in rows:
        table += format_row(row, column_widths)
    
    table += draw_horizontal_line(column_widths)
    RETURN table
```

## Component 4: CLI Interface

### 4.1 Command Line Interface
```
FUNCTION main():
    args = parse_arguments()
    
    IF args.init:
        initialize_configuration()
        RETURN
    
    config = load_configuration()
    service = SPARQLService(config)
    
    IF args.interactive:
        run_interactive_mode(service)
    ELSE IF args.query:
        run_query_mode(service, args.query, args)
    ELSE:
        show_help()

FUNCTION parse_arguments():
    parser = ArgumentParser("kb-query")
    parser.add("query", help="Natural language query")
    parser.add("--profile", "-p", help="Endpoint profile")
    parser.add("--show-sparql", "-s", help="Display generated SPARQL")
    parser.add("--debug", "-d", help="Enable debug mode")
    parser.add("--interactive", "-i", help="Interactive mode")
    parser.add("--init", help="Initialize configuration")
    RETURN parser.parse()
```

### 4.2 Interactive Mode
```
FUNCTION run_interactive_mode(service):
    grammar = load_grammar()
    session = {
        history: [],
        debug: False,
        show_sparql: False
    }
    
    print("KB Query CLI - Interactive Mode")
    print("Type 'help' for commands, 'exit' to quit")
    
    WHILE True:
        user_input = prompt("kb-query> ")
        
        IF user_input == "exit":
            BREAK
        ELSE IF user_input == "help":
            show_interactive_help()
        ELSE IF user_input.startswith("."):
            handle_command(user_input, session)
        ELSE:
            TRY:
                result = process_query(user_input, service, grammar, session)
                display_result(result, session)
                session.history.append(user_input)
            CATCH error:
                display_error(error, session)

FUNCTION process_query(input_text, service, grammar, session):
    IF session.debug:
        print(f"Parsing: {input_text}")
    
    parsed = parse_query(input_text, grammar)
    
    IF session.debug:
        print(f"Matched pattern: {parsed.pattern}")
        print(f"Extracted entities: {parsed.entities}")
    
    sparql = build_sparql(parsed)
    
    IF session.show_sparql OR session.debug:
        print(f"SPARQL:\n{sparql}")
    
    results = service.execute_query(sparql)
    RETURN results
```

### 4.3 Configuration Manager
```
FUNCTION load_configuration():
    config_dir = get_xdg_config_dir() + "/kb-query/"
    config_file = config_dir + "config.yaml"
    
    IF NOT exists(config_file):
        RAISE ConfigurationError("Not initialized. Run 'kb-query --init'")
    
    config = load_yaml(config_file)
    
    # Load profiles
    profiles_dir = config_dir + "profiles/"
    FOR each profile_file in list_files(profiles_dir, "*.yaml"):
        profile = load_yaml(profile_file)
        config.profiles[profile.name] = profile
    
    # Substitute environment variables
    config = substitute_env_vars(config)
    
    RETURN config

FUNCTION initialize_configuration():
    config_dir = get_xdg_config_dir() + "/kb-query/"
    
    IF exists(config_dir):
        IF NOT confirm("Configuration exists. Overwrite?"):
            RETURN
    
    create_directory(config_dir)
    create_directory(config_dir + "profiles/")
    
    # Create default config
    default_config = {
        'default_profile': 'dev',
        'debug': False,
        'timeout': 30
    }
    save_yaml(config_dir + "config.yaml", default_config)
    
    # Create example profiles
    dev_profile = {
        'name': 'dev',
        'endpoint': prompt("Dev endpoint URL: "),
        'auth': {
            'type': 'basic',
            'username': prompt("Dev username: "),
            'password': prompt_password("Dev password: ")
        }
    }
    save_yaml(config_dir + "profiles/dev.yaml", dev_profile)
    
    print(f"Configuration created in {config_dir}")
```

## Component 5: Error Handling & Debug

### 5.1 Error Handler
```
FUNCTION handle_error(error, debug_mode):
    IF isinstance(error, QueryParseError):
        print(f"Could not understand query: {error.query}")
        IF error.suggestions:
            print("Did you mean:")
            FOR suggestion in error.suggestions[:3]:
                print(f"  - {suggestion}")
    
    ELSE IF isinstance(error, SPARQLError):
        print(f"SPARQL execution failed: {error.message}")
        IF debug_mode:
            print(f"Status: {error.status}")
            print(f"Response: {error.response}")
    
    ELSE IF isinstance(error, EndpointConnectionError):
        print(f"Could not connect to endpoint: {error.endpoint}")
        print("Check your network and endpoint configuration")
    
    ELSE:
        print(f"Unexpected error: {error}")
        IF debug_mode:
            print(format_traceback(error))
```

### 5.2 Query Suggestions
```
FUNCTION find_similar_patterns(user_input, grammar):
    suggestions = []
    input_tokens = tokenize(user_input.lower())
    
    FOR each pattern in grammar:
        pattern_tokens = tokenize(pattern.pattern.lower())
        similarity = calculate_similarity(input_tokens, pattern_tokens)
        
        IF similarity > 0.5:
            suggestions.append({
                'pattern': pattern.pattern,
                'score': similarity,
                'example': pattern.examples[0]
            })
    
    suggestions.sort(by='score', descending=True)
    RETURN [s.example for s in suggestions[:5]]

FUNCTION calculate_similarity(tokens1, tokens2):
    # Use Levenshtein distance or cosine similarity
    common_tokens = intersection(tokens1, tokens2)
    total_tokens = union(tokens1, tokens2)
    RETURN len(common_tokens) / len(total_tokens)
```

## Data Flow Summary

```
1. INITIALIZATION:
   Load Config → Load Grammar → Initialize Service

2. QUERY FLOW:
   User Input → Parse Query → Match Pattern → 
   Build SPARQL → Execute Query → Format Results → Display

3. ERROR FLOW:
   Error Detected → Classify Error → Generate Suggestions → 
   Display Helpful Message → Log if Debug Mode

4. CACHE FLOW:
   Check Cache → Load if Valid → Generate if Missing → 
   Save to Cache → Use Grammar
```

## State Management

```
APPLICATION STATE:
- Current profile
- Grammar cache
- Debug mode
- Session history (interactive)

SESSION STATE (Interactive Mode):
- Query history
- Debug flag
- Show SPARQL flag
- Current profile override

CACHE STATE:
- Grammar cache by ontology hash
- Timestamp for invalidation
- Profile credentials (encrypted)
```