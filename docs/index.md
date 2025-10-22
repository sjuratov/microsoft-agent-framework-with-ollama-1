# Slogan Writer-Reviewer Agent System

Multi-agent CLI application for generating creative slogans through iterative Writer-Reviewer collaboration using Microsoft Agent Framework and Ollama.

<div class="grid cards" markdown>

-   :material-robot:{ .lg .middle } __Multi-Agent Collaboration__

    ---

    Writer and Reviewer agents work together iteratively to create compelling slogans

-   :material-cog:{ .lg .middle } __Highly Configurable__

    ---

    Customize iterations, models, and output formats to match your needs

-   :material-lightning-bolt:{ .lg .middle } __Fast & Local__

    ---

    Runs entirely on your machine using Ollama - no API keys or external services

-   :material-api:{ .lg .middle } __CLI & REST API__

    ---

    Use from command line or integrate via FastAPI REST endpoints

</div>

## Overview

This tool uses two AI agents to collaboratively create compelling slogans:

- **Writer Agent**: Generates creative slogans based on your input
- **Reviewer Agent**: Provides critical feedback or approves with "SHIP IT!"

The agents iterate up to 10 times (default 5, configurable) until the reviewer approves or the maximum turns are reached.

## Key Features

- 🤖 **Multi-Agent Collaboration**: Writer and Reviewer agents work together iteratively
- 🔄 **Configurable Iterations**: Set custom iteration limits (1-10 turns, default 5)
- 👀 **Iteration Visibility**: Optional verbose mode to see the collaboration process
- 🎨 **Model Selection**: Choose different Ollama models for varied creative styles
- 🚀 **Fast & Local**: Runs entirely on your machine using Ollama
- ⏱️ **Performance Timing**: Track total duration and per-turn timing in verbose mode
- 🎨 **Color-Coded Output**: Clear visual feedback with styled terminal output
- 💾 **Multiple Output Formats**: Save results as text or JSON for integration
- 🔧 **Model Management**: List available models and validate before generation
- 🌐 **REST API**: Full FastAPI implementation with interactive docs

## Quick Links

<div class="grid" markdown>

[:material-download: **Installation**](getting-started/installation.md){ .md-button .md-button--primary }
[:material-rocket-launch: **Quick Start**](getting-started/quickstart.md){ .md-button }
[:material-console: **CLI Guide**](guides/cli-usage.md){ .md-button }
[:material-api: **API Guide**](guides/api-usage.md){ .md-button }

</div>

## Example Usage

### Command Line

```bash
# Basic usage
slogan-gen "eco-friendly water bottle"

# See the iteration process
slogan-gen "eco-friendly water bottle" --verbose

# Use a specific model
slogan-gen "tech startup" --model llama2

# Save output
slogan-gen "coffee shop" --output slogan.txt
```

### REST API

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/generate",
    json={
        "description": "eco-friendly water bottle",
        "max_iterations": 5
    }
)
print(response.json()["slogan"])
```

## Architecture

```
User Input
    ↓
Writer Agent ──────→ Generates Slogan
    ↓
Reviewer Agent ────→ Provides Feedback
    ↓
    ├─→ "SHIP IT!" → Done ✓
    └─→ Feedback → Writer Agent (iterate)
```

The system uses Microsoft Agent Framework for orchestration and Ollama for local LLM inference, ensuring fast, private, and cost-effective slogan generation.

## Get Started

Ready to generate creative slogans? Follow our [Installation Guide](getting-started/installation.md) to get started in minutes!

## Resources

- [Installation Guide](getting-started/installation.md) - Get up and running
- [Quick Start](getting-started/quickstart.md) - Your first slogan
- [CLI Usage](guides/cli-usage.md) - Complete command reference
- [API Usage](guides/api-usage.md) - REST API integration
- [Development Guide](guides/development.md) - Contributing to the project
- [Architecture](architecture/overview.md) - System design and patterns
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

## Prerequisites

- **Python 3.11+**: Required for modern async/await support
- **Ollama**: Local LLM runtime ([install from ollama.ai](https://ollama.ai))
- **uv**: Fast Python package manager ([install instructions](https://github.com/astral-sh/uv))

## License

This project is open source. See the project repository for license details.

## Contributing

Contributions are welcome! Please see our [Development Guide](guides/development.md) for details on how to contribute.
