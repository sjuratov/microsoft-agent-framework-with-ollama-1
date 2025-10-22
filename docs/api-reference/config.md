# Configuration API Reference

This page documents the configuration management for the Slogan Writer-Reviewer system.

## Overview

The configuration system uses [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) to manage environment variables and provide type-safe configuration.

**Key Features**:

- Environment variable-based configuration
- `.env` file support
- Type validation with Pydantic
- Cached configuration singleton
- Automatic Ollama model discovery

---

## OllamaConfig

::: src.config.settings.OllamaConfig
    options:
      show_source: true
      heading_level: 3

**Purpose**: Main configuration class for Ollama settings.

### Configuration Fields

| Field | Type | Default | Range | Description |
|-------|------|---------|-------|-------------|
| `base_url` | str | `http://localhost:11434/v1` | | Ollama API endpoint |
| `model_name` | str | `mistral:latest` | | Default model identifier |
| `temperature` | float | `0.7` | 0.0-2.0 | Sampling temperature |
| `max_tokens` | int | `500` | 1-4096 | Maximum response length |
| `timeout` | int | `30` | 1-300 | Request timeout (seconds) |
| `max_turns` | int | `5` | 1-10 | Maximum iteration turns |

### Environment Variables

All fields can be configured via environment variables with the `OLLAMA_` prefix:

| Environment Variable | Maps To | Example |
|---------------------|---------|---------|
| `OLLAMA_BASE_URL` | `base_url` | `http://localhost:11434/v1` |
| `OLLAMA_MODEL_NAME` | `model_name` | `mistral:latest` |
| `OLLAMA_TEMPERATURE` | `temperature` | `0.7` |
| `OLLAMA_MAX_TOKENS` | `max_tokens` | `500` |
| `OLLAMA_TIMEOUT` | `timeout` | `30` |
| `OLLAMA_MAX_TURNS` | `max_turns` | `5` |

### .env File Support

Create a `.env` file in your project root:

```bash
# .env
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL_NAME=llama3.2:latest
OLLAMA_TEMPERATURE=0.8
OLLAMA_MAX_TOKENS=1000
OLLAMA_TIMEOUT=60
OLLAMA_MAX_TURNS=7
```

The configuration will automatically load from this file.

### Usage Example

```python
from src.config.settings import OllamaConfig

# Create config (loads from environment/file)
config = OllamaConfig()

print(f"Using model: {config.model_name}")
print(f"Temperature: {config.temperature}")
print(f"Max turns: {config.max_turns}")

# Override values
custom_config = OllamaConfig(
    model_name="gemma2:2b",
    max_turns=3,
    temperature=0.9
)

# Validation is automatic
try:
    invalid = OllamaConfig(temperature=3.0)  # Error: must be <= 2.0
except ValueError as e:
    print(f"Validation error: {e}")
```

---

## Configuration Functions

### get_ollama_config

::: src.config.settings.get_ollama_config
    options:
      show_source: true
      heading_level: 4

**Purpose**: Get cached configuration singleton.

**Returns**: `OllamaConfig` instance

**Behavior**:

- First call: Creates and caches configuration
- Subsequent calls: Returns cached instance
- Cache can be cleared: `get_ollama_config.cache_clear()`

**Usage Example**:

```python
from src.config import get_ollama_config

# Get config (cached)
config = get_ollama_config()

# Use in agents
from src.agents import create_writer_agent
writer = create_writer_agent(config)

# Clear cache to reload config
import os
os.environ["OLLAMA_MODEL_NAME"] = "llama3.2:latest"
get_ollama_config.cache_clear()
config = get_ollama_config()  # Reloads with new environment
```

---

### get_available_models

::: src.config.settings.get_available_models
    options:
      show_source: true
      heading_level: 4

**Purpose**: Query Ollama API for installed models.

**Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_url` | str \| None | `None` | Ollama base URL (uses config if None) |
| `timeout` | int | `10` | Request timeout in seconds |

**Returns**: `list[str]` - List of model names

**Raises**:

- `ConnectionError`: Cannot connect to Ollama
- `RuntimeError`: API request failed

**Usage Example**:

```python
from src.config import get_available_models

# Get models using default config
try:
    models = get_available_models()
    print(f"Available models: {models}")
    # ['gemma2:2b', 'mistral:latest', 'llama3.2:latest']
    
except ConnectionError as e:
    print(f"Ollama not running: {e}")
except RuntimeError as e:
    print(f"API error: {e}")

# Use custom Ollama instance
models = get_available_models(
    base_url="http://remote-server:11434/v1",
    timeout=30
)
```

---

## Configuration Patterns

### Development Configuration

```python
# config/dev.env
OLLAMA_MODEL_NAME=gemma2:2b
OLLAMA_MAX_TURNS=3
OLLAMA_TIMEOUT=15
OLLAMA_TEMPERATURE=0.7
```

```python
from dotenv import load_dotenv
load_dotenv("config/dev.env")

