# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run Commands

```bash
# Install dependencies
uv add -e .

# Start MCP server
uv run src.main

# Run linting
ruff check ./src

```

## Code Style Guidelines

### Imports
- Standard library → third-party → local modules
- Alphabetical ordering within groups
- Absolute imports preferred: `from src.api import get_customers`

### Types
- Type hints required on all functions/methods
- Use `Optional[Type]` for optional parameters
- Use `Union[Type1, Type2]` for multiple types

### Naming Conventions
- Variables/functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_CASE`
- Environment variables: `AUTH_TOKEN`, `API_KEY`

### Error Handling
- Use specific exception types in try/except blocks
- Log errors with `logger.error()`
- Return descriptive error messages to users
- Wrap all API calls in try/except blocks