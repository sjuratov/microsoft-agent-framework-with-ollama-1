# CLI Usage Guide

Complete reference for using the Slogan Writer-Reviewer Agent System command-line interface.

## Overview

The CLI provides an intuitive interface for generating slogans through multi-agent collaboration. All commands are accessed through the `slogan-gen` command.

```bash
slogan-gen --help
```

## Command Structure

```bash
slogan-gen [COMMAND] [OPTIONS] [ARGUMENTS]
```

**Available Commands:**

| Command | Description |
|---------|-------------|
| `generate` | Generate a slogan (main command) |
| `models` | List available Ollama models |
| `config show` | Display current configuration |
| `config set` | Set configuration values |

---

## Generate Command

Generate creative slogans through Writer-Reviewer collaboration.

### Basic Syntax

```bash
slogan-gen generate "your product or service description"
```

### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--model` | | string | `mistral:latest` | Ollama model to use |
| `--max-turns` | | integer | 5 | Maximum iteration turns (1-10) |
| `--verbose` | `-v` | flag | false | Show detailed iteration history |
| `--output` | `-o` | path | | Save results to file (.txt or .json) |

### Examples

#### Basic Generation

```bash
slogan-gen generate "eco-friendly water bottle"
```

**Output:**
```
🚀 Generating slogan for: eco-friendly water bottle
   Using model: mistral:latest

✅ Final Slogan:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   💧 Pure Hydration, Zero Waste!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Approved by Reviewer in 2 turns
⏱️  Total duration: 5.8 seconds
```

#### Verbose Mode

See the complete Writer-Reviewer collaboration process:

```bash
slogan-gen generate "tech startup" --verbose
```

**Output:**
```
🚀 Generating slogan for: tech startup
   Using model: mistral:latest

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Turn 1/5
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Writer's Slogan:
   Innovation at the Speed of Tomorrow

💭 Reviewer's Feedback:
   Good foundation, but it's too generic. Can we make it more
   specific to what the startup does? Add more impact.

Duration: 2.3s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Turn 2/5
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Writer's Slogan:
   🚀 Building Tomorrow's Tech, Today!

💭 Reviewer's Feedback:
   SHIP IT! Perfect combination of emoji, energy, and clarity!

Duration: 2.8s

✅ Final Slogan:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   🚀 Building Tomorrow's Tech, Today!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Approved by Reviewer in 2 turns
⏱️  Total duration: 5.1 seconds (avg 2.6s per turn)
```

#### Custom Model

Use a different Ollama model:

```bash
# Fast generation with smaller model
slogan-gen generate "coffee shop" --model gemma2:2b

# High quality with larger model
slogan-gen generate "coffee shop" --model llama3.2:latest
```

#### Custom Iteration Limit

Control how many refinement turns are allowed:

```bash
# Quick generation (3 turns max)
slogan-gen generate "fitness app" --max-turns 3

# Extensive refinement (10 turns max)
slogan-gen generate "luxury brand" --max-turns 10
```

#### Save to File

**Text Format:**

```bash
slogan-gen generate "pizza restaurant" --output result.txt
```

Creates `result.txt` with the formatted output.

**JSON Format:**

```bash
slogan-gen generate "pizza restaurant" --output result.json
```

Creates `result.json`:

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
      "duration_seconds": 2.9,
      "timestamp": "2024-01-15T10:30:00"
    },
    {
      "turn_number": 2,
      "slogan": "🍕 Slice of Heaven, Every Bite!",
      "feedback": "SHIP IT! Perfect combination of emoji and excitement.",
      "approved": true,
      "duration_seconds": 2.9,
      "timestamp": "2024-01-15T10:30:05"
    }
  ]
}
```

#### Combined Options

```bash
slogan-gen generate "AI assistant" \
  --model mistral:latest \
  --max-turns 7 \
  --verbose \
  --output results.json
```

---

## Models Command

List and manage available Ollama models.

### Basic Syntax

```bash
slogan-gen models
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--refresh` | `-r` | Force refresh the model list |

### Examples

**List Models:**

```bash
slogan-gen models
```

**Output:**
```
📦 Available Ollama Models:

  1. gemma2:2b
  2. llama3.2:latest
  3. mistral:latest (default)
  4. phi3:mini

