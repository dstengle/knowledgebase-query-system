# ADR-003: Configuration Management

## Status
Accepted

## Context
The CLI needs to manage:
- Multiple endpoint profiles (dev, prod, test)
- Authentication credentials
- Grammar cache locations
- Debug settings

## Decision
Follow **XDG Base Directory Specification** for all configuration:

```
$XDG_CONFIG_HOME/kb-query/
├── config.yaml          # Main configuration
├── profiles/           # Endpoint profiles
│   ├── prod.yaml
│   └── dev.yaml
└── credentials/        # Encrypted credentials
    └── .credentials

$XDG_CACHE_HOME/kb-query/
├── grammar/            # Cached grammar files
│   └── {ontology-hash}.json
└── queries/            # Query history (future)
```

## Profile Structure

```yaml
# profiles/prod.yaml
name: production
endpoint: http://localhost:13030/kb
auth:
  type: basic
  username: ${KB_PROD_USER}
  password: ${KB_PROD_PASS}
timeout: 30
verify_ssl: true

# profiles/dev.yaml  
name: development
endpoint: http://fuseki:3030/test
auth:
  type: basic
  username: ${KB_DEV_USER}
  password: ${KB_DEV_PASS}
timeout: 60
verify_ssl: false
debug: true
```

## Consequences

### Positive
- Standard locations respect user preferences
- Profile system supports multiple environments
- Credentials can use environment variables
- Cache improves performance

### Negative
- Additional setup for first-time users
- Need to handle missing XDG variables on Windows

## Security Notes
- Credentials stored with 600 permissions
- Support for environment variable substitution
- Option to use system keyring (future enhancement)