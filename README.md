# Slogan Writer-Reviewer Agent System

Multi-agent CLI application for generating creative slogans through iterative Writer-Reviewer collaboration using Microsoft Agent Framework and Ollama.

## Overview

This tool uses two AI agents to collaboratively create compelling slogans:

- **Writer Agent**: Generates creative slogans based on your input
- **Reviewer Agent**: Provides critical feedback or approves with "SHIP IT!"

The agents iterate up to 10 times (default 5, configurable) until the reviewer approves or the maximum turns are reached.

## Features

- 🤖 **Multi-Agent Collaboration**: Writer and Reviewer agents work together iteratively
- 🔄 **Configurable Iterations**: Set custom iteration limits (1-10 turns, default 5)
- 👀 **Iteration Visibility**: Optional verbose mode to see the collaboration process
- 🎨 **Model Selection**: Choose different Ollama models for varied creative styles
- 🚀 **Fast & Local**: Runs entirely on your machine using Ollama
- ⏱️ **Performance Timing**: Track total duration and per-turn timing in verbose mode
- 🎨 **Color-Coded Output**: Clear visual feedback with styled terminal output
- 💾 **Multiple Output Formats**: Save results as text or JSON for integration
- 🔧 **Model Management**: List available models and validate before generation

## Prerequisites

- **Python 3.11+**: Required for modern async/await support
- **Ollama**: Local LLM runtime ([install from ollama.ai](https://ollama.ai))
- **uv**: Fast Python package manager ([install instructions](https://github.com/astral-sh/uv))

## Installation

### 1. Install Ollama

```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Or visit https://ollama.ai for other installation methods
```

### 2. Pull a Model

```bash
# Recommended: Fast, lightweight model for quick generation
ollama pull gemma2:2b

# Default: Good balance of speed and quality
ollama pull mistral

# Alternative models
ollama pull llama3.2:latest    # Latest Llama version
ollama pull phi3:mini          # Microsoft's efficient model
```

**Model Performance Tips:**

- **gemma2:2b** or **phi3:mini**: Best for speed (~5-10s total)
- **mistral**: Good balance of quality and performance (~15-30s total)
- **llama3.2:latest**: Higher quality, slower (~60s+ total)
- Models with 7B+ parameters may be slow on CPU-only systems

### 3. Install the CLI

```bash
# Clone the repository
cd microsoft-agent-framework-with-ollama-1

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

```bash
# Generate a slogan
slogan-gen generate "eco-friendly water bottle"
```

### Verbose Mode (See Iteration Process)

```bash
# Watch the agents collaborate
slogan-gen generate "tech startup" --verbose
```

### Custom Model

```bash
# Use a different Ollama model
slogan-gen generate "coffee shop" --model mistral
```

### Custom Iteration Limit

```bash
# Limit to 3 turns
slogan-gen generate "fitness app" --max-turns 3
```

### Save to File

```bash
# Save as text (default)
slogan-gen generate "pizza restaurant" --output result.txt

# Save as JSON for programmatic use
slogan-gen generate "pizza restaurant" --output result.json
```

**JSON Output Format:**

```json
{
  "input": "pizza restaurant",
  "final_slogan": "🍕 Slice of Heaven, Every Bite!",
  "completion_reason": "approved",
  "turn_count": 2,
  "max_turns": 5,
  "total_duration_seconds": 5.8,
  "average_duration_per_turn": 2.9,
  "turns": [
    {
      "turn_number": 1,
      "slogan": "Pizza Perfection in Every Slice",
      "feedback": "Good start, but needs more excitement...",
      "approved": false,
      "timestamp": "2024-01-15T10:30:00"
    },
    {
      "turn_number": 2,
      "slogan": "🍕 Slice of Heaven, Every Bite!",
      "feedback": "SHIP IT! Perfect combination of emoji and excitement.",
      "approved": true,
      "timestamp": "2024-01-15T10:30:05"
    }
  ]
}
```

## REST API

The application provides a FastAPI REST API for programmatic access to slogan generation.

### Starting the API Server

```bash
# Start the development server with auto-reload
uvicorn src.api.main:app --reload

# Production server (with workers)
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`.

### Interactive API Documentation

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>
- **OpenAPI Schema**: <http://localhost:8000/openapi.json>

### Generating OpenAPI Specification

You can export the OpenAPI specification to use with frontend generators, API clients, or documentation tools:

```bash
# Start the API server first
uvicorn src.api.main:app --reload

# In another terminal, export the OpenAPI spec
curl http://localhost:8000/openapi.json > docs/openapi.json
```

The generated `docs/openapi.json` file contains the complete API specification and can be used with:

- **Frontend generators**: GitHub Spark, Swagger Codegen, OpenAPI Generator
- **API clients**: Postman, Insomnia, Bruno
- **Documentation tools**: Stoplight, ReadMe, Redocly
- **Code generation**: TypeScript types, Python clients, etc.

### API Endpoints

#### Root Endpoint

```bash
curl http://localhost:8000/

# Response
{
  "message": "AI Slogan Generator API",
  "version": "1.0.0",
  "endpoints": {
    "health": "/api/v1/health",
    "models": "/api/v1/models",
    "generate": "/api/v1/slogans/generate"
  }
}
```

#### Health Check

```bash
curl http://localhost:8000/api/v1/health

# Response
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "ollama": {
    "status": "connected",
    "base_url": "http://localhost:11434/v1"
  }
}
```

#### List Available Models

```bash
curl http://localhost:8000/api/v1/models

# Response
{
  "models": [
    {
      "id": "mistral:latest",
      "name": "Mistral 7B",
      "size": "7B",
      "description": "Fast and capable instruction-following model"
    }
  ],
  "total": 1,
  "default_model": "mistral:latest"
}
```

#### Generate Slogan

```bash
curl -X POST http://localhost:8000/api/v1/slogans/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input": "coffee shop",
    "model": "mistral:latest",
    "max_turns": 5,
    "verbose": false
  }'

# Response (streaming disabled)
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "input": "coffee shop",
  "final_slogan": "☕ Brew Happiness, One Cup at a Time",
  "completion_reason": "approved",
  "turn_count": 2,
  "max_turns": 5,
  "total_duration_seconds": 4.2,
  "model_used": "mistral:latest",
  "turns": [...]
}
```

**Request Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `input` | string | Yes | - | Business/product description (3-200 chars) |
| `model` | string | No | `mistral:latest` | Ollama model to use |
| `max_turns` | integer | No | `5` | Max iteration rounds (1-10) |
| `verbose` | boolean | No | `false` | Include detailed turn information |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `request_id` | string | Unique request identifier (UUID) |
| `input` | string | Original input description |
| `final_slogan` | string | Generated slogan (if successful) |
| `completion_reason` | string | `approved`, `max_turns_reached`, or `error` |
| `turn_count` | integer | Number of iterations performed |
| `error` | string | Error message (only if failed) |
| `turns` | array | Turn-by-turn details (when `verbose=true`) |

### Python Client Example

```python
import httpx

# Generate slogan
response = httpx.post(
    "http://localhost:8000/api/v1/slogans/generate",
    json={
        "input": "coffee shop",
        "model": "mistral:latest",
        "max_turns": 5,
        "verbose": True
    },
    timeout=630.0  # 10.5 minutes (matches API timeout)
)

result = response.json()
print(f"Slogan: {result['final_slogan']}")
print(f"Took {result['turn_count']} turns in {result['total_duration_seconds']:.1f}s")
```

### API Configuration

Configure the API using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `API_CORS_ORIGINS` | `http://localhost:3000,http://localhost:8080` | Comma-separated CORS origins |
| `API_GENERATION_TIMEOUT` | `600` | Max generation time (seconds) |
| `API_REQUEST_TIMEOUT` | `630` | Total request timeout (seconds) |
| `API_LOG_LEVEL` | `WARNING` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `API_MAX_CONCURRENT_REQUESTS` | `10` | Max simultaneous generations |

**Example Configuration:**

```bash
# .env file
API_CORS_ORIGINS=http://localhost:3000,https://myapp.com
API_GENERATION_TIMEOUT=300
API_LOG_LEVEL=INFO
API_MAX_CONCURRENT_REQUESTS=5

# Start with environment
uvicorn src.api.main:app --env-file .env
```

### Error Responses

All errors follow a consistent format and include the `X-Request-ID` header for tracking:

**Validation Error (422):**

```json
{
  "detail": [
    {
      "loc": ["body", "input"],
      "msg": "String should have at least 3 characters",
      "type": "string_too_short"
    }
  ]
}
```

**HTTP Error (400, 404, 500):**

```json
{
  "detail": "Model 'unknown' not found in Ollama",
  "status_code": 400
}
```

**Request ID Header:**

Every response includes `X-Request-ID` for debugging:

```bash
curl -I http://localhost:8000/api/v1/health
# X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
```

## Configuration

### Environment Variables

Configure defaults using environment variables:

```bash
export OLLAMA_BASE_URL="http://localhost:11434/v1"
export OLLAMA_MODEL_NAME="mistral:latest"
export OLLAMA_MAX_TURNS=5
export OLLAMA_TEMPERATURE=0.7
export OLLAMA_MAX_TOKENS=500
export OLLAMA_TIMEOUT=30
```

**Note**: Environment variable names changed from `SLOGAN_*` to `OLLAMA_*` in recent versions.

### Configuration Commands

```bash
# Show current configuration
slogan-gen config show

# Set a value
slogan-gen config set model_name mistral

# List available models
slogan-gen models
```

## Development

### Setup Development Environment

```bash
# Install with development dependencies
uv pip install -e ".[dev]"
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
ruff format src/ tests/

# Lint code
ruff check src/ tests/

# Type check
mypy src/
```

## Troubleshooting

### Ollama Connection Error

```text
❌ Error: Cannot connect to Ollama at http://localhost:11434
```

**Solution**: Ensure Ollama is running:

```bash
ollama serve
```

### Model Validation Errors (String Too Long)

```text
❌ Workflow Error: 2 validation errors for Turn
slogan: String should have at most 500 characters
feedback: String should have at most 1000 characters
```

**Cause**: Smaller models (1B-2B parameters) like `gemma3:1b` may not follow instructions well and generate verbose output instead of concise slogans.

**Solution**: Use a larger, more instruction-following model:

```bash
# Recommended: Use mistral (7B parameters)
slogan-gen generate "coffee shop" --model mistral:latest

# Or use phi3:mini (3.8B parameters)
slogan-gen generate "coffee shop" --model phi3:mini
```

**Why this happens**: Smaller models sometimes:

- Generate explanations instead of just the slogan
- Provide overly detailed feedback with examples
- Don't follow the "concise output" instructions

**Model Recommendations by Use Case**:

| Model | Size | Instruction Following | Best For |
|-------|------|----------------------|----------|
| gemma2:2b | 2B | Fair | Quick testing only |
| phi3:mini | 3.8B | Good | Development |
| mistral:latest | 7B | Excellent | Production (default) |
| llama3.2:latest | 8B | Excellent | High quality output |

**Note**: The validation limits (500 chars for slogans, 1000 chars for feedback) are intentionally strict to enforce quality. This is working as designed.

### Model Not Found

```text
❌ Error: Model 'unknown-model' not found
```

**Solution**: Pull the model first:

```bash
ollama pull llama2
```

### Slow Generation

If slogan generation is slow:

**Quick Wins:**

- **Use a smaller model**: `gemma2:2b` (2B params) is 100x+ faster than `llama3:8b`
- **Reduce max-turns**: Use `--max-turns 3` to limit iterations
- **Check system resources**: Close other apps, ensure adequate RAM

**Model Size Comparison:**

| Model | Size | Typical Time (2 turns) | Quality |
|-------|------|----------------------|---------|
| gemma2:2b | 2B | ~5-10s | Good |
| phi3:mini | 3.8B | ~10-15s | Very Good |
| mistral:latest | 7B | ~15-30s | Excellent |
| llama3:8b | 8B | ~60-120s | Excellent |

**Performance bottleneck**: LLMs are computationally intensive. CPU-only generation is slow for 7B+ models. Consider:

- Using GPU acceleration (NVIDIA/AMD GPU with Ollama CUDA/ROCm support)
- Switching to a smaller model for development/testing
- Running on a machine with more cores/RAM

## Architecture

The application follows a 3-layer architecture:

- **CLI Layer** (`src/cli/`): Command-line interface using Click
- **Orchestration Layer** (`src/orchestration/`): Workflow coordination between agents
- **Agent Layer** (`src/agents/`): Writer and Reviewer agent implementations

This design enables future FastAPI integration by reusing the orchestration and agent layers.

## License

[Your License Here]

## Contributing

Contributions welcome! Please ensure all tests pass and code follows the style guide (Ruff + mypy).
