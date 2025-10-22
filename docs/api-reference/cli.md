# CLI API Reference

# CLI API Reference

This page documents the CLI implementation for the Slogan Writer-Reviewer system.

## Overview

The CLI provides a user-friendly command-line interface built with [Click](https://click.palletsprojects.com/). It includes commands for generating slogans, managing models, and configuring settings.

## Main Entry Point

::: src.cli.main.cli
    options:
      show_source: true
      heading_level: 3

The main CLI group that serves as the entry point for all commands.

---

## Commands

### generate

::: src.cli.main.generate
    options:
      show_source: true
      heading_level: 4

**Purpose**: Generate creative slogans through Writer-Reviewer collaboration.

**Usage**:

```bash
slogan-gen generate "eco-friendly water bottle"
slogan-gen generate "AI assistant" --model mistral:latest --max-turns 7 --verbose
slogan-gen generate "coffee shop" --output result.json
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--model` | string | `mistral:latest` | Ollama model to use |
| `--max-turns` | integer | 5 | Maximum iteration turns (1-10) |
| `--verbose` / `-v` | flag | false | Show detailed iteration history |
| `--output` / `-o` | path | | Save results to file (.txt or .json) |

---

### models

::: src.cli.main.models
    options:
      show_source: true
      heading_level: 4

**Purpose**: List available Ollama models.

**Usage**:

```bash
slogan-gen models
slogan-gen models --refresh
```

**Options**:

| Option | Description |
|--------|-------------|
| `--refresh` / `-r` | Force refresh the model list from Ollama |

---

### config (group)

::: src.cli.main.config
    options:
      show_source: true
      heading_level: 4

**Purpose**: Manage configuration settings.

Parent command for configuration subcommands.

---

### config show

::: src.cli.main.config_show
    options:
      show_source: true
      heading_level: 4

**Purpose**: Display current configuration settings.

**Usage**:

```bash
slogan-gen config show
```

**Output**:

```
⚙️  Current Configuration:
============================================================
Ollama Base URL.............. http://localhost:11434
Default Model................ mistral:latest
Temperature.................. 0.7 (range: 0.0-2.0)
Max Tokens................... 500 (range: 1-4096)
Timeout...................... 30s (range: 1-300)
Max Turns.................... 5 (range: 1-10)
============================================================
```

---

### config set

::: src.cli.main.config_set
    options:
      show_source: true
      heading_level: 4

**Purpose**: Set configuration value via environment variable (temporary for current session).

**Usage**:

```bash
slogan-gen config set MODEL_NAME mistral:latest
slogan-gen config set MAX_TURNS 7
slogan-gen config set TEMPERATURE 0.9
```

**Key Mapping**:

| Friendly Key | Environment Variable |
|--------------|---------------------|
| `MODEL_NAME` / `MODEL` | `OLLAMA_MODEL_NAME` |
| `BASE_URL` / `URL` | `OLLAMA_BASE_URL` |
| `TEMPERATURE` / `TEMP` | `OLLAMA_TEMPERATURE` |
| `MAX_TOKENS` / `TOKENS` | `OLLAMA_MAX_TOKENS` |
| `TIMEOUT` | `OLLAMA_TIMEOUT` |
| `MAX_TURNS` / `TURNS` | `OLLAMA_MAX_TURNS` |

---

## Output Formatting

::: src.cli.output.format_session_output
    options:
      show_source: true
      heading_level: 3

**Purpose**: Format IterationSession for CLI output.

**Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `session` | IterationSession | required | The completed session |
| `verbose` | bool | `False` | Include turn-by-turn details |

**Output Modes**:

**Standard Mode** (verbose=False):
```
✅ Final Slogan:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Your Generated Slogan Here!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Approved by Reviewer in 3 turns
⏱️  Total duration: 8.2 seconds
```

**Verbose Mode** (verbose=True):
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Turn 1/5
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Writer's Slogan:
   Initial Slogan Here

💭 Reviewer's Feedback:
   Feedback text here

Duration: 2.3s

[... additional turns ...]

✅ Final Slogan:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Final Approved Slogan
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Approved by Reviewer in 3 turns
⏱️  Total duration: 8.2 seconds (avg 2.7s per turn)
```

**Usage Example**:

```python
from src.cli.output import format_session_output
from src.orchestration import run_slogan_generation

session = await run_slogan_generation("coffee shop")

# Standard output
output = format_session_output(session, verbose=False)
print(output)

# Verbose output
output = format_session_output(session, verbose=True)
print(output)
```

---

## Error Handling

The CLI provides user-friendly error messages for common issues:

### Empty Input

```bash
$ slogan-gen generate ""
❌ Error: Input cannot be empty
```

### Model Not Found

```bash
$ slogan-gen generate "test" --model unknown
⚠️  Warning: Model 'unknown' not found in available models.

Available models: gemma2:2b, mistral:latest, phi3:mini

Continue anyway? [y/N]: n

💡 To install the model, run: ollama pull unknown
```

### Connection Error

```bash
$ slogan-gen generate "test"
❌ Connection Error: Cannot connect to Ollama at http://localhost:11434

💡 Tips:
   • Ensure Ollama is running: ollama serve
   • Check if the model is available: ollama list
   • Pull the model if needed: ollama pull mistral:latest
```

### Validation Error

```bash
$ slogan-gen generate "test" --model gemma2:2b
❌ Validation Error: 2 validation errors for Turn
slogan: String should have at most 500 characters
feedback: String should have at most 1000 characters
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (validation, connection, runtime, etc.) |

---

## Color and Styling

The CLI uses Click's styling features for visual feedback:

| Element | Style | Example |
|---------|-------|---------|
| Success | Green | `✓ Approved by Reviewer` |
| Error | Red | `❌ Error: ...` |
| Warning | Yellow | `⚠️  Warning: ...` |
| Info | Cyan | `🚀 Generating slogan...` |
| Slogan | Bold | Final slogan display |
| Duration | Regular | `⏱️  Total duration: 8.2s` |

---

## Integration Examples

### Shell Script

```bash
#!/bin/bash
# batch_generate.sh

while read -r input; do
  echo "Generating for: $input"
  slogan-gen generate "$input" --output "results/${input// /_}.json"
done < inputs.txt
```

### Python Integration

```python
import subprocess
import json

def generate_via_cli(input_text: str) -> dict:
    """Generate slogan using CLI."""
    result = subprocess.run(
        ["slogan-gen", "generate", input_text, "--output", "-"],
        capture_output=True,
        text=True,
        check=True
    )
    return json.loads(result.stdout)

# Usage
slogan_data = generate_via_cli("coffee shop")
print(slogan_data["final_slogan"])
```

---

## See Also

- [CLI Usage Guide](../guides/cli-usage.md) - Complete CLI user guide
- [Configuration API](config.md) - Configuration management
- [Orchestration API](orchestration.md) - Workflow coordination
- [Troubleshooting Guide](../troubleshooting.md) - Common CLI issues
