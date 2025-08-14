# SPARC Phase 2: Core Algorithms

## Algorithm Complexity Analysis

### Pattern Matching Algorithm
**Time Complexity**: O(n*m) where n = number of patterns, m = average pattern length  
**Space Complexity**: O(k) where k = number of potential matches

```
ALGORITHM: fuzzy_pattern_matching(user_input, patterns)
    INPUT: user_input (string), patterns (list of Pattern objects)
    OUTPUT: list of MatchResult objects

    normalized_input = normalize(user_input)
    matches = []
    
    FOR each pattern in patterns:
        normalized_pattern = normalize(pattern.text)
        
        # Exact match check (fastest path)
        IF normalized_input == normalized_pattern:
            matches.append(MatchResult(pattern, 1.0, "exact"))
            CONTINUE
        
        # Token-based matching
        input_tokens = tokenize(normalized_input)
        pattern_tokens = tokenize(normalized_pattern, preserve_placeholders=True)
        
        # Early exit for length mismatch
        IF abs(len(input_tokens) - len(pattern_tokens)) > 2:
            CONTINUE
        
        match_score = calculate_token_alignment(input_tokens, pattern_tokens)
        
        IF match_score >= MATCH_THRESHOLD:
            entities = extract_entities(input_tokens, pattern_tokens)
            matches.append(MatchResult(pattern, match_score, "fuzzy", entities))
    
    RETURN sort_by_score(matches, descending=True)
```

### Entity Extraction Algorithm
```
ALGORITHM: extract_entities(input_tokens, pattern_tokens)
    INPUT: input_tokens (list), pattern_tokens (list with placeholders)
    OUTPUT: dictionary of {placeholder: value}
    
    entities = {}
    i = 0  # input pointer
    j = 0  # pattern pointer
    
    WHILE i < len(input_tokens) AND j < len(pattern_tokens):
        pattern_token = pattern_tokens[j]
        
        IF pattern_token.is_placeholder:
            # Multi-token entity extraction
            entity_start = i
            entity_end = find_entity_boundary(input_tokens, pattern_tokens, i, j)
            
            entity_value = join_tokens(input_tokens[entity_start:entity_end])
            entities[pattern_token.name] = entity_value
            
            i = entity_end
            j += 1
        
        ELSE IF pattern_token.matches(input_tokens[i]):
            i += 1
            j += 1
        
        ELSE:
            # Backtrack or skip
            i += 1
    
    RETURN entities
```

## Query Optimization Strategies

### 1. Grammar Pre-filtering
```
ALGORITHM: prefilter_patterns(user_input, patterns)
    # Reduce search space before expensive matching
    
    input_keywords = extract_keywords(user_input)
    candidate_patterns = []
    
    FOR each pattern in patterns:
        pattern_keywords = pattern.keywords
        keyword_overlap = intersection(input_keywords, pattern_keywords)
        
        IF len(keyword_overlap) >= MIN_KEYWORD_OVERLAP:
            candidate_patterns.append(pattern)
    
    RETURN candidate_patterns
```

### 2. SPARQL Query Optimization
```
ALGORITHM: optimize_sparql(sparql_query)
    # Apply query optimization techniques
    
    parsed = parse_sparql(sparql_query)
    
    # 1. Predicate ordering (most selective first)
    optimized_patterns = sort_patterns_by_selectivity(parsed.patterns)
    
    # 2. Filter pushdown (apply filters early)
    optimized_filters = push_filters_down(parsed.filters, optimized_patterns)
    
    # 3. Join optimization
    optimized_joins = optimize_join_order(optimized_patterns)
    
    RETURN build_sparql(optimized_joins, optimized_filters)
```

## Memory Management

### Cache Eviction Strategy
```
ALGORITHM: cache_eviction_lru()
    # Least Recently Used eviction when cache size limit reached
    
    IF cache.size > MAX_CACHE_SIZE:
        items_to_remove = cache.size - TARGET_CACHE_SIZE
        lru_items = cache.get_lru_items(items_to_remove)
        
        FOR each item in lru_items:
            remove_from_cache(item.key)
            free_memory(item.data)
```

### Grammar Loading Strategy
```
ALGORITHM: lazy_grammar_loading(ontology_path)
    # Load grammar incrementally to reduce startup time
    
    ontology_hash = hash_file(ontology_path)
    
    IF cached_grammar_exists(ontology_hash):
        # Load minimal grammar first
        essential_patterns = load_essential_patterns(ontology_hash)
        
        # Background loading of remaining patterns
        spawn_background_task(load_remaining_patterns, ontology_hash)
        
        RETURN essential_patterns
    
    ELSE:
        # Generate grammar incrementally
        RETURN generate_grammar_incremental(ontology_path)
```

