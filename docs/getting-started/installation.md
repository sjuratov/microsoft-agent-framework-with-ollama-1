# Installation

This guide will walk you through installing the Slogan Writer-Reviewer Agent System on your machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+**: Required for modern async/await support
- **Ollama**: Local LLM runtime for running AI models
- **uv**: Fast Python package manager (recommended)

## Step 1: Install Ollama

Ollama is required to run local AI models. Install it for your platform:

### macOS and Linux

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Windows

Download and run the installer from [ollama.ai](https://ollama.ai)

### Verify Installation

```bash
# Check that Ollama is installed
ollama --version

# Start Ollama service (if not auto-started)
ollama serve
```

## Step 2: Pull an AI Model

Download at least one model for slogan generation. We recommend starting with `mistral` for the best balance of quality and speed:

### Recommended Models

```bash
# Default: Best balance of speed and quality (recommended)
ollama pull mistral

# Fast: Lightweight for quick testing
ollama pull gemma2:2b

# High Quality: Slower but better output
ollama pull llama3.2:latest

# Microsoft: Efficient and capable
ollama pull phi3:mini
```

### Model Comparison

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| `gemma2:2b` | 2B | ⚡⚡⚡ | ⭐⭐ | Quick testing |
| `phi3:mini` | 3.8B | ⚡⚡ | ⭐⭐⭐ | Development |
| `mistral` | 7B | ⚡ | ⭐⭐⭐⭐ | Production (default) |
| `llama3.2` | 8B | 🐌 | ⭐⭐⭐⭐⭐ | High quality output |

!!! tip "Performance Tip"
    Smaller models (2B-3B parameters) run much faster on CPU but may not follow instructions as well. For production use, stick with `mistral` or larger.

### Verify Model Installation

```bash
# List installed models
ollama list

# Test model generation
ollama run mistral "Write a short slogan for a coffee shop"
```

## Step 3: Install uv Package Manager

`uv` is a fast Python package manager that simplifies dependency management:

### Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# Via pip
pip install uv
```

For more installation options, see the [uv documentation](https://github.com/astral-sh/uv).

## Step 4: Install the Slogan Generator

Clone the repository and install the package:

```bash
# Clone the repository
git clone <repository-url>
cd microsoft-agent-framework-with-ollama-1

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package with dependencies
uv pip install -e .

# For development (includes testing and linting tools)
uv pip install -e ".[dev]"

# For documentation (includes MkDocs)
uv pip install -e ".[docs]"
```

!!! info "Editable Installation"
    The `-e` flag installs the package in "editable" mode, meaning changes to the source code take effect immediately without reinstalling.

## Step 5: Verify Installation

Test that everything is working:

```bash
# Test CLI installation
slogan-gen --version

# Test configuration
slogan-gen config show

# List available models
slogan-gen models

# Generate your first slogan
slogan-gen generate "eco-friendly water bottle"
```

If the slogan generation works, you're all set! 🎉

## Troubleshooting

### Ollama Not Running

**Error**: `❌ Error: Cannot connect to Ollama at http://localhost:11434`

**Solution**: Start the Ollama service:

```bash
ollama serve
```

### Model Not Found

**Error**: `❌ Error: Model 'mistral' not found`

**Solution**: Pull the model first:

```bash
ollama pull mistral
```

### Python Version Too Old

**Error**: `Requires Python >=3.11`

**Solution**: Upgrade Python:

```bash
# macOS (Homebrew)
brew install python@3.11

# Ubuntu/Debian
sudo apt install python3.11

# Windows: Download from python.org
```

### Command Not Found: slogan-gen

**Error**: `zsh: command not found: slogan-gen`

**Solution**: Ensure virtual environment is activated:

```bash
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

Or reinstall the package:

```bash
uv pip install -e .
```

## Next Steps

- [Quick Start Guide](quickstart.md) - Generate your first slogans
- [Configuration](configuration.md) - Customize default settings
- [CLI Usage](../guides/cli-usage.md) - Complete command reference
- [API Usage](../guides/api-usage.md) - Use the REST API

## Alternative: Using pip

If you prefer not to use `uv`, you can use standard `pip`:

```bash
# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install package
pip install -e .
pip install -e ".[dev]"  # With development dependencies
```

However, `uv` is significantly faster and provides better dependency resolution.
