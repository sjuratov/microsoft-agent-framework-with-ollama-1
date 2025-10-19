# Quickstart Guide - Slogan Writer-Reviewer Agent System

**Feature**: 001-slogan-writer-reviewer  
**Date**: 2025-10-19  
**Audience**: Developers

## Overview

This guide will help you set up and start using the Slogan Writer-Reviewer agent system. You'll be generating creative slogans through AI agent collaboration in minutes.

## Prerequisites

### Required

- **Python 3.11 or higher** - Check with `python --version`
- **Ollama** - Local LLM runtime ([ollama.ai](https://ollama.ai))
- **uv** - Fast Python package manager ([docs.astral.sh/uv](https://docs.astral.sh/uv))

### Recommended

- **Terminal with Unicode support** - For rich CLI output
- **At least 8GB RAM** - For running Ollama models
- **10GB free disk space** - For model storage

## Installation

### Step 1: Install System Dependencies

#### Install Ollama

**macOS**:

```bash
brew install ollama
```

**Linux**:

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows**:

Download installer from [ollama.ai/download](https://ollama.ai/download)

#### Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or with pip:

```bash
pip install uv
```

### Step 2: Start Ollama Service

```bash
ollama serve
```

Keep this terminal window open. Ollama runs on `http://localhost:11434` by default.

### Step 3: Pull an Ollama Model

In a new terminal:

```bash
ollama pull llama2
```

This downloads the default model (~4GB). Other options:

```bash
ollama pull mistral      # Alternative model
ollama pull codellama    # Code-focused model
```

### Step 4: Clone and Setup Project

```bash
# Clone repository
git clone https://github.com/your-org/microsoft-agent-framework-with-ollama-1.git
cd microsoft-agent-framework-with-ollama-1

# Checkout feature branch
git checkout 001-slogan-writer-reviewer

# Create Python environment with uv
uv venv

# Activate environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -e .
```

## Quick Start

### Generate Your First Slogan

```bash
slogan-gen generate "eco-friendly water bottle"
```

Expected output:

```text
✨ Final Slogan ✨

"Hydrate Green, Stay Clean"

---
Generated in 3 turns using llama2
Reviewer status: Approved
```

### See the Iteration Process

Use `--verbose` to watch agents collaborate:

```bash
slogan-gen generate "affordable electric SUV" --verbose
```

You'll see:

- Each turn's slogan from the Writer
- Reviewer's detailed feedback
- Approval decision or refinement request

### Try Different Models

```bash
# Use Mistral model
slogan-gen generate "coffee shop" --model mistral

# List available models
slogan-gen models
```

### Control Iteration Count

```bash
# Allow up to 7 turns (default is 5)
slogan-gen generate "tech startup" --max-turns 7
```

## Configuration

### Environment Variables

Create a `.env` file or export variables:

```bash
export SLOGAN_MODEL_NAME=mistral
export SLOGAN_MAX_ITERATIONS=7
export SLOGAN_TEMPERATURE=0.8
```

### Config Command

```bash
# View current config
slogan-gen config show

# Change default model
slogan-gen config set model mistral

# Increase creativity
slogan-gen config set temperature 0.9
```

## Common Use Cases

### 1. Marketing Team Brainstorming

```bash
# Generate slogans for different products
slogan-gen generate "premium headphones" --verbose
slogan-gen generate "organic skincare line" --verbose
slogan-gen generate "smart home device" --verbose
```

### 2. Quick Exploration

```bash
# Generate multiple variations quickly
for product in "fitness app" "meal kit service" "online course platform"; do
    echo "=== $product ==="
    slogan-gen generate "$product"
    echo ""
done
```

### 3. Batch Processing with Output Files

```bash
# Save results to files
slogan-gen generate "tech startup" --output startup-slogan.txt
slogan-gen generate "restaurant" --output restaurant-slogan.txt
```

### 4. Different Creative Approaches

```bash
# Conservative (lower temperature)
slogan-gen generate "law firm" --config temperature 0.3

# Creative (higher temperature)
slogan-gen generate "art gallery" --config temperature 1.2
```

## Troubleshooting

### Ollama Connection Error

**Problem**:

```text
❌ Error: Cannot connect to Ollama at http://localhost:11434
```

**Solution**:

1. Check if Ollama is running: `ps aux | grep ollama`
2. Start Ollama: `ollama serve`
3. Verify endpoint: `curl http://localhost:11434/api/version`

### Model Not Found

**Problem**:

```text
❌ Error: Model 'llama2' not found
```

**Solution**:

```bash
# Pull the model
ollama pull llama2

# List available models
ollama list
```

### Slow Generation

**Problem**: Slogan generation takes too long.

**Solutions**:

- Use smaller model: `--model llama2` (instead of larger models)
- Reduce max turns: `--max-turns 3`
- Close other applications to free memory
- Check Ollama logs: `ollama logs`

### Empty or Poor Quality Output

**Problem**: Generated slogans are not creative or relevant.

**Solutions**:

- Provide more detailed input: `"Create a slogan for an eco-friendly water bottle that emphasizes sustainability and fun design"`
- Increase temperature for more creativity: `slogan-gen config set temperature 0.9`
- Try different model: `--model mistral`
- Use verbose mode to see agent reasoning: `--verbose`

## Development Workflow

### Run Tests

```bash
# All tests
uv run pytest

# Specific test file
uv run pytest tests/unit/test_workflow.py

# With coverage
uv run pytest --cov=src
```

### Code Quality Checks

```bash
# Linting with Ruff
uv run ruff check src/

# Type checking
uv run mypy src/

# Format code
uv run ruff format src/
```

### Development Mode

Install in editable mode for active development:

```bash
uv pip install -e ".[dev]"
```

## Next Steps

### Explore Advanced Features

- **Custom Agent Instructions**: Modify agent personalities in `src/agents/`
- **Workflow Customization**: Adjust iteration logic in `src/orchestration/`
- **New Output Formats**: Add JSON or CSV export in `src/cli/output.py`

### Contribute

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes following code quality guidelines
3. Add tests for new functionality
4. Submit pull request

### API Extension (Coming Soon)

The system is designed for future FastAPI extension. Stay tuned for:

- REST API endpoints
- WebSocket support for streaming
- Web-based UI

## Examples Gallery

### Marketing Slogans

```bash
# Tech products
slogan-gen generate "wireless earbuds with noise cancellation"
# Output: "Silence the World, Amplify Your Sound"

# Food & Beverage
slogan-gen generate "artisanal chocolate made with fair trade cocoa"
# Output: "Ethical Indulgence, Every Bite Matters"

# Services
slogan-gen generate "24/7 virtual assistant for busy professionals"
# Output: "Your Time, Multiplied"
```

### Event Campaigns

```bash
# Conference
slogan-gen generate "AI and machine learning conference for developers"
# Output: "Code the Future, Together"

# Product Launch
slogan-gen generate "innovative smart watch with health tracking"
# Output: "Your Health, Your Way, Your Wrist"
```

## Resources

### Documentation

- **Full Specification**: See `specs/001-slogan-writer-reviewer/spec.md`
- **Implementation Plan**: See `specs/001-slogan-writer-reviewer/plan.md`
- **Data Models**: See `specs/001-slogan-writer-reviewer/data-model.md`

### External Links

- **Ollama Documentation**: [ollama.ai/docs](https://ollama.ai/docs)
- **Microsoft Agent Framework**: [GitHub](https://github.com/microsoft/agent-framework)
- **Click Documentation**: [click.palletsprojects.com](https://click.palletsprojects.com)

### Support

- **Issues**: GitHub Issues tracker
- **Discussions**: GitHub Discussions
- **Constitution**: Project principles at `.specify/memory/constitution.md`

## Summary

You're now ready to generate creative slogans through AI agent collaboration! The system:

- ✅ Runs entirely locally (no cloud API costs)
- ✅ Provides full visibility into agent reasoning
- ✅ Supports multiple Ollama models
- ✅ Enables customization through configuration
- ✅ Follows code quality and simplicity principles

Happy slogan generating! 🎨✨