## Error Recovery Algorithms

### Query Suggestion Generation
```
ALGORITHM: generate_suggestions(failed_query, patterns)
    INPUT: failed_query (string), patterns (list)
    OUTPUT: list of suggested queries
    
    suggestions = []
    query_tokens = tokenize(failed_query)
    
    # 1. Typo correction
    corrected_tokens = []
    FOR each token in query_tokens:
        best_correction = find_closest_word(token, vocabulary)
        corrected_tokens.append(best_correction)
    
    corrected_query = join(corrected_tokens)
    suggestions.append(corrected_query)
    
    # 2. Pattern-based suggestions
    FOR each pattern in patterns:
        similarity = calculate_similarity(query_tokens, tokenize(pattern.example))
        IF similarity > SUGGESTION_THRESHOLD:
            suggestions.append(pattern.example)
    
    # 3. Partial match expansion
    partial_matches = find_partial_matches(query_tokens, patterns)
    FOR each match in partial_matches:
        completed_query = complete_partial_match(failed_query, match)
        suggestions.append(completed_query)
    
    RETURN deduplicate_and_rank(suggestions)
```

### Graceful Degradation
```
ALGORITHM: graceful_degradation(query, error_type)
    # Provide increasingly simplified alternatives when query fails
    
    SWITCH error_type:
        CASE PATTERN_NOT_FOUND:
            # Try broader patterns
            simplified_query = simplify_query(query)
            RETURN retry_with_simplified_query(simplified_query)
        
        CASE ENTITY_NOT_RECOGNIZED:
            # Suggest entity disambiguation
            entities = extract_potential_entities(query)
            candidates = find_entity_candidates(entities)
            RETURN suggest_entity_disambiguation(candidates)
        
        CASE SPARQL_SYNTAX_ERROR:
            # Fall back to basic query structure
            basic_query = generate_basic_query(query)
            RETURN execute_basic_query(basic_query)
```

## Concurrent Processing

### Multi-threaded Pattern Matching
```
ALGORITHM: parallel_pattern_matching(user_input, patterns)
    # Divide pattern set among worker threads
    
    num_workers = min(CPU_CORES, ceil(len(patterns) / MIN_PATTERNS_PER_WORKER))
    pattern_chunks = divide_patterns(patterns, num_workers)
    
    futures = []
    FOR each chunk in pattern_chunks:
        future = submit_to_thread_pool(match_patterns, user_input, chunk)
        futures.append(future)
    
    all_matches = []
    FOR each future in futures:
        chunk_matches = future.get_result()
        all_matches.extend(chunk_matches)
    
    RETURN merge_and_sort_matches(all_matches)
```

### Async SPARQL Execution
```
ALGORITHM: async_query_execution(sparql_query, endpoints)
    # Execute query against multiple endpoints concurrently
    
    futures = []
    FOR each endpoint in endpoints:
        future = submit_async(execute_sparql, sparql_query, endpoint)
        futures.append((future, endpoint))
    
    results = {}
    FOR future, endpoint in futures:
        TRY:
            result = await future
            results[endpoint.name] = result
        EXCEPT timeout:
            results[endpoint.name] = TimeoutError()
        EXCEPT error:
            results[endpoint.name] = error
    
    # Return first successful result, or aggregate errors
    RETURN process_concurrent_results(results)
```

## Performance Benchmarks (Target)

| Operation | Target Time | Complexity |
|-----------|-------------|------------|
| Grammar Loading | < 500ms | O(n) where n = ontology size |
| Pattern Matching | < 50ms | O(p) where p = pattern count |
| SPARQL Generation | < 10ms | O(1) for simple queries |
| Result Formatting | < 100ms | O(r) where r = result count |
| Cache Operations | < 5ms | O(1) for hash operations |

## Memory Usage Targets

| Component | Max Memory | Notes |
|-----------|------------|--------|
| Grammar Cache | 50MB | LRU eviction at 75MB |
| Query History | 10MB | Rolling buffer of 1000 queries |
| Result Cache | 25MB | Optional result caching |
| Working Memory | 100MB | Peak during processing |

## Algorithm Selection Rationale

1. **Pattern Matching**: Token-based approach balances accuracy with performance
2. **Entity Extraction**: Greedy algorithm with backtracking for complex cases
3. **Cache Strategy**: LRU for temporal locality in user queries
4. **Suggestion Generation**: Multi-strategy approach for comprehensive coverage
5. **Concurrent Processing**: Thread pool for I/O bound operations, avoid for CPU-bound