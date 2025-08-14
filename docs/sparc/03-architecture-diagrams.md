# SPARC Phase 3: Architecture Diagrams

## System Context Diagram

```mermaid
graph TB
    User[User] --> CLI[KB Query CLI]
    CLI --> DevEndpoint[Dev SPARQL Endpoint<br/>fuseki:3030/test]
    CLI --> ProdEndpoint[Prod SPARQL Endpoint<br/>localhost:13030/kb]
    CLI --> Config[XDG Config Files<br/>~/.config/kb-query/]
    CLI --> Cache[XDG Cache<br/>~/.cache/kb-query/]
    CLI --> Ontology[OWL Vocabulary File<br/>data/kb-vocabulary.ttl]
    
    subgraph "External Systems"
        DevEndpoint
        ProdEndpoint
    end
    
    subgraph "File System"
        Config
        Cache
        Ontology
    end
```

## Component Interaction Diagram

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant QueryService
    participant GrammarEngine
    participant PatternMatcher
    participant SPARQLBuilder
    participant SPARQLClient
    participant Endpoint
    
    User->>CLI: "meetings with John Smith"
    CLI->>QueryService: process_query(input, profile)
    QueryService->>GrammarEngine: load_grammar()
    GrammarEngine-->>QueryService: Grammar patterns
    QueryService->>PatternMatcher: find_matches(input, grammar)
    PatternMatcher-->>QueryService: MatchResult
    QueryService->>SPARQLBuilder: build_query(match)
    SPARQLBuilder-->>QueryService: SPARQL query
    QueryService->>SPARQLClient: execute(sparql, endpoint)
    SPARQLClient->>Endpoint: POST /sparql
    Endpoint-->>SPARQLClient: Results JSON
    SPARQLClient-->>QueryService: QueryResult
    QueryService-->>CLI: QueryResponse
    CLI-->>User: Formatted table
```

## Layer Architecture Diagram

```mermaid
graph TD
    subgraph "CLI Interface Layer"
        IC[Interactive CLI<br/>REPL Loop]
        CC[Command CLI<br/>Single Query]
    end
    
    subgraph "Application Service Layer"
        QS[Query Service<br/>Orchestration]
        CM[Config Manager<br/>Profiles & Settings]
        RF[Result Formatter<br/>ASCII Table]
    end
    
    subgraph "Core Business Layer"
        GE[Grammar Engine<br/>OWL Processing]
        PM[Pattern Matcher<br/>NL Matching]
        SB[SPARQL Builder<br/>Query Generation]
    end
    
    subgraph "Infrastructure Layer"
        SC[SPARQL Client<br/>HTTP Requests]
        CAC[Cache Manager<br/>LRU Cache]
        FS[File System<br/>XDG Directories]
    end
    
    IC --> QS
    CC --> QS
    QS --> GE
    QS --> PM
    QS --> SB
    QS --> RF
    QS --> CM
    GE --> CAC
    PM --> CAC
    SB --> SC
    SC --> FS
    CM --> FS
```

## Data Flow Diagram

```mermaid
flowchart TD
    Start([User Input]) --> Validate{Valid Input?}
    Validate -->|No| Error[Display Error + Suggestions]
    Validate -->|Yes| LoadGrammar[Load Grammar from Cache]
    LoadGrammar --> CheckCache{Grammar Cached?}
    CheckCache -->|No| ParseOWL[Parse OWL Ontology]
    ParseOWL --> GeneratePatterns[Generate Patterns]
    GeneratePatterns --> CacheGrammar[Cache Grammar]
    CacheGrammar --> Match[Match Patterns]
    CheckCache -->|Yes| Match
    Match --> Found{Pattern Found?}
    Found -->|No| Suggest[Generate Suggestions]
    Suggest --> Error
    Found -->|Yes| Extract[Extract Entities]
    Extract --> BuildSPARQL[Build SPARQL Query]
    BuildSPARQL --> Execute[Execute Against Endpoint]
    Execute --> Success{Query Success?}
    Success -->|No| HandleError[Handle SPARQL Error]
    HandleError --> Error
    Success -->|Yes| Format[Format Results]
    Format --> Display[Display to User]
    Display --> End([End])
    Error --> End
```

## Component Dependency Graph

```mermaid
graph LR
    CLI[CLI Components] --> Services[Service Layer]
    Services --> Core[Core Business Logic]
    Core --> Infrastructure[Infrastructure Layer]
    
    subgraph CLI
        direction TB
        InteractiveCLI
        CommandCLI
        ArgumentParser
    end
    
    subgraph Services
        direction TB
        QueryService
        ConfigManager
        SuggestionService
    end
    
    subgraph Core
        direction TB
        GrammarEngine
        PatternMatcher
        SPARQLBuilder
        EntityExtractor
    end
    
    subgraph Infrastructure
        direction TB
        SPARQLClient
        CacheManager
        FileSystemManager
        CredentialManager
    end
```

## State Transition Diagram (Interactive Mode)

```mermaid
stateDiagram-v2
    [*] --> Initializing
    Initializing --> LoadingConfig: Config found
    Initializing --> Setup: No config
    Setup --> LoadingConfig: Config created
    LoadingConfig --> LoadingGrammar: Config loaded
    LoadingGrammar --> Ready: Grammar loaded
    LoadingGrammar --> Error: Grammar failed
    Ready --> Processing: User input
    Processing --> Displaying: Query success
    Processing --> ErrorState: Query failed
    Displaying --> Ready: Results shown
    ErrorState --> Ready: Error handled
    Ready --> [*]: Exit command
    Error --> [*]: Fatal error
```

## Error Handling Flow

```mermaid
flowchart TD
    Exception([Exception Thrown]) --> Classify{Classify Error Type}
    Classify -->|Config Error| ConfigHandler[Configuration Error Handler]
    Classify -->|Parse Error| ParseHandler[Query Parse Error Handler]
    Classify -->|SPARQL Error| SPARQLHandler[SPARQL Error Handler]
    Classify -->|Network Error| NetworkHandler[Network Error Handler]
    Classify -->|Unknown Error| GenericHandler[Generic Error Handler]
    
    ConfigHandler --> ConfigSuggestions[Suggest Config Fix]
    ParseHandler --> QuerySuggestions[Generate Query Suggestions]
    SPARQLHandler --> SPARQLDebug[Show SPARQL Debug Info]
    NetworkHandler --> NetworkTroubleshoot[Network Troubleshooting]
    GenericHandler --> GenericMessage[Generic Error Message]
    
    ConfigSuggestions --> Display[Display Error Message]
    QuerySuggestions --> Display
    SPARQLDebug --> Display
    NetworkTroubleshoot --> Display
    GenericMessage --> Display
    
    Display --> LogError{Debug Mode?}
    LogError -->|Yes| WriteLog[Write to Debug Log]
    LogError -->|No| End([Return to CLI])
    WriteLog --> End
```

## Cache Architecture

```mermaid
graph TB
    subgraph "Cache Manager"
        LRU[LRU Eviction Policy]
        HashIndex[Hash-based Index]
        SizeTracker[Size Tracking]
    end
    
    subgraph "Cache Types"
        GrammarCache[Grammar Cache<br/>50MB limit<br/>Persistent]
        PatternCache[Pattern Cache<br/>In-memory<br/>Session-based]
        ResultCache[Result Cache<br/>Optional<br/>TTL-based]
    end
    
    subgraph "Storage"
        DiskStorage[Disk Storage<br/>~/.cache/kb-query/]
        MemoryStorage[Memory Storage<br/>Process heap]
    end
    
    GrammarCache --> DiskStorage
    PatternCache --> MemoryStorage
    ResultCache --> MemoryStorage
    
    LRU --> GrammarCache
    HashIndex --> GrammarCache
    SizeTracker --> GrammarCache
```

## Security Architecture

```mermaid
graph TB
    subgraph "Credential Flow"
        EnvVars[Environment Variables] --> CredManager[Credential Manager]
        ConfigFile[Config Files] --> VarSubstitution[Variable Substitution]
        VarSubstitution --> CredManager
        CredManager --> Encryption[Encryption at Rest]
        Encryption --> SystemKeyring[System Keyring]
    end
    
    subgraph "Input Validation"
        UserInput[User Input] --> InputValidator[Input Validator]
        InputValidator --> Sanitization[SPARQL Injection Prevention]
        Sanitization --> QueryBuilder[Query Builder]
    end
    
    subgraph "Network Security"
        HTTPSOnly[HTTPS Only]
        CertValidation[Certificate Validation]
        AuthHeaders[Auth Header Injection]
    end
```

## Testing Architecture

```mermaid
graph TB
    subgraph "Test Types"
        UT[Unit Tests<br/>Individual Components]
        IT[Integration Tests<br/>Component Interaction]
        E2E[End-to-End Tests<br/>Full User Journeys]
    end
    
    subgraph "Test Infrastructure"
        MockEndpoint[Mock SPARQL Endpoint]
        TestFixtures[Test Data Fixtures]
        ConfigMocks[Configuration Mocks]
    end
    
    subgraph "Test Execution"
        pytest[Pytest Framework]
        Coverage[Coverage Reporting]
        CI[Continuous Integration]
    end
    
    UT --> MockEndpoint
    IT --> MockEndpoint
    E2E --> MockEndpoint
    
    UT --> TestFixtures
    IT --> TestFixtures
    E2E --> ConfigMocks
    
    pytest --> Coverage
    Coverage --> CI
```

## Deployment Architecture

```mermaid
graph LR
    subgraph "Development"
        DevCode[Source Code] --> DevBuild[Build Process]
        DevBuild --> DevTest[Test Suite]
        DevTest --> DevPackage[Package Creation]
    end
    
    subgraph "Distribution"
        DevPackage --> PyPI[PyPI Package]
        PyPI --> UserInstall[pip install kb-query]
    end
    
    subgraph "User System"
        UserInstall --> CreateDirs[Create XDG Directories]
        CreateDirs --> InitConfig[Initialize Configuration]
        InitConfig --> Ready[Ready to Use]
    end
    
    subgraph "Runtime Dependencies"
        Python[Python 3.8+]
        RDFLib[rdflib]
        Requests[requests]
        Click[click/typer]
        Rich[rich]
    end
```

## Performance Monitoring

```mermaid
graph TB
    subgraph "Metrics Collection"
        TimingMetrics[Query Timing]
        CacheMetrics[Cache Hit Rates] 
        ErrorMetrics[Error Frequencies]
        MemoryMetrics[Memory Usage]
    end
    
    subgraph "Performance Targets"
        GrammarLoad["Grammar Load < 500ms"]
        PatternMatch["Pattern Match < 50ms"]
        SPARQLGen["SPARQL Gen < 10ms"]
        ResultFormat["Result Format < 100ms"]
    end
    
    TimingMetrics --> GrammarLoad
    TimingMetrics --> PatternMatch
    TimingMetrics --> SPARQLGen
    TimingMetrics --> ResultFormat
    
    CacheMetrics --> CacheOptimization[Cache Optimization]
    ErrorMetrics --> ErrorReduction[Error Reduction]
    MemoryMetrics --> MemoryOptimization[Memory Optimization]
```