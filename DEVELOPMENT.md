# Development Guide

This guide provides instructions for developers contributing to the Slogan Writer-Reviewer Agent System.

## Development Setup

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- [Ollama](https://ollama.ai) for running tests with real LLMs
- Git for version control

### Initial Setup

```bash
# Clone the repository
git clone <repository-url>
cd microsoft-agent-framework-with-ollama-1

# Install with development dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Pull a test model
ollama pull mistral:latest
```

## Development Workflow

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/unit/test_workflow.py

# Run specific test
uv run pytest tests/unit/test_workflow.py::TestIsApproved::test_approved_exact_match

# Run with coverage
uv run pytest --cov=src --cov-report=html
open htmlcov/index.html  # View coverage report
```

**Test Organization:**

- `tests/unit/`: Unit tests for individual components
- `tests/integration/`: Integration tests (require Ollama running)
- All tests use pytest with async support (pytest-asyncio)

### Code Quality Tools

#### Linting with Ruff

```bash
# Check all code
uv run ruff check src/ tests/

# Auto-fix issues
uv run ruff check --fix src/ tests/

# Auto-fix with unsafe fixes (whitespace, etc.)
uv run ruff check --fix --unsafe-fixes src/ tests/
```

**Ruff Configuration** (in `pyproject.toml`):

- Line length: 100 characters
- Target: Python 3.11
- Rules: E (pycodestyle errors), F (pyflakes), I (isort), N (pep8-naming), UP (pyupgrade), W (whitespace)

#### Formatting with Ruff

```bash
# Format all code
uv run ruff format src/ tests/

# Check formatting without changing files
uv run ruff format --check src/ tests/
```

#### Type Checking with Mypy

```bash
# Type check all modules
uv run mypy -p agents -p cli -p config -p orchestration --show-error-codes

# Strict mode (already configured in pyproject.toml)
uv run mypy -p agents -p cli -p config -p orchestration --strict
```

**Mypy Configuration** (in `pyproject.toml`):

- Python version: 3.11
- Strict mode enabled
- Disallow untyped definitions
- Warn on unused configs and return Any

### Pre-Commit Checklist

Before committing code, ensure:

```bash
# 1. Format code
uv run ruff format src/ tests/

# 2. Lint and fix issues
uv run ruff check --fix src/ tests/

# 3. Type check
uv run mypy -p agents -p cli -p config -p orchestration

# 4. Run all tests
uv run pytest

# 5. Check coverage (optional)
uv run pytest --cov=src --cov-report=term-missing
```

## Project Structure

```
microsoft-agent-framework-with-ollama-1/
├── src/
│   ├── agents/          # Agent implementations
│   │   ├── writer.py    # Writer agent
│   │   └── reviewer.py  # Reviewer agent
│   ├── cli/             # Command-line interface
│   │   ├── main.py      # CLI commands
│   │   └── output.py    # Output formatting
│   ├── config/          # Configuration management
│   │   └── settings.py  # Pydantic settings
│   └── orchestration/   # Workflow coordination
│       ├── workflow.py  # Orchestration logic
│       └── models.py    # Data models
├── tests/
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
├── pyproject.toml       # Project configuration
├── README.md            # User documentation
└── DEVELOPMENT.md       # This file
```

## Architecture

### Layer Design

1. **CLI Layer** (`src/cli/`):
   - Entry point via Click commands
   - Handles user input/output
   - Delegates to orchestration layer

2. **Orchestration Layer** (`src/orchestration/`):
   - Coordinates Writer-Reviewer workflow
   - Manages iteration state
   - Independent of CLI (reusable for FastAPI)

3. **Agent Layer** (`src/agents/`):
   - Individual agent implementations
   - Uses OpenAI-compatible API via Ollama
   - Stateless design

4. **Configuration Layer** (`src/config/`):
   - Environment variable management
   - Pydantic settings validation
   - Model discovery

### Key Design Principles

- **Separation of Concerns**: Each layer has distinct responsibilities
- **Testability**: Pure functions, dependency injection, async/await
- **Type Safety**: Full type hints, mypy strict mode
- **Simplicity**: Clear naming, minimal abstractions, explicit over implicit

## Adding New Features

### Adding a New CLI Command

1. Add command function in `src/cli/main.py`:

```python
@cli.command()
@click.argument("input")
def my_command(input: str) -> None:
    """Description of command."""
    # Implementation
```

2. Add tests in `tests/unit/test_cli.py`
3. Update README.md with usage examples

### Adding a New Agent

1. Create agent file in `src/agents/`:

```python
"""My new agent."""

from config.settings import get_config

async def my_agent(input: str) -> str:
    """Agent description.
    
    Args:
        input: Input text
        
    Returns:
        Agent response
    """
    # Implementation
```

2. Add tests in `tests/unit/test_my_agent.py`
3. Update orchestration if needed

### Adding Configuration Options

1. Add field to `OllamaConfig` in `src/config/settings.py`:

```python
my_option: str = Field(
    default="default_value",
    description="Option description",
)
```

2. Add environment variable documentation to README.md
3. Add tests for configuration validation

## Debugging

### Running with Debugger

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Run command
uv run slogan-gen generate "test"
```

### Verbose Logging

```bash
# Enable verbose output to see agent interactions
uv run slogan-gen generate "test" --verbose
```

### Testing Ollama Connection

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Test generation directly
curl -X POST http://localhost:11434/api/generate \
  -d '{"model": "mistral:latest", "prompt": "Hello"}'
```

## Common Issues

### Import Errors

**Issue**: `ModuleNotFoundError: No module named 'agents'`

**Solution**: Install package in editable mode:

```bash
uv pip install -e .
```

### Mypy Errors

**Issue**: `error: Skipping analyzing "agents": module is installed, but missing library stubs`

**Solution**: Ensure `py.typed` marker files exist:

```bash
# Should exist:
src/py.typed
src/agents/py.typed
src/cli/py.typed
src/config/py.typed
src/orchestration/py.typed
```

### Test Failures

**Issue**: Tests fail with Ollama connection error

**Solution**: Ensure Ollama is running:

```bash
ollama serve
```

**Issue**: Tests fail with "model not found"

**Solution**: Pull the default model:

```bash
ollama pull mistral:latest
```

## Contributing Guidelines

### Code Style

- Follow PEP 8 (enforced by Ruff)
- Use type hints everywhere (enforced by mypy)
- Write docstrings for all public functions/classes
- Keep functions small and focused
- Prefer explicit over implicit

### Commit Messages

Use conventional commit format:

```
feat: add JSON output format
fix: handle timeout errors gracefully
docs: update README with new examples
test: add edge case tests for approval detection
refactor: simplify workflow iteration logic
```

### Pull Request Process

1. Create feature branch from `main`
2. Make changes with tests
3. Run pre-commit checklist
4. Create PR with clear description
5. Ensure CI passes
6. Request review

## Performance Testing

### Benchmarking Models

```bash
# Test different models
time uv run slogan-gen generate "test" --model gemma2:2b
time uv run slogan-gen generate "test" --model mistral:latest
time uv run slogan-gen generate "test" --model llama3:8b
```

### Profiling

```python
# Add profiling decorator
import cProfile

cProfile.run('main()', 'profile_stats')

# Analyze results
import pstats
p = pstats.Stats('profile_stats')
p.sort_stats('cumulative').print_stats(10)
```

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Run full test suite
4. Tag release: `git tag v1.0.0`
5. Push tags: `git push --tags`
6. Build package: `uv build`
7. Publish: `uv publish`

## Getting Help

- Review existing tests for examples
- Check project constitution for design principles
- Ask in team discussions
- Reference Microsoft Agent Framework documentation
