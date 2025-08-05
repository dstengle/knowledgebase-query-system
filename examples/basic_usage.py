#!/usr/bin/env python3
"""Basic usage examples for KB Query Interface"""

from kb_query import KBQueryEngine

def main():
    # Initialize with your ontology
    engine = KBQueryEngine('data/kb-vocabulary.ttl')
    
    print("KB Query Interface - Examples\n")
    
    # Example 1: Simple queries
    print("1. Simple Queries:")
    queries = [
        "meetings with John Smith",
        "todos assigned to me",
        "daily notes from last week",
        "books by Douglas Adams",
        "stale relationships"
    ]
    
    for q in queries:
        print(f"\nQuery: {q}")
        try:
            result = engine.query(q)
            print(f"SPARQL: {result['sparql'][:100]}...")
        except Exception as e:
            print(f"Error: {e}")
    
    # Example 2: Get patterns for a class
    print("\n\n2. Available patterns for 'Meeting':")
    patterns = engine.get_patterns_for_class("Meeting")
    for p in patterns[:5]:
        print(f"  - {p}")
    
    # Example 3: Query suggestions
    print("\n\n3. Query suggestions for 'meet':")
    suggestions = engine.suggest_queries("meet")
    for s in suggestions:
        print(f"  - {s}")

if __name__ == "__main__":
    main()
