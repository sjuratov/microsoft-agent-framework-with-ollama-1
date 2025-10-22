# Configuration

Learn how to customize the Slogan Writer-Reviewer Agent System to match your needs.

## Configuration Methods

The system can be configured in three ways (in order of precedence):

1. **Command-line flags** (highest priority)
2. **Environment variables**
3. **Default values** (lowest priority)

## Command-Line Configuration

Override settings for individual commands:

```bash
# Specify model
slogan-gen generate "input" --model mistral

# Set iteration limit
slogan-gen generate "input" --max-turns 7

# Enable verbose output
slogan-gen generate "input" --verbose

# Combine multiple options
slogan-gen generate "coffee shop" \
  --model llama3.2 \
  --max-turns 5 \
  --verbose \
  --output result.json
```

## Environment Variables

Set default values via environment variables:

### Ollama Configuration

```bash
# Ollama API base URL (default: http://localhost:11434/v1)
export OLLAMA_BASE_URL="http://localhost:11434/v1"

# Default model to use (default: mistral:latest)
export OLLAMA_MODEL_NAME="mistral:latest"

# Maximum iteration rounds (default: 5)
export OLLAMA_MAX_TURNS=5

# Temperature for generation (0.0-2.0, default: 0.7)
export OLLAMA_TEMPERATURE=0.7

# Maximum tokens per response (default: 500)
export OLLAMA_MAX_TOKENS=500

# Request timeout in seconds (default: 30)
export OLLAMA_TIMEOUT=30
```

### API Configuration

If using the REST API:

```bash
# Allowed CORS origins (comma-separated)
export API_CORS_ORIGINS="http://localhost:3000,http://localhost:8080"

# Maximum generation time in seconds (default: 600)
export API_GENERATION_TIMEOUT=600

# Total request timeout in seconds (default: 630)
export API_REQUEST_TIMEOUT=630

# Logging level (default: WARNING)
export API_LOG_LEVEL=INFO

# Maximum concurrent requests (default: 10)
export API_MAX_CONCURRENT_REQUESTS=10
```

### Using a .env File

Create a `.env` file in the project root:

```bash
# .env
OLLAMA_MODEL_NAME=mistral:latest
OLLAMA_MAX_TURNS=5
OLLAMA_TEMPERATURE=0.7
API_LOG_LEVEL=INFO
```

The application will automatically load these variables.

!!! tip "Environment File Loading"
    For the CLI, you can use `direnv` or manually source the file. For the API, `uvicorn` can load `.env` files with the `--env-file` flag.

## CLI Configuration Commands

### Show Current Configuration

Display all current settings:

```bash
slogan-gen config show
```

**Example Output:**

```yaml
Ollama Configuration:
  Base URL: http://localhost:11434/v1
  Model: mistral:latest
  Max Turns: 5
  Temperature: 0.7
  Max Tokens: 500
  Timeout: 30s

Available Models:
  - mistral:latest (default)
  - gemma2:2b
  - llama3.2:latest
```

### Set Configuration Values

Change default settings:

```bash
# Set default model
slogan-gen config set model_name mistral

# Set max iterations
slogan-gen config set max_turns 7

# Set temperature
slogan-gen config set temperature 0.9
```

!!! warning "Configuration Persistence"
    Currently, `config set` commands update environment variables for the current session only. For permanent changes, add them to your shell profile (`~/.zshrc`, `~/.bashrc`) or `.env` file.

### List Available Models

See what models you have installed:

```bash
slogan-gen models
```

**Example Output:**

```
Available Ollama Models:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Model              Size    Modified
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
mistral:latest     7B      2 days ago
gemma2:2b          2B      1 week ago
llama3.2:latest    8B      3 days ago
phi3:mini          3.8B    5 days ago
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Default model: mistral:latest
```

## Configuration Parameters Reference

### Model Selection

| Parameter | Description | Default | Valid Values |
|-----------|-------------|---------|--------------|
| `model` | Ollama model to use | `mistral:latest` | Any installed Ollama model |

**Examples:**

- `gemma2:2b` - Fast, lightweight
- `mistral:latest` - Balanced quality/speed
- `llama3.2:latest` - High quality
- `phi3:mini` - Microsoft's efficient model

### Generation Parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `max_turns` | Maximum iteration rounds | 5 | 1-10 |
| `temperature` | Creativity level | 0.7 | 0.0-2.0 |
| `max_tokens` | Max response length | 500 | 50-2000 |
| `timeout` | Request timeout (seconds) | 30 | 5-300 |

