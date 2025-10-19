# Phase 0: Research - Slogan Writer-Reviewer Agent System

**Feature**: 001-slogan-writer-reviewer  
**Date**: 2025-10-19  
**Status**: Complete

## Research Overview

This document consolidates research findings for implementing a multi-agent slogan generation system using Microsoft Agent Framework with Ollama local models.

## 1. Microsoft Agent Framework with Ollama Integration

### Decision: Use OpenAIChatClient with Ollama's OpenAI-compatible API

**Rationale**:

- Microsoft Agent Framework's `OpenAIChatClient` supports custom `base_url` parameter
- Ollama provides OpenAI-compatible API endpoint at `http://localhost:11434/v1`
- This approach leverages existing Agent Framework patterns without custom client implementation
- Maintains compatibility with framework's multi-agent orchestration features

**Implementation Pattern**:

```python
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

# Configure client to use Ollama's OpenAI-compatible endpoint
client = OpenAIChatClient(
    base_url="http://localhost:11434/v1",
    api_key="dummy-key"  # Ollama doesn't require real API key
)

writer_agent = ChatAgent(
    chat_client=client,
    name="Writer",
    instructions="You are a creative slogan writer..."
)
```

**Alternatives Considered**:

1. **Custom Ollama client implementation** - Rejected: Over-engineering; OpenAI-compatible API provides all needed functionality
2. **Direct Ollama Python SDK** - Rejected: Would require custom integration with Agent Framework's chat client interface
3. **LangChain with Ollama** - Rejected: Adds unnecessary abstraction layer; spec requires Microsoft Agent Framework

### Configuration Management

**Decision**: Use Pydantic Settings for Ollama configuration

**Rationale**:

- Type-safe configuration with validation
- Environment variable support for different environments
- Clear defaults for user experience
- Aligns with simplicity principle (no complex config framework)

**Configuration Fields**:

```python
from pydantic_settings import BaseSettings

class OllamaSettings(BaseSettings):
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model: str = "llama2"  # Default model
    max_iterations: int = 5
    
    class Config:
        env_prefix = "SLOGAN_"  # Enables SLOGAN_OLLAMA_MODEL override
```

## 2. Multi-Agent Workflow Orchestration

### Decision: Sequential Workflow with WorkflowBuilder

**Rationale**:

- Agent Framework's `WorkflowBuilder` provides graph-based workflow construction
- Sequential pattern (Writer → Reviewer → Writer) naturally fits the iterative feedback loop
- Built-in support for conditional edges (approval detection)
- Maintains simplicity while enabling observable agent interactions

**Workflow Pattern**:

```python
from agent_framework import WorkflowBuilder, AgentExecutor

# Build workflow: writer -> reviewer -> conditional loop
workflow = (WorkflowBuilder()
    .set_start_executor(writer_executor)
    .add_edge(writer_executor, reviewer_executor)
    .add_edge(reviewer_executor, writer_executor, condition=should_continue_iteration)
    .build())
```

**Iteration Control**:

- Track turn count in workflow context
- Terminate on "SHIP IT!" detection in reviewer response
- Terminate on max 5 turns reached
- Return final slogan with iteration metadata

**Alternatives Considered**:

1. **Manual async coordination** - Rejected: Loses framework's observability and event handling
2. **State machine library** - Rejected: Over-engineering for simple sequential flow
3. **Direct agent.run() calls in loop** - Rejected: Harder to track and visualize agent interactions

## 3. CLI Design with Click

### Decision: Click-based CLI with async support

**Rationale**:

- Click provides clean, declarative command interface
- Good integration with async functions via `asyncio.run()`
- Built-in help generation and parameter validation
- Widely used, well-documented, aligns with simplicity principle

**CLI Structure**:

```python
import click
import asyncio

@click.group()
def cli():
    """Slogan Writer-Reviewer Agent System"""
    pass

@cli.command()
@click.argument('input_text')
@click.option('--model', default='llama2', help='Ollama model to use')
@click.option('--verbose', is_flag=True, help='Show iteration details')
def generate(input_text: str, model: str, verbose: bool):
    """Generate a slogan through iterative agent collaboration."""
    result = asyncio.run(run_slogan_generation(input_text, model, verbose))
    click.echo(result)
```

**Output Formatting**:

- P1 (Basic): Final slogan only
- P2 (Verbose): Turn-by-turn display with colors (using Click's styling)
- P3 (Config): Model selection via --model flag

**Alternatives Considered**:

1. **argparse** - Rejected: More verbose, less modern than Click
2. **Typer** - Rejected: Good but adds dependency; Click sufficient for needs
3. **Custom CLI parser** - Rejected: Violates simplicity principle

## 4. Testing Strategy

### Decision: pytest with pytest-asyncio for async agent testing

**Rationale**:

- pytest is Python standard for testing
- pytest-asyncio handles async test functions cleanly
- Mocking Ollama responses enables fast unit tests
- Integration tests verify full workflow

**Test Layers**:

1. **Unit Tests**:
   - Agent instruction prompts
   - Workflow condition logic (approval detection)
   - CLI command parsing and output formatting
   
2. **Integration Tests**:
   - End-to-end workflow with mocked Ollama responses
   - Verify iteration count tracking
   - Verify approval termination
   - Verify max turns termination

**Mocking Strategy**:

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_reviewer_approves_slogan():
    with patch('agent_framework.openai.OpenAIChatClient') as mock_client:
        mock_client.get_response.return_value = AsyncMock(
            messages=[ChatMessage(text="SHIP IT! This slogan is perfect.")]
        )
        # Test approval detection logic
```

**Alternatives Considered**:

1. **unittest** - Rejected: pytest more feature-rich and concise
2. **VCR.py for recording real responses** - Deferred: Good for future but adds complexity for MVP
3. **Manual test scripts** - Rejected: Not maintainable, violates code quality principle

## 5. Approval Detection Logic

### Decision: Simple string contains check for "SHIP IT!"

**Rationale**:

- Spec explicitly defines approval as containing "SHIP IT!"
- Case-insensitive check for robustness
- No complex NLP needed for clear signal
- Can be enhanced later if needed

**Implementation**:

```python
def is_approved(reviewer_response: str) -> bool:
    """Check if reviewer approved the slogan."""
    return "ship it" in reviewer_response.lower()
```

**Edge Cases Handled**:

- Case variations ("SHIP IT", "Ship it!", "ship it")
- Embedded in sentence ("I think we should SHIP IT!")
- Whitespace variations

**Alternatives Considered**:

1. **Exact match** - Rejected: Too brittle given LLM output variability
2. **Regex pattern** - Rejected: Over-engineering for simple substring check
3. **Sentiment analysis** - Rejected: Unnecessary complexity; spec is explicit about signal

## 6. Error Handling Strategy

### Decision: Graceful degradation with clear error messages

**Error Scenarios**:

1. **Ollama not running**: Check connection on startup, provide setup instructions
2. **Model not available**: List available models, suggest `ollama pull <model>`
3. **Empty user input**: Validate before starting workflow
4. **Max turns without approval**: Return last slogan with warning message

**User Experience**:

```text
❌ Error: Cannot connect to Ollama at http://localhost:11434
   
   Please ensure Ollama is running:
   1. Install Ollama: https://ollama.ai
   2. Start Ollama service: ollama serve
   3. Pull a model: ollama pull llama2
```

**Alternatives Considered**:

1. **Silent failures** - Rejected: Violates code quality principle (clear communication)
2. **Auto-start Ollama** - Rejected: Over-engineering; user should control services
3. **Retry logic** - Deferred: Good for future but adds complexity for MVP

## 7. Future FastAPI Extension Architecture

### Decision: Layer separation for API reusability

**Architecture Layers**:

1. **Core Layer** (`src/agents`, `src/orchestration`): Pure business logic, no CLI/API dependencies
2. **Interface Layer** (`src/cli`, future `src/api`): UI-specific logic

**Future API Structure**:

```text
src/
├── agents/          # Shared
├── orchestration/   # Shared
├── cli/             # CLI-specific
└── api/             # Future: FastAPI endpoints
    ├── routes.py
    ├── schemas.py
    └── dependencies.py
```

**Benefits**:

- Core logic reusable across CLI and API
- Easy to add API layer without refactoring agents
- Maintains simplicity for current MVP
- Aligns with incremental development principle

## Research Completion Checklist

- [x] Microsoft Agent Framework integration pattern with Ollama
- [x] Multi-agent workflow orchestration approach
- [x] CLI framework selection and design
- [x] Testing strategy and tools
- [x] Approval detection logic
- [x] Error handling approach
- [x] Future API extensibility architecture

**Status**: All research complete. Ready for Phase 1 (Design & Contracts).
