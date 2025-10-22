# Quick Start

Get up and running with the Slogan Writer-Reviewer Agent System in minutes!

## Prerequisites

Make sure you've completed the [Installation Guide](installation.md) before proceeding.

## Your First Slogan

Generate a slogan with a single command:

```bash
slogan-gen generate "eco-friendly water bottle"
```

**Expected Output:**

```
🎯 Generating slogan for: eco-friendly water bottle

🎨 Writer-Reviewer Collaboration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Final Slogan (Turn 2/5):
💧 Hydrate Sustainably, Live Responsibly

✓ Approved by Reviewer
⏱️  Total Duration: 8.2 seconds
```

Congratulations! You've generated your first slogan! 🎉

## See the Collaboration Process

Use `--verbose` mode to watch the Writer and Reviewer agents collaborate:

```bash
slogan-gen generate "tech startup" --verbose
```

**Example Output:**

```
🎯 Generating slogan for: tech startup

🎨 Writer-Reviewer Collaboration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─ Turn 1 ─────────────────────────────────┐
│ 📝 Writer:                               │
│ "Innovate Today, Transform Tomorrow"    │
│                                          │
│ 💬 Reviewer Feedback:                    │
│ "Good start, but feels generic. Add     │
│ more specificity about the tech         │
│ industry. Consider making it punchier." │
│                                          │
│ ⏱️  Duration: 4.1s                       │
└──────────────────────────────────────────┘

┌─ Turn 2 ─────────────────────────────────┐
│ 📝 Writer:                               │
│ "🚀 Code the Future, Ship the Possible" │
│                                          │
│ 💬 Reviewer Feedback:                    │
│ "SHIP IT! Perfect combination of tech   │
│ imagery and aspirational messaging."     │
│                                          │
│ ✅ APPROVED                              │
│ ⏱️  Duration: 3.8s                       │
└──────────────────────────────────────────┘

✅ Final Slogan (Turn 2/5):
🚀 Code the Future, Ship the Possible

✓ Approved by Reviewer
⏱️  Total Duration: 7.9 seconds
```

## Common Usage Patterns

### Use a Different Model

Try different AI models for varied styles:

```bash
# Fast and efficient
slogan-gen generate "coffee shop" --model gemma2:2b

# Default balanced model
slogan-gen generate "coffee shop" --model mistral

# High quality output
slogan-gen generate "coffee shop" --model llama3.2
```

### Limit Iterations

Control how many revision rounds are allowed:

```bash
# Quick generation (1-3 turns recommended)
slogan-gen generate "fitness app" --max-turns 3

# More iterations for quality (default is 5)
slogan-gen generate "luxury hotel" --max-turns 7
```

### Save Output to File

Save slogans for later use:

```bash
# Save as plain text
slogan-gen generate "pizza restaurant" --output slogan.txt

# Save as JSON for programmatic use
slogan-gen generate "pizza restaurant" --output result.json
```

**JSON Output Example:**

```json
{
  "input": "pizza restaurant",
  "final_slogan": "🍕 Slice of Heaven, Every Bite!",
  "completion_reason": "approved",
  "turn_count": 2,
  "max_turns": 5,
  "total_duration_seconds": 5.8,
  "average_duration_per_turn": 2.9,
  "model_used": "mistral:latest",
  "turns": [
    {
      "turn_number": 1,
      "slogan": "Pizza Perfection in Every Slice",
      "feedback": "Good start, but needs more excitement and memorability.",
      "approved": false,
      "timestamp": "2024-01-15T10:30:00Z",
      "duration_seconds": 3.1
    },
    {
      "turn_number": 2,
      "slogan": "🍕 Slice of Heaven, Every Bite!",
      "feedback": "SHIP IT! Perfect combination of emoji and excitement.",
      "approved": true,
      "timestamp": "2024-01-15T10:30:05Z",
      "duration_seconds": 2.7
    }
  ]
}
```

## Tips for Better Slogans

### Be Specific

❌ **Vague**: `slogan-gen generate "business"`

✅ **Specific**: `slogan-gen generate "eco-friendly cleaning products for homes"`

### Provide Context

Include details about your target audience or unique value:

```bash
slogan-gen generate "mobile app for busy parents to organize family schedules"
```

### Experiment with Models

Different models have different creative styles:

- **gemma2:2b**: Quick, straightforward slogans
- **mistral**: Balanced creativity and professionalism
- **llama3.2**: More nuanced, literary style
- **phi3:mini**: Technical and precise

### Use Verbose Mode for Insights

Watch how the agents collaborate to understand what makes a good slogan:

```bash
slogan-gen generate "your product" --verbose
```

## Configuration

Check your current settings:

```bash
slogan-gen config show
```

List available models:

```bash
slogan-gen models
```

## Example Workflows

### Quick Brainstorming Session

Generate multiple slogans quickly:

```bash
slogan-gen generate "coffee shop" --model gemma2:2b --max-turns 3 --output coffee1.txt
slogan-gen generate "artisan coffee with local beans" --model gemma2:2b --max-turns 3 --output coffee2.txt
slogan-gen generate "cozy neighborhood café" --model gemma2:2b --max-turns 3 --output coffee3.txt
```

### High-Quality Final Slogan

Take time for a polished result:

```bash
slogan-gen generate "premium organic coffee roastery" \
  --model llama3.2 \
  --max-turns 7 \
  --verbose \
  --output final-slogan.json
```

### Batch Processing

Process multiple inputs from a file:

```bash
# Create input file
cat > inputs.txt << EOF
eco-friendly water bottle
tech startup
coffee shop
fitness app
EOF

# Process each line
while read line; do
  slogan-gen generate "$line" --output "slogan-$(echo $line | tr ' ' '-').txt"
done < inputs.txt
```

## What's Next?

- [Configuration Guide](configuration.md) - Customize default settings
- [CLI Usage](../guides/cli-usage.md) - Complete command reference
- [API Usage](../guides/api-usage.md) - Integrate with REST API
- [Troubleshooting](../troubleshooting.md) - Common issues and solutions

## Common Issues

### Slow Generation

If generation takes too long, try:

1. Use a smaller model: `--model gemma2:2b`
2. Reduce iterations: `--max-turns 3`
3. Check system resources (close other apps)

See [Troubleshooting](../troubleshooting.md) for more solutions.

### Quality Issues with Small Models

If slogans are poor quality:

1. Switch to a larger model: `--model mistral`
2. Increase iterations: `--max-turns 7`
3. Provide more specific input

### Connection Errors

If you get connection errors:

```bash
# Ensure Ollama is running
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```