from src.config import get_ollama_config
config = get_ollama_config()
```

### Production Configuration

```python
# config/prod.env
OLLAMA_MODEL_NAME=mistral:latest
OLLAMA_MAX_TURNS=5
OLLAMA_TIMEOUT=30
OLLAMA_TEMPERATURE=0.7
OLLAMA_MAX_TOKENS=500
```

### Testing Configuration

```python
# tests/conftest.py
import pytest
from src.config.settings import OllamaConfig

@pytest.fixture
def test_config():
    """Test configuration with fast model."""
    return OllamaConfig(
        model_name="gemma2:2b",
        max_turns=2,
        timeout=10
    )
```

### Runtime Configuration Override

```python
import os
from src.config import get_ollama_config

# Change configuration at runtime
os.environ["OLLAMA_MODEL_NAME"] = "llama3.2:latest"
os.environ["OLLAMA_MAX_TURNS"] = "7"

# Clear cache to reload
get_ollama_config.cache_clear()

# New config takes effect
config = get_ollama_config()
print(config.model_name)  # "llama3.2:latest"
print(config.max_turns)   # 7
```

---

## Configuration Validation

Pydantic automatically validates configuration:

### Type Validation

```python
# ❌ Invalid: wrong type
config = OllamaConfig(max_turns="five")  # Error: must be int

# ✅ Valid
config = OllamaConfig(max_turns=5)
```

### Range Validation

```python
# ❌ Invalid: out of range
config = OllamaConfig(temperature=3.0)  # Error: must be <= 2.0
config = OllamaConfig(max_turns=15)     # Error: must be <= 10

# ✅ Valid
config = OllamaConfig(temperature=0.8)
config = OllamaConfig(max_turns=7)
```

### URL Validation

```python
# ✅ Valid URLs
config = OllamaConfig(base_url="http://localhost:11434/v1")
config = OllamaConfig(base_url="http://192.168.1.100:11434/v1")
config = OllamaConfig(base_url="https://ollama.example.com/v1")
```

---

## Environment-Specific Configuration

### Docker/Container

```dockerfile
# Dockerfile
ENV OLLAMA_BASE_URL=http://ollama:11434/v1
ENV OLLAMA_MODEL_NAME=mistral:latest
ENV OLLAMA_MAX_TURNS=5
```

### Docker Compose

```yaml
# docker-compose.yml
services:
  app:
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434/v1
      - OLLAMA_MODEL_NAME=mistral:latest
      - OLLAMA_TEMPERATURE=0.7
```

### Kubernetes

```yaml
# deployment.yaml
env:
  - name: OLLAMA_BASE_URL
    value: "http://ollama-service:11434/v1"
  - name: OLLAMA_MODEL_NAME
    value: "mistral:latest"
  - name: OLLAMA_MAX_TURNS
    value: "5"
```

### Shell/Terminal

```bash
# .bashrc or .zshrc
export OLLAMA_BASE_URL="http://localhost:11434/v1"
export OLLAMA_MODEL_NAME="mistral:latest"
export OLLAMA_TEMPERATURE=0.7
export OLLAMA_MAX_TURNS=5

# Or inline
OLLAMA_MODEL_NAME=gemma2:2b slogan-gen generate "test"
```

---

## Configuration Best Practices

### Use .env Files

✅ **Do**:
```bash
# .env
OLLAMA_MODEL_NAME=mistral:latest
OLLAMA_MAX_TURNS=5
```

❌ **Don't**:
```python
# Hardcoded values
config = OllamaConfig(model_name="mistral:latest")  # Inflexible
```

### Validate Early

✅ **Do**:
```python
# Validate at startup
config = get_ollama_config()
models = get_available_models()
if config.model_name not in models:
    print(f"Warning: {config.model_name} not installed")
```

### Cache Wisely

✅ **Do**:
```python
# Clear cache when environment changes
os.environ["OLLAMA_MODEL_NAME"] = "new-model"
get_ollama_config.cache_clear()
config = get_ollama_config()
```

❌ **Don't**:
```python
# Forgetting to clear cache
os.environ["OLLAMA_MODEL_NAME"] = "new-model"
config = get_ollama_config()  # Still returns old cached config!
```

---

## Troubleshooting

### Configuration Not Loading

**Problem**: Changes to .env file not reflected

**Solution**:
```python
# Clear cache
get_ollama_config.cache_clear()

# Or restart application
```

### Model Validation Errors

**Problem**: `get_available_models()` raises ConnectionError

**Solution**:
```bash
# Ensure Ollama is running
ollama serve

# Verify Ollama is accessible
curl http://localhost:11434/api/tags
```

### Type Errors

**Problem**: Pydantic validation errors

**Solution**:
```python
# Check environment variable types
import os
print(type(os.environ.get("OLLAMA_MAX_TURNS")))  # str

# Pydantic converts automatically, but must be valid
os.environ["OLLAMA_MAX_TURNS"] = "5"     # ✅ Valid (converts to int)
os.environ["OLLAMA_MAX_TURNS"] = "five"  # ❌ Invalid (can't convert)
```

---

## See Also

- [Configuration Guide](../getting-started/configuration.md) - User configuration guide
- [CLI Usage Guide](../guides/cli-usage.md) - Using configuration via CLI
- [API Usage Guide](../guides/api-usage.md) - API configuration
- [Development Guide](../guides/development.md) - Development setup
