# Development Guide

Complete guide for developers contributing to the Slogan Writer-Reviewer Agent System.

## Overview

This guide covers setting up your development environment, running tests, maintaining code quality, and contributing to the project.

**Project Stack:**

- **Language**: Python 3.11+
- **Package Manager**: uv (fast Python package installer)
- **Framework**: Microsoft Agent Framework + Ollama
- **API**: FastAPI
- **CLI**: Click
- **Testing**: pytest
- **Code Quality**: Ruff (linter + formatter), mypy (type checker)

---

## Development Setup

### Prerequisites

Ensure you have these installed:

- **Python 3.11+**: `python --version`
- **uv**: Fast Python package manager ([install guide](https://github.com/astral-sh/uv))
- **Ollama**: Local LLM runtime ([install guide](https://ollama.ai))
- **Git**: Version control

### Clone Repository

```bash
git clone https://github.com/your-org/microsoft-agent-framework-with-ollama.git
cd microsoft-agent-framework-with-ollama-1
```

### Create Virtual Environment

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### Install Dependencies

```bash
# Install in editable mode with dev dependencies
uv pip install -e ".[dev]"

# Verify installation
slogan-gen --version
```

**Dependency Groups:**

- **Default**: Core runtime dependencies
- **dev**: Development tools (pytest, ruff, mypy, coverage)
- **docs**: Documentation tools (mkdocs, mkdocs-material)

**Install All Dependencies:**

```bash
uv pip install -e ".[dev,docs]"
```

### Setup Ollama

```bash
# Ensure Ollama is running
ollama serve

# Pull test model
ollama pull mistral:latest
```

### Verify Setup

```bash
# Check configuration
slogan-gen config show

# Test generation
slogan-gen generate "test" --model mistral:latest

# Run tests
pytest
```

---

## Project Structure

```
microsoft-agent-framework-with-ollama-1/
├── src/
│   ├── agents/           # Writer and Reviewer agent implementations
│   │   ├── writer.py     # Writer agent (generates slogans)
│   │   └── reviewer.py   # Reviewer agent (provides feedback)
│   ├── orchestration/    # Workflow coordination
│   │   ├── workflow.py   # Main workflow logic
│   │   └── models.py     # Data models (Turn, Session)
│   ├── cli/              # Command-line interface
│   │   ├── main.py       # CLI commands (generate, models, config)
│   │   └── output.py     # Output formatting
│   ├── api/              # REST API (FastAPI)
│   │   ├── main.py       # FastAPI app and startup
│   │   ├── routes/       # API endpoints (health, generate, models)
│   │   ├── schemas/      # Request/response models
│   │   ├── middleware.py # Request ID, CORS, error handling
│   │   └── exceptions.py # Custom exceptions
│   └── config/           # Configuration management
│       └── settings.py   # Pydantic settings (OllamaConfig)
├── tests/
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── api/              # API tests
├── docs/                 # MkDocs documentation
├── pyproject.toml        # Project configuration
└── README.md             # Main documentation
```

### Key Principles

**3-Layer Architecture:**

1. **Agent Layer** (`src/agents/`): AI agent implementations
2. **Orchestration Layer** (`src/orchestration/`): Workflow coordination
3. **Interface Layer** (`src/cli/`, `src/api/`): User interfaces

**Benefits:**

- Separation of concerns
- Easy to add new interfaces (e.g., Web UI)
- Testable components
- Shared business logic

---

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Edit code, add tests, update documentation.

### 3. Run Code Quality Checks

```bash
# Format code
ruff format src/ tests/

# Lint code
ruff check src/ tests/ --fix

# Type check
mypy src/
```

### 4. Run Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add your feature description"
```

**Commit Message Format:**

```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `chore`: Maintenance tasks

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Create a Pull Request on GitHub.

---

## Testing

### Running Tests

**All Tests:**

```bash
pytest
```

**Specific Test File:**

```bash
pytest tests/unit/test_workflow.py
```

**Specific Test:**

```bash
pytest tests/unit/test_workflow.py::test_successful_approval
```

**With Verbose Output:**

```bash
pytest -v
```

**With Print Statements:**

```bash
pytest -s
```

### Test Categories

**Unit Tests** (`tests/unit/`):

- Test individual components in isolation
- Fast, no external dependencies
- Mock Ollama responses

```python
# Example: tests/unit/test_workflow.py
def test_successful_approval(mock_ollama_client):
    """Test workflow completes when reviewer approves."""
    # ...
```

**Integration Tests** (`tests/integration/`):

- Test component interactions
- Require Ollama running
- Use real models

```python
# Example: tests/integration/test_end_to_end.py
async def test_end_to_end_generation():
    """Test complete slogan generation workflow."""
    # ...
```

**API Tests** (`tests/api/`):

- Test FastAPI endpoints
- Use TestClient
- Mock Ollama where needed

```python
# Example: tests/api/test_generate.py
def test_generate_slogan_success(client):
    """Test successful slogan generation via API."""
    response = client.post("/api/v1/slogans/generate", json={...})
    assert response.status_code == 200
```

### Coverage

**Generate Coverage Report:**

```bash
pytest --cov=src --cov-report=html --cov-report=term
```

**View HTML Report:**

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

**Coverage Goals:**

- Overall: >80%
- Critical paths (agents, orchestration): >90%

---

## Code Quality Tools

### Ruff (Linter + Formatter)

Ruff is a fast Python linter and formatter (replaces Black, isort, flake8).

**Format Code:**

```bash
ruff format src/ tests/
```

**Lint Code:**

```bash
# Check for issues
ruff check src/ tests/

# Auto-fix issues
ruff check src/ tests/ --fix
```

**Configuration** (`pyproject.toml`):

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
ignore = ["E501"]  # Line too long (handled by formatter)
```

### Mypy (Type Checker)

Mypy ensures type safety and catches type errors.

**Run Type Checks:**

```bash
mypy src/
```

**Configuration** (`pyproject.toml`):

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

**Common Type Issues:**

```python
# ❌ Missing type annotations
def process_data(data):
    return data

# ✅ With type annotations
def process_data(data: str) -> str:
    return data
```

### Pre-Commit Checklist

Before committing, ensure:

1. **Code is formatted**: `ruff format src/ tests/`
2. **No lint errors**: `ruff check src/ tests/`
3. **Types are correct**: `mypy src/`
4. **Tests pass**: `pytest`
5. **Coverage is good**: `pytest --cov=src`

**Automated Pre-Commit Hook** (optional):

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
EOF

# Install hook
pre-commit install

# Now checks run automatically on commit
```

---

## Adding New Features

### Example: Adding a New Agent

**1. Define Agent Interface** (`src/agents/base.py`):

```python
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate response from agent."""
        pass
```

**2. Implement Agent** (`src/agents/editor.py`):

```python
from src.agents.base import BaseAgent

class EditorAgent(BaseAgent):
    """Agent that edits and improves slogans."""
    
    async def generate(self, prompt: str) -> str:
        # Implementation
        pass
```

**3. Add Tests** (`tests/unit/test_editor.py`):

```python
import pytest
from src.agents.editor import EditorAgent

@pytest.mark.asyncio
async def test_editor_improves_slogan():
    agent = EditorAgent()
    result = await agent.generate("Make this better: Pizza Place")
    assert len(result) > 0
```

**4. Update Workflow** (`src/orchestration/workflow.py`):

Integrate new agent into existing workflow.

**5. Document** (update relevant docs):

- API reference
- Architecture docs
- User guides

---

## Debugging

### CLI Debugging

**Verbose Mode:**

```bash
slogan-gen generate "test" --verbose
```

**Python Debugger:**

```python
# Add to code
import pdb; pdb.set_trace()

# Or use breakpoint() (Python 3.7+)
breakpoint()
```

**Run with Debugger:**

```bash
python -m pdb -m src.cli.main generate "test"
```

### API Debugging

**Debug Logging:**

```bash
export API_LOG_LEVEL=DEBUG
uvicorn src.api.main:app --reload
```

**FastAPI Debug Mode:**

```python
# src/api/main.py
app = FastAPI(debug=True)
```

**VS Code Debugging** (`.vscode/launch.json`):

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["src.api.main:app", "--reload"],
      "jinja": true
    }
  ]
}
```

---

## Common Issues

### Import Errors

**Problem:**

```
ModuleNotFoundError: No module named 'agents'
```

**Solution:**

```bash
# Reinstall in editable mode
uv pip install -e .
```

### Missing py.typed Files

**Problem:**

```
error: Skipping analyzing "agents": module is installed, but missing library stubs
```

**Solution:**

```bash
# Create py.typed markers
touch src/py.typed
touch src/agents/py.typed
touch src/cli/py.typed
touch src/config/py.typed
touch src/orchestration/py.typed
```

### Ollama Connection Errors

**Problem:**

```
❌ Cannot connect to Ollama at http://localhost:11434
```

**Solutions:**

```bash
# 1. Start Ollama
ollama serve

# 2. Check if running
curl http://localhost:11434/api/tags

# 3. Verify model installed
ollama list
```

### Test Failures

**Problem:** Tests fail with connection errors.

**Solution:**

```bash
# Ensure Ollama is running
ollama serve

# Pull test model
ollama pull mistral:latest

# Run tests
pytest
```

---

## Contributing Guidelines

### Code Style

- **Follow PEP 8**: Use ruff for formatting
- **Type Annotations**: All functions must have type hints
- **Docstrings**: Use Google style docstrings
- **Line Length**: 100 characters max

**Example:**

```python
def generate_slogan(
    input_text: str,
    model: str = "mistral:latest",
    max_turns: int = 5
) -> dict[str, Any]:
    """Generate a slogan using Writer-Reviewer collaboration.
    
    Args:
        input_text: Product or service description
        model: Ollama model identifier
        max_turns: Maximum iteration rounds
    
    Returns:
        Dictionary containing final slogan and metadata
    
    Raises:
        ValueError: If input_text is empty or invalid
        ConnectionError: If cannot connect to Ollama
    """
    # Implementation
    pass
```

### Testing Requirements

- **All new features must have tests**
- **Maintain >80% coverage**
- **Include unit and integration tests**
- **Test edge cases and error handling**

### Documentation Requirements

- **Update relevant docs** in `docs/`
- **Add docstrings** to all functions/classes
- **Include usage examples**
- **Update CHANGELOG.md**

### Pull Request Process

1. **Create feature branch**: `git checkout -b feature/name`
2. **Make changes**: Code + tests + docs
3. **Run quality checks**: ruff, mypy, pytest
4. **Commit with clear message**: `feat: add feature`
5. **Push and create PR**
6. **Address review feedback**
7. **Merge after approval**

---

## Performance Testing

### Benchmarking

**CLI Performance:**

```bash
time slogan-gen generate "test" --model gemma2:2b
time slogan-gen generate "test" --model mistral:latest
time slogan-gen generate "test" --model llama3.2:latest
```

**API Performance:**

```bash
# Using Apache Bench
ab -n 100 -c 10 -p request.json -T application/json \
  http://localhost:8000/api/v1/slogans/generate

# Using wrk
wrk -t12 -c400 -d30s --latency \
  http://localhost:8000/api/v1/health
```

### Load Testing

See [API Usage Guide](api-usage.md#performance-considerations) for load testing details.

---

## Release Process

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes (2.0.0)
- **MINOR**: New features (1.1.0)
- **PATCH**: Bug fixes (1.0.1)

### Release Steps

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md**
3. **Run full test suite**: `pytest`
4. **Build package**: `python -m build`
5. **Create git tag**: `git tag v1.0.0`
6. **Push tag**: `git push origin v1.0.0`
7. **Create GitHub release**
8. **Publish to PyPI** (if applicable)

---

## Resources

### Documentation

- [Quick Start Guide](../getting-started/quickstart.md)
- [CLI Usage Guide](cli-usage.md)
- [API Usage Guide](api-usage.md)
- [Configuration Guide](../getting-started/configuration.md)
- [Troubleshooting Guide](../troubleshooting.md)

### External Resources

- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [Ollama Documentation](https://ollama.ai/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [pytest Documentation](https://docs.pytest.org/)

### Getting Help

- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions and share ideas
- **Pull Requests**: Contribute code improvements

---

## Appendix

### Useful Commands

```bash
# Development
uv pip install -e ".[dev]"          # Install dev dependencies
source .venv/bin/activate           # Activate virtual environment
slogan-gen --version                # Check installed version

# Testing
pytest                              # Run all tests
pytest -v                           # Verbose output
pytest --cov=src                    # With coverage
pytest -k "test_name"               # Run specific test

# Code Quality
ruff format src/ tests/             # Format code
ruff check src/ tests/ --fix       # Lint and auto-fix
mypy src/                           # Type check

# API
uvicorn src.api.main:app --reload  # Start dev server
curl http://localhost:8000/docs    # View API docs

# Documentation
mkdocs serve                        # Preview docs locally
mkdocs build                        # Build static site

# Git
git checkout -b feature/name        # Create feature branch
git add .                           # Stage changes
git commit -m "feat: description"  # Commit with message
git push origin feature/name        # Push branch
```

### Configuration Files

**pyproject.toml** - Project configuration:
- Dependencies
- Build system
- Tool configuration (ruff, mypy, pytest)

**mkdocs.yml** - Documentation configuration:
- Site structure
- Theme settings
- Plugins

**.env** - Environment variables (not committed):
- API configuration
- Ollama settings
- Development overrides

---

## Next Steps

1. **Set up your environment** following this guide
2. **Read the codebase** to understand the architecture
3. **Run the tests** to verify your setup
4. **Pick an issue** from GitHub to work on
5. **Create a PR** with your changes

Welcome to the project! 🎉
