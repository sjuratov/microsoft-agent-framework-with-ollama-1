# CLI Interface Contract

**Feature**: 001-slogan-writer-reviewer  
**Date**: 2025-10-19  
**Interface Type**: Command Line Interface (Click-based)

## Overview

This document defines the command-line interface contract for the Slogan Writer-Reviewer agent system. All commands follow Click framework conventions.

## Base Command

### `slogan-gen`

Root command group for the slogan generation system.

**Usage**:

```bash
slogan-gen [OPTIONS] COMMAND [ARGS]...
```

**Options**:

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--version` | flag | Show version and exit | - |
| `--help` | flag | Show help message | - |

**Example**:

```bash
$ slogan-gen --version
slogan-gen version 0.1.0

$ slogan-gen --help
Usage: slogan-gen [OPTIONS] COMMAND [ARGS]...

  Slogan Writer-Reviewer Agent System
  
  Multi-agent CLI for generating creative slogans through
  iterative collaboration between Writer and Reviewer agents.

Commands:
  generate  Generate a slogan through agent collaboration
  config    Manage configuration settings
  models    List available Ollama models
```

## Commands

### 1. `generate` - Generate Slogan (P1 - Core Functionality)

Generate a slogan through iterative Writer-Reviewer collaboration.

**Usage**:

```bash
slogan-gen generate [OPTIONS] INPUT
```

**Arguments**:

| Argument | Type | Description | Required |
|----------|------|-------------|----------|
| `INPUT` | text | Product/topic description for slogan | Yes |

**Options**:

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--model`, `-m` | text | Ollama model name | `llama2` |
| `--verbose`, `-v` | flag | Show iteration details | Off |
| `--max-turns` | int | Maximum iteration turns (1-10) | 5 |
| `--output`, `-o` | path | Save result to file | stdout |

**Exit Codes**:

| Code | Meaning |
|------|---------|
| 0 | Success - slogan generated |
| 1 | General error (Ollama not available, etc.) |
| 2 | Invalid input (empty or too long) |
| 3 | Configuration error |

**Output Format (Non-verbose)**:

```text
✨ Final Slogan ✨

[Generated slogan here]

---
Generated in 3 turns using llama2
Reviewer status: Approved
```

**Output Format (Verbose)**:

```text
🚀 Starting slogan generation for: "eco-friendly water bottle"
Model: llama2 | Max turns: 5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Turn 1/5
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✏️  Writer:
   "Hydrate Green, Live Clean"

💬 Reviewer:
   Good start! The environmental message is clear, but the brief mentioned 
   making it "fun to use." Let's add more energy and playfulness to capture 
   that aspect.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Turn 2/5
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✏️  Writer:
   "Sip Smart, Play Green!"

💬 Reviewer:
   SHIP IT! 🎉 Perfect! You've nailed the balance between the eco-friendly 
   message and the fun, energetic vibe. "Sip Smart" is catchy and "Play Green" 
   adds that playful element. Well done!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ Final Slogan ✨

"Sip Smart, Play Green!"

---
Generated in 2 turns using llama2
Reviewer status: Approved ✅
Total time: 45 seconds
```

**Error Examples**:

```bash
# Empty input
$ slogan-gen generate ""
Error: INPUT argument is required and cannot be empty.

# Ollama not running
$ slogan-gen generate "eco bottle"
❌ Error: Cannot connect to Ollama at http://localhost:11434

Please ensure Ollama is running:
  1. Install Ollama: https://ollama.ai
  2. Start service: ollama serve
  3. Pull a model: ollama pull llama2

# Invalid model
$ slogan-gen generate "eco bottle" --model unknown-model
❌ Error: Model 'unknown-model' not found

Available models:
  - llama2
  - mistral
  - codellama

Pull a model: ollama pull <model-name>
```

**Examples**:

```bash
# Basic usage
$ slogan-gen generate "affordable electric SUV"

# With specific model
$ slogan-gen generate "coffee shop" --model mistral

# Verbose output
$ slogan-gen generate "fitness app" --verbose

# Save to file
$ slogan-gen generate "tech startup" --output result.txt

# Custom max turns
$ slogan-gen generate "pizza restaurant" --max-turns 3
```

### 2. `config` - Configuration Management (P3 - Configuration)

View and update configuration settings.

**Usage**:

```bash
slogan-gen config [OPTIONS] [COMMAND]
```

**Subcommands**:

#### `config show`

Display current configuration.

```bash
$ slogan-gen config show
Current Configuration:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ollama URL:      http://localhost:11434/v1
Default Model:   llama2
Max Turns:       5
Temperature:     0.7
Timeout:         120s
```

