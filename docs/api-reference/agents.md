# Agents API Reference

This page documents the agent implementations used in the Slogan Writer-Reviewer system.

## Overview

The system uses two specialized AI agents that collaborate to generate high-quality slogans:

- **Writer Agent**: Generates creative slogans based on user input and incorporates feedback
- **Reviewer Agent**: Evaluates slogans and provides constructive feedback or approval

Both agents are implemented using the [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) and communicate with Ollama for LLM inference.

## Architecture

```
User Input
    ↓
Writer Agent (generates slogan)
    ↓
Reviewer Agent (evaluates)
    ↓
Feedback Loop ←→ Writer Agent (revises)
    ↓
Final Approved Slogan
```

The agents follow a collaborative pattern where:

1. Writer creates an initial slogan
2. Reviewer evaluates and provides feedback
3. Writer incorporates feedback and revises
4. Loop continues until approval or max turns reached

## Writer Agent

::: src.agents.writer.create_writer_agent
    options:
      show_source: true
      heading_level: 3

### Writer System Prompt

The Writer agent is configured with a system prompt that:

- Emphasizes creativity and memorability
- Encourages concise output (under 100 characters)
- Focuses on emotional appeal
- Instructs to incorporate reviewer feedback
- Outputs only the slogan text

**Key Characteristics**:

- **Goal**: Generate catchy, impactful slogans
- **Style**: Creative, concise, emotionally engaging
- **Behavior**: Responds to feedback by revising while maintaining creativity
- **Output**: Pure slogan text only (no explanations)

### Usage Example

```python
from src.agents.writer import create_writer_agent
from src.config import get_ollama_config

# Create writer agent
config = get_ollama_config()
writer = create_writer_agent(config)

# Generate initial slogan
response = await writer.send_message("Create a slogan for: eco-friendly water bottle")
slogan = response.message.content

print(f"Writer: {slogan}")
# Output: "💧 Pure Hydration, Zero Waste!"
```

---

## Reviewer Agent

::: src.agents.reviewer.create_reviewer_agent
    options:
      show_source: true
      heading_level: 3

### Reviewer System Prompt

The Reviewer agent is configured with a system prompt that:

- Evaluates slogans against specific criteria
- Provides constructive, actionable feedback
- Approves only excellent slogans
- Uses "SHIP IT!" for approval
- Never mixes feedback with approval

**Evaluation Criteria**:

1. **Memorability**: Is it catchy and easy to remember?
2. **Clarity**: Does it clearly relate to the product/service?
3. **Conciseness**: Is it impactful and to the point?
4. **Emotional Appeal**: Does it resonate emotionally?
5. **Uniqueness**: Is it creative and original?

**Response Patterns**:

- **Needs Improvement**: Provides specific, actionable feedback only
- **Excellent**: Responds with "SHIP IT!" only (no additional text)
- **Critical Rule**: Never mixes feedback with approval

### Usage Example

```python
from src.agents.reviewer import create_reviewer_agent
from src.config import get_ollama_config

# Create reviewer agent
config = get_ollama_config()
reviewer = create_reviewer_agent(config)

# Evaluate slogan
slogan = "Cloud Storage Solutions"
response = await reviewer.send_message(
    f"Review this slogan for a cloud storage company: {slogan}"
)
feedback = response.message.content

print(f"Reviewer: {feedback}")
# Output: "Too generic. What makes this storage different? Add unique value."

# After revision
improved_slogan = "☁️ Your Files, Anywhere, Instantly"
response = await reviewer.send_message(
    f"Review this slogan: {improved_slogan}"
)
feedback = response.message.content

print(f"Reviewer: {feedback}")
# Output: "SHIP IT!"
```

---

## Agent Configuration

Both agents are configured using `OllamaConfig` which includes:

| Parameter | Type | Description |
|-----------|------|-------------|
| `base_url` | str | Ollama API endpoint (default: http://localhost:11434/v1) |
| `model_name` | str | Model identifier (default: mistral:latest) |
| `temperature` | float | Sampling temperature (default: 0.7) |
| `max_tokens` | int | Maximum response length (default: 500) |
| `timeout` | int | Request timeout in seconds (default: 30) |

### Configuration Example

```python
from src.config import get_ollama_config

# Get default configuration
config = get_ollama_config()

# Or create custom configuration
from src.config.settings import OllamaConfig

custom_config = OllamaConfig(
    base_url="http://localhost:11434/v1",
    model_name="llama3.2:latest",
    temperature=0.8,
    max_tokens=300
)

# Use with agents
writer = create_writer_agent(custom_config)
reviewer = create_reviewer_agent(custom_config)
```

---

## Agent Communication

Agents communicate using the Microsoft Agent Framework's message protocol:

```python
# Send message to agent
response = await agent.send_message(prompt)

# Access response content
content = response.message.content

# Response includes metadata
print(f"Role: {response.message.role}")  # 'assistant'
print(f"Content: {response.message.content}")  # The slogan or feedback
```

---

## Best Practices

### Writer Agent

✅ **Do**:
- Provide specific, detailed product/service descriptions
- Include target audience when relevant
- Give context about brand personality
- Let the writer be creative

❌ **Don't**:
- Give vague, generic inputs like "business" or "app"
- Over-constrain the creative process
- Expect exact character counts (aim for <100 chars)

### Reviewer Agent

✅ **Do**:
- Trust the reviewer's critical evaluation
- Use feedback to improve slogans iteratively
- Expect high standards (only great slogans get "SHIP IT!")

❌ **Don't**:
- Expect approval on first try
- Ignore specific feedback points
- Assume feedback means rejection (it's guidance)

---

## Model Selection

Choose models based on your needs:

| Model | Size | Writer Performance | Reviewer Performance | Best For |
|-------|------|-------------------|---------------------|----------|
| `gemma2:2b` | 2B | Good | Fair | Quick testing |
| `phi3:mini` | 3.8B | Very Good | Good | Development |
| `mistral:latest` | 7B | Excellent | Excellent | Production |
| `llama3.2:latest` | 8B | Excellent | Excellent | High quality |

**Note**: Smaller models (1B-2B) may struggle with the strict output format required by the reviewer and can produce validation errors.

---

## Error Handling

Common agent-related errors:

### Connection Errors

```python
try:
    writer = create_writer_agent(config)
    response = await writer.send_message(prompt)
except Exception as e:
    if "connection" in str(e).lower():
        print("Ollama is not running. Start it with: ollama serve")
    raise
```

### Timeout Errors

```python
from src.config.settings import OllamaConfig

# Increase timeout for slower models
config = OllamaConfig(timeout=60)  # 60 seconds
writer = create_writer_agent(config)
```

### Model Not Found

```bash
# Ensure model is pulled
ollama list
ollama pull mistral:latest
```

---

## See Also

- [Orchestration API](orchestration.md) - Workflow coordination between agents
- [Configuration API](config.md) - Configuration management
- [CLI Usage Guide](../guides/cli-usage.md) - Using agents via CLI
- [Architecture Overview](../architecture/overview.md) - System design