✓ Total: 4 models

💡 Use with: slogan-gen generate "your input" --model <model-name>
```

**Refresh Model List:**

```bash
slogan-gen models --refresh
```

---

## Config Commands

View and modify configuration settings.

### Config Show

Display current configuration values.

```bash
slogan-gen config show
```

**Output:**
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

💡 To modify settings, set environment variables:
   Example: export OLLAMA_MODEL_NAME=mistral:latest
   Or create a .env file in your project directory
```

### Config Set

Set configuration values (temporary, for current session).

#### Syntax

```bash
slogan-gen config set KEY VALUE
```

#### Supported Keys

| Key | Environment Variable | Example Value |
|-----|---------------------|---------------|
| `MODEL_NAME` / `MODEL` | `OLLAMA_MODEL_NAME` | `mistral:latest` |
| `BASE_URL` / `URL` | `OLLAMA_BASE_URL` | `http://localhost:11434` |
| `TEMPERATURE` / `TEMP` | `OLLAMA_TEMPERATURE` | `0.8` |
| `MAX_TOKENS` / `TOKENS` | `OLLAMA_MAX_TOKENS` | `1000` |
| `TIMEOUT` | `OLLAMA_TIMEOUT` | `60` |
| `MAX_TURNS` / `TURNS` | `OLLAMA_MAX_TURNS` | `7` |

#### Examples

**Change Model:**

```bash
slogan-gen config set MODEL mistral:latest
```

**Adjust Temperature:**

```bash
slogan-gen config set TEMPERATURE 0.9
```

**Increase Timeout:**

```bash
slogan-gen config set TIMEOUT 60
```

!!! note "Temporary Changes"
    Changes made with `config set` are temporary and only affect the current session. For persistent changes, add to your `.env` file or shell profile.

---

## Input Guidelines

### Best Practices

✅ **Good Inputs:**
- Specific and descriptive
- Include target audience if relevant
- Mention key features or benefits

```bash
slogan-gen generate "premium organic coffee roastery targeting health-conscious millennials"
slogan-gen generate "eco-friendly cleaning products for environmentally conscious homeowners"
slogan-gen generate "AI-powered project management tool for remote teams"
```

❌ **Avoid:**
- Single generic words
- Extremely long inputs (>200 characters)
- Empty or whitespace-only inputs

```bash
# Too vague
slogan-gen generate "business"

# Too long (>200 chars will be rejected)
slogan-gen generate "a very long description that goes on and on..."
```

### Input Length

- **Minimum**: 3 characters
- **Maximum**: 200 characters
- **Recommended**: 10-50 characters for best results

---

## Output Formats

### Text Output (Default)

Human-readable format with colors and formatting:

```
✅ Final Slogan:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Your Generated Slogan Here!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Approved by Reviewer in 3 turns
⏱️  Total duration: 8.2 seconds
```

### JSON Output

Machine-readable format for programmatic use:

```json
{
  "input": "string",
  "final_slogan": "string",
  "completion_reason": "approved|max_turns_reached",
  "turn_count": 0,
  "max_turns": 5,
  "total_duration_seconds": 0.0,
  "average_duration_per_turn": 0.0,
  "turns": [
    {
      "turn_number": 1,
      "slogan": "string",
      "feedback": "string",
      "approved": false,
      "duration_seconds": 0.0,
      "timestamp": "2024-01-15T10:30:00"
    }
  ]
}
```

---

## Performance Considerations

### Model Selection

Choose models based on your needs:

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| `gemma2:2b` | 2B | ⚡⚡⚡ | ⭐⭐ | Quick testing |
| `phi3:mini` | 3.8B | ⚡⚡ | ⭐⭐⭐ | Development |
| `mistral:latest` | 7B | ⚡ | ⭐⭐⭐⭐ | Production (default) |
| `llama3.2:latest` | 8B | 🐌 | ⭐⭐⭐⭐⭐ | High quality |

### Timing Expectations

**Typical generation times** (2 turns, CPU-only):

- **2B models**: 5-10 seconds
- **7B models**: 15-30 seconds
- **8B+ models**: 60-120 seconds

**With GPU acceleration**, times are significantly faster.

### Optimization Tips