**Temperature Guide:**

- **0.0-0.3**: Very focused, deterministic (good for consistency)
- **0.4-0.7**: Balanced creativity (recommended for slogans)
- **0.8-1.2**: More creative and varied
- **1.3-2.0**: Highly creative, potentially chaotic

### Output Options

| Parameter | Description | Default | Valid Values |
|-----------|-------------|---------|--------------|
| `verbose` | Show iteration details | `false` | `true`, `false` |
| `output` | Save output to file | `None` | Any file path |

**Output Formats:**

- `.txt` - Plain text (slogan only)
- `.json` - Full JSON with metadata
- stdout - Console output (default)

## Advanced Configuration

### Custom Ollama Instance

Connect to a remote or custom Ollama instance:

```bash
export OLLAMA_BASE_URL="http://remote-server:11434/v1"
slogan-gen generate "test"
```

### Performance Tuning

Optimize for speed:

```bash
export OLLAMA_MODEL_NAME="gemma2:2b"  # Fastest model
export OLLAMA_MAX_TURNS=3              # Fewer iterations
export OLLAMA_MAX_TOKENS=200           # Shorter responses
export OLLAMA_TIMEOUT=15               # Shorter timeout
```

Optimize for quality:

```bash
export OLLAMA_MODEL_NAME="llama3.2:latest"  # Best model
export OLLAMA_MAX_TURNS=7                    # More iterations
export OLLAMA_TEMPERATURE=0.8                # More creative
export OLLAMA_MAX_TOKENS=800                 # Longer responses
```

### Shell Aliases

Create shortcuts for common configurations:

```bash
# Add to ~/.zshrc or ~/.bashrc

# Fast generation
alias slogan-fast='slogan-gen generate --model gemma2:2b --max-turns 3'

# High quality
alias slogan-hq='slogan-gen generate --model llama3.2 --max-turns 7 --verbose'

# Save as JSON
alias slogan-json='slogan-gen generate --output result.json'
```

Usage:

```bash
slogan-fast "coffee shop"
slogan-hq "luxury hotel"
```

## Configuration Examples

### Development Setup

Fast iterations for testing:

```bash
# .env.development
OLLAMA_MODEL_NAME=gemma2:2b
OLLAMA_MAX_TURNS=3
OLLAMA_TIMEOUT=15
API_LOG_LEVEL=DEBUG
```

### Production Setup

Quality and reliability:

```bash
# .env.production
OLLAMA_MODEL_NAME=mistral:latest
OLLAMA_MAX_TURNS=5
OLLAMA_TEMPERATURE=0.7
OLLAMA_TIMEOUT=30
API_LOG_LEVEL=WARNING
API_MAX_CONCURRENT_REQUESTS=10
```

### Load Testing Setup

Handle high volume:

```bash
# .env.loadtest
OLLAMA_MODEL_NAME=gemma2:2b
OLLAMA_MAX_TURNS=3
API_MAX_CONCURRENT_REQUESTS=50
API_GENERATION_TIMEOUT=300
```

## Troubleshooting Configuration

### Check Active Configuration

Verify what settings are active:

```bash
slogan-gen config show
```

### Environment Variable Not Working

Ensure proper export:

```bash
# Wrong (no export)
OLLAMA_MODEL_NAME=mistral

# Correct
export OLLAMA_MODEL_NAME=mistral
```

### Persistent Configuration

Add to shell profile for permanent changes:

```bash
# Add to ~/.zshrc or ~/.bashrc
export OLLAMA_MODEL_NAME="mistral:latest"
export OLLAMA_MAX_TURNS=5

# Reload shell
source ~/.zshrc  # or source ~/.bashrc
```

### Configuration Priority

Remember the precedence order:

1. **CLI flags** override everything
2. **Environment variables** override defaults
3. **Defaults** are used if nothing else set

Example:

```bash
# Environment sets default
export OLLAMA_MAX_TURNS=5

# CLI flag overrides environment
slogan-gen generate "test" --max-turns 3  # Uses 3, not 5
```

## Next Steps

- [Quick Start](quickstart.md) - Start generating slogans
- [CLI Usage](../guides/cli-usage.md) - Complete command reference
- [API Usage](../guides/api-usage.md) - REST API configuration
- [Troubleshooting](../troubleshooting.md) - Common configuration issues