#### `config set`

Update configuration value.

```bash
slogan-gen config set [OPTIONS] KEY VALUE
```

**Arguments**:

| Argument | Description | Valid Values |
|----------|-------------|--------------|
| KEY | Configuration key | `model`, `max-turns`, `temperature`, `timeout`, `url` |
| VALUE | New value | Depends on key |

**Examples**:

```bash
$ slogan-gen config set model mistral
✅ Configuration updated: model = mistral

$ slogan-gen config set max-turns 7
✅ Configuration updated: max-turns = 7

$ slogan-gen config set temperature 0.9
✅ Configuration updated: temperature = 0.9
```

### 3. `models` - List Ollama Models (P3 - Configuration)

List available Ollama models installed locally.

**Usage**:

```bash
slogan-gen models [OPTIONS]
```

**Options**:

| Option | Type | Description |
|--------|------|-------------|
| `--refresh` | flag | Query Ollama for latest models |

**Output Format**:

```text
Available Ollama Models:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ llama2               (default)
  Size: 3.8 GB
  Modified: 2 days ago

✓ mistral
  Size: 4.1 GB
  Modified: 1 week ago

✓ codellama
  Size: 3.8 GB
  Modified: 3 weeks ago

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 3 models | Disk usage: 11.7 GB

To pull a new model:
  ollama pull <model-name>
```

**Error Handling**:

```bash
$ slogan-gen models
❌ Error: Cannot connect to Ollama

Ollama service is not running. Start it with:
  ollama serve
```

**Example**:

```bash
$ slogan-gen models
$ slogan-gen models --refresh
```

## Environment Variables

Configuration can be overridden via environment variables with `SLOGAN_` prefix:

| Variable | Description | Default |
|----------|-------------|---------|
| `SLOGAN_BASE_URL` | Ollama API endpoint | `http://localhost:11434/v1` |
| `SLOGAN_MODEL_NAME` | Default Ollama model | `llama2` |
| `SLOGAN_MAX_ITERATIONS` | Maximum turns | `5` |
| `SLOGAN_TEMPERATURE` | Model temperature | `0.7` |
| `SLOGAN_TIMEOUT` | Request timeout (sec) | `120` |

**Example**:

```bash
export SLOGAN_MODEL_NAME=mistral
export SLOGAN_MAX_ITERATIONS=7
slogan-gen generate "tech startup"
```

## Output Styling

The CLI uses Click's styling for rich terminal output:

| Style | Usage |
|-------|-------|
| ✨ Bright/Bold | Final output, success messages |
| ✏️ Blue | Writer agent output |
| 💬 Yellow | Reviewer agent output |
| ✅ Green | Success indicators |
| ❌ Red | Error messages |
| 🚀 Cyan | Process indicators |
| `━━━` Gray | Section dividers |

## Return Data Structures (Internal)

While CLI outputs text, internal functions return structured data:

### GenerationResult

```python
@dataclass
class GenerationResult:
    """Result from slogan generation."""
    slogan: str
    turns_taken: int
    approved: bool
    completion_reason: str
    duration_seconds: float
    model_used: str
    session: IterationSession
```

### ConfigData

```python
@dataclass
class ConfigData:
    """Configuration data."""
    base_url: str
    model_name: str
    max_iterations: int
    temperature: float
    timeout: int
```

## Testing Contract

All CLI commands must be testable using Click's `CliRunner`:

```python
from click.testing import CliRunner

def test_generate_command():
    runner = CliRunner()
    result = runner.invoke(generate, ['test input'])
    assert result.exit_code == 0
    assert 'Final Slogan' in result.output
```

## API Extensibility (Future)

The CLI layer is designed to share business logic with future FastAPI layer:

```text
┌──────────────┐     ┌──────────────┐
│     CLI      │     │   FastAPI    │  (future)
│  (Click)     │     │  (REST API)  │
└──────┬───────┘     └──────┬───────┘
       │                    │
       └────────┬───────────┘
                │
       ┌────────▼────────┐
       │  Orchestration  │
       │    (Shared)     │
       └────────┬────────┘
                │
       ┌────────▼────────┐
       │     Agents      │
       │    (Shared)     │
       └─────────────────┘
```

Both interfaces will call the same `SloganOrchestrator` class, ensuring business logic consistency.

## Summary

The CLI interface provides:

- **P1**: Core `generate` command with basic output
- **P2**: Verbose mode with turn-by-turn visibility
- **P3**: Configuration and model management

All commands follow Click conventions, provide helpful error messages, and maintain the simplicity principle while enabling rich user experience.
