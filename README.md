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
# Default model
ollama pull llama2

# Or try other models
ollama pull mistral
ollama pull codellama
```

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
# Save the result
slogan-gen generate "pizza restaurant" --output result.txt
```

## Configuration

### Environment Variables

Configure defaults using environment variables:

```bash
export SLOGAN_BASE_URL="http://localhost:11434/v1"
export SLOGAN_MODEL_NAME="llama2"
export SLOGAN_MAX_ITERATIONS=5
export SLOGAN_TEMPERATURE=0.7
export SLOGAN_TIMEOUT=120
```

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

If slogan generation is slow, try:

- Using a smaller model (e.g., `llama2` instead of `llama2:70b`)
- Reducing `--max-turns` to limit iterations
- Checking your system resources

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
