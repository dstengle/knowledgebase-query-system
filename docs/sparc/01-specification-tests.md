# SPARC Phase 1: Test Specifications

## Test Strategy
High-level test cases that validate each requirement from the specification. These tests will guide TDD implementation in Phase 4 (Refinement).

## Test Categories

### 1. Grammar Generation Tests

#### TG-001: OWL Vocabulary Processing
**Requirement**: Pre-process OWL vocabulary files  
**Test**: Given a valid OWL file, the grammar processor should extract all classes and properties
```python
def test_owl_vocabulary_processing():
    # Given: Sample OWL file with Meeting, Person classes
    # When: Grammar processor parses the file
    # Then: All classes and properties are extracted
    # And: Domain/range relationships are preserved
```

#### TG-002: Pattern Generation from Properties
**Requirement**: Generate query patterns from ontology structure  
**Test**: Property names should generate multiple natural language patterns
```python
def test_pattern_generation():
    # Given: Property kb:hasAttendee with domain Meeting, range Person
    # When: Pattern generator processes the property
    # Then: Patterns include "meetings with {Person}", "meetings attended by {Person}"
```

#### TG-003: Grammar Caching
**Requirement**: Cache grammar for performance  
**Test**: Grammar should be cached and reused on subsequent runs
```python
def test_grammar_caching():
    # Given: Grammar generated from OWL file
    # When: System restarts with same OWL file
    # Then: Cached grammar is loaded (< 100ms)
    # And: No re-processing occurs
```

### 2. Query Processing Tests

#### TQ-001: Natural Language to SPARQL
**Requirement**: Accept queries like "meetings with John Smith"  
**Test**: Natural language queries should produce valid SPARQL
```python
def test_natural_language_conversion():
    # Given: Query "meetings with John Smith"
    # When: Query parser processes input
    # Then: Valid SPARQL is generated
    # And: SPARQL includes correct triple patterns
```

#### TQ-002: Error Messages with Suggestions
**Requirement**: Clear error messages with suggestions  
**Test**: Invalid queries should return helpful feedback
```python
def test_error_suggestions():
    # Given: Invalid query "meeting with with John"
    # When: Parser fails to match pattern
    # Then: Error message explains the issue
    # And: Suggests valid patterns like "meetings with John"
```

#### TQ-003: Debug Mode Output
**Requirement**: Debug mode for troubleshooting  
**Test**: Debug flag should show parsing steps
```python
def test_debug_mode():
    # Given: Debug mode enabled
    # When: Query is processed
    # Then: Shows pattern matching attempts
    # And: Shows SPARQL generation steps
    # And: Shows execution details
```

### 3. CLI Interface Tests

#### TC-001: Interactive Mode REPL
**Requirement**: REPL interface for continuous querying  
**Test**: Interactive mode should maintain session state
```python
def test_interactive_mode():
    # Given: User starts interactive mode
    # When: Multiple queries are entered
    # Then: Each query is processed
    # And: Session history is maintained
    # And: Exit command terminates cleanly
```

#### TC-002: Command Line Mode
**Requirement**: Direct command execution  
**Test**: CLI arguments should execute and return
```python
def test_cli_mode():
    # Given: Command `kb-query "meetings today"`
    # When: Command executes
    # Then: Results are displayed in ASCII table
    # And: Exit code is 0 for success
```

#### TC-003: Optional SPARQL Display
**Requirement**: Optional SPARQL display for learning  
**Test**: Flag should control SPARQL visibility
```python
def test_sparql_display():
    # Given: Query with --show-sparql flag
    # When: Query executes
    # Then: Generated SPARQL is displayed
    # And: Results are displayed
```

### 4. Configuration Tests

#### CF-001: Profile Management
**Requirement**: Configure multiple endpoints (dev/prod)  
**Test**: Profiles should switch endpoints correctly
```python
def test_profile_switching():
    # Given: Profiles for dev and prod
    # When: User selects dev profile
    # Then: Queries go to dev endpoint
    # And: Dev credentials are used
```

#### CF-002: XDG Compliance
**Requirement**: XDG Base Directory compliance  
**Test**: Configuration in standard locations
```python
def test_xdg_directories():
    # Given: XDG_CONFIG_HOME is set
    # When: Config is saved
    # Then: Files are in $XDG_CONFIG_HOME/kb-query/
    # And: Cache is in $XDG_CACHE_HOME/kb-query/
```

#### CF-003: Credential Security
**Requirement**: Credentials stored securely  
**Test**: Sensitive data should be protected
```python
def test_credential_storage():
    # Given: Basic auth credentials
    # When: Credentials are saved
    # Then: File permissions are 600
    # And: Passwords are not in plain text in memory
    # And: Environment variables can override
```

### 5. Core Service Tests

#### CS-001: Service Independence
**Requirement**: Core service testable in isolation  
**Test**: Service module should work without CLI
```python
def test_core_service_independence():
    # Given: Core service module imported
    # When: Service methods are called directly
    # Then: No CLI dependencies required
    # And: Results are returned as data structures
```

#### CS-002: Endpoint Communication
**Requirement**: Execute SPARQL against endpoints  
**Test**: Service should handle endpoint communication
```python
def test_endpoint_communication():
    # Given: Valid SPARQL query
    # When: Executed against endpoint
    # Then: Results are returned
    # And: Timeouts are respected
    # And: Auth headers are included
```

#### CS-003: Result Processing
**Requirement**: ASCII table output for results  
**Test**: Query results formatted correctly
```python
def test_result_formatting():
    # Given: SPARQL query results
    # When: Formatter processes results
    # Then: ASCII table is generated
    # And: Columns are aligned
    # And: Data types are handled
```

### 6. Integration Tests

#### IT-001: End-to-End Query Flow
**Requirement**: Complete query processing pipeline  
**Test**: Full flow from natural language to results
```python
def test_end_to_end_flow():
    # Given: OWL file and natural language query
    # When: Complete pipeline executes
    # Then: Results are displayed correctly
    # And: All components integrate smoothly
```

#### IT-002: Multi-Profile Queries
**Requirement**: Switch between dev/prod endpoints  
**Test**: Same query against different endpoints
```python
def test_multi_profile_execution():
    # Given: Same query, different profiles
    # When: Executed against each profile
    # Then: Each endpoint receives correct query
    # And: Results may differ by endpoint
```

## Test Execution Plan

### Phase 4 (Refinement) - TDD Approach
1. Write failing test from specification
2. Implement minimal code to pass
3. Refactor while keeping tests green
4. Repeat for each requirement

### Test Coverage Goals
- Unit Tests: >80% code coverage
- Integration Tests: All user journeys
- E2E Tests: Critical paths

### Test Environment Requirements
- Mock SPARQL endpoint for testing
- Sample OWL ontologies
- Test data fixtures
- CI/CD pipeline integration

## Traceability Matrix

| Requirement | Test IDs | Priority |
|------------|----------|----------|
| Natural language queries | TQ-001, TQ-002 | High |
| Grammar generation | TG-001, TG-002, TG-003 | High |
| Interactive mode | TC-001 | High |
| CLI mode | TC-002 | High |
| Profile support | CF-001 | High |
| Debug mode | TQ-003 | Medium |
| SPARQL display | TC-003 | Medium |
| XDG compliance | CF-002 | Medium |
| Credential security | CF-003 | High |
| Service independence | CS-001 | High |
| Result formatting | CS-003 | High |
| E2E flow | IT-001 | Critical |