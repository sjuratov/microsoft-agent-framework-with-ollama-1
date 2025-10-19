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