1. **Use smaller models for testing**: `gemma2:2b` or `phi3:mini`
2. **Reduce max turns**: `--max-turns 3` for quick results
3. **Ensure Ollama uses GPU**: Check `ollama serve` output
4. **Close other applications**: Free up system resources

---

## Error Handling

### Common Errors

**Empty Input:**
```
❌ Error: Input cannot be empty
```

**Model Not Found:**
```
⚠️  Warning: Model 'unknown' not found in available models.

Available models: gemma2:2b, mistral:latest, phi3:mini

Continue anyway? [y/N]: n

💡 To install the model, run: ollama pull unknown
```

**Connection Error:**
```
❌ Connection Error: Cannot connect to Ollama at http://localhost:11434

💡 Tips:
   • Ensure Ollama is running: ollama serve
   • Check if the model is available: ollama list
   • Pull the model if needed: ollama pull mistral:latest
```

**Validation Error:**
```
❌ Validation Error: 2 validation errors for Turn
slogan: String should have at most 500 characters
feedback: String should have at most 1000 characters
```

Solution: Use a larger, more capable model (see [Troubleshooting Guide](../troubleshooting.md#model-validation-errors-string-too-long))

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (validation, connection, runtime, etc.) |

---

## Tips & Best Practices

### 1. Start with Verbose Mode

When learning the system, use `--verbose` to understand the collaboration process:

```bash
slogan-gen generate "your input" --verbose
```

### 2. Experiment with Models

Try different models to find the best balance of speed and quality for your use case:

```bash
slogan-gen generate "test" --model gemma2:2b     # Fast
slogan-gen generate "test" --model mistral       # Balanced
slogan-gen generate "test" --model llama3.2      # Quality
```

### 3. Adjust Iterations Based on Quality

- **Quick brainstorming**: `--max-turns 3`
- **Standard generation**: Default (5 turns)
- **High-quality output**: `--max-turns 7` or more

### 4. Save Important Results

Always save results you want to keep:

```bash
slogan-gen generate "product" --output results/product-slogan.json
```

### 5. Use Shell Aliases

Create shortcuts for common tasks:

```bash
# Add to ~/.zshrc or ~/.bashrc
alias slogan='slogan-gen generate'
alias slogan-fast='slogan-gen generate --model gemma2:2b --max-turns 3'
alias slogan-quality='slogan-gen generate --model llama3.2 --max-turns 7 --verbose'

# Usage
slogan "coffee shop"
slogan-fast "quick test"
slogan-quality "luxury brand"
```

### 6. Batch Processing

Generate multiple slogans using a shell loop:

```bash
# Using a file with inputs
while read -r line; do
  slogan-gen generate "$line" --output "results/${line// /_}.json"
done < inputs.txt
```

### 7. Monitor Performance

Use verbose mode to track timing:

```bash
slogan-gen generate "test" --verbose | grep "Duration:"
```

---

## Integration Examples

### Shell Scripts

```bash
#!/bin/bash
# generate_slogan.sh

INPUT="$1"
OUTPUT="${2:-slogan.json}"
MODEL="${3:-mistral:latest}"

slogan-gen generate "$INPUT" \
  --model "$MODEL" \
  --max-turns 5 \
  --output "$OUTPUT"

echo "Slogan saved to $OUTPUT"
```

Usage:
```bash
./generate_slogan.sh "coffee shop" "results/coffee.json" "mistral:latest"
```

### Python Integration

```python
import subprocess
import json

def generate_slogan(input_text: str, model: str = "mistral:latest") -> dict:
    """Generate slogan using CLI."""
    result = subprocess.run(
        ["slogan-gen", "generate", input_text, "--model", model, "--output", "-"],
        capture_output=True,
        text=True,
        check=True
    )
    return json.loads(result.stdout)

# Usage
slogan_data = generate_slogan("eco-friendly water bottle")
print(slogan_data["final_slogan"])
```

---

## See Also

- [Quick Start Guide](../getting-started/quickstart.md) - First-time usage tutorial
- [Configuration Guide](../getting-started/configuration.md) - Detailed configuration options
- [API Usage Guide](api-usage.md) - REST API alternative
- [Troubleshooting Guide](../troubleshooting.md) - Common issues and solutions
