# Architecture Overview

This document provides a high-level overview of the Slogan Writer-Reviewer system architecture, design decisions, and technology stack.

## System Overview

The Slogan Writer-Reviewer is a **multi-agent collaborative system** that generates creative slogans through iterative Writer-Reviewer interactions. The system leverages the **Microsoft Agent Framework** pattern with **Ollama** for local LLM execution.

### Key Characteristics

- **Multi-Agent Collaboration**: Separate Writer and Reviewer agents with distinct roles
- **Iterative Refinement**: Feedback loop until approval or max iterations
- **Local-First**: Runs entirely on local infrastructure (no cloud dependencies)
- **Multi-Interface**: Supports both CLI and REST API interfaces
- **Type-Safe**: Fully typed Python codebase with Pydantic validation
- **Production-Ready**: Comprehensive error handling, logging, and testing

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interfaces                          │
├───────────────────────────────┬─────────────────────────────────┤
│         CLI (Click)           │      REST API (FastAPI)         │
│   • slogan-gen generate       │   • POST /slogans/generate      │
│   • slogan-gen models         │   • GET /models                 │
│   • slogan-gen config         │   • GET /health                 │
└───────────────┬───────────────┴──────────────┬──────────────────┘
                │                              │
                └──────────────┬───────────────┘
                               │
                ┌──────────────▼──────────────┐
                │   Orchestration Layer       │
                │  (src/orchestration/)       │
                │                             │
                │  • Workflow Coordination    │
                │  • Iteration Management     │
                │  • State Tracking           │
                │  • Approval Logic           │
                └──────────────┬──────────────┘
                               │
                ┌──────────────▼──────────────┐
                │      Agent Layer            │
                │    (src/agents/)            │
                ├──────────────┬──────────────┤
                │    Writer    │   Reviewer   │
                │   Agent      │    Agent     │
                │              │              │
                │  Generates   │  Evaluates   │
                │  slogans     │  & approves  │
                └──────┬───────┴──────┬───────┘
                       │              │
                       └──────┬───────┘
                              │
                ┌─────────────▼─────────────┐
                │    LLM Provider           │
                │  (Ollama + Models)        │
                │                           │
                │  • mistral:latest         │
                │  • gemma2:2b              │
                │  • llama3.2:latest        │
                └───────────────────────────┘
```

---

## Component Architecture

### 1. Interface Layer

#### CLI Interface (`src/cli/`)
- **Framework**: Click (command-line interface toolkit)
- **Entry Point**: `slogan-gen` command
- **Commands**:
  - `generate`: Create slogans with Writer-Reviewer workflow
  - `models`: List available Ollama models
  - `config show`: Display current configuration
  - `config set`: Update configuration values
- **Output**: Formatted terminal output with color and styling
- **Error Handling**: User-friendly error messages with exit codes

#### REST API Interface (`src/api/`)
- **Framework**: FastAPI (async ASGI web framework)
- **Endpoints**:
  - `POST /api/v1/slogans/generate`: Slogan generation
  - `GET /api/v1/models`: List models
  - `GET /api/v1/health`: Health check
  - `GET /`: API information
- **Features**:
  - OpenAPI/Swagger documentation
  - CORS support for cross-origin requests
  - Request logging with unique IDs
  - Comprehensive error handling
  - Async request processing

### 2. Orchestration Layer (`src/orchestration/`)

**Purpose**: Coordinates the Writer-Reviewer interaction workflow

**Key Components**:

- **`workflow.py`**: Main workflow orchestration
  - `run_slogan_generation()`: Entry point for generation
  - `is_approved()`: Checks for "SHIP IT!" approval
  - `should_continue_iteration()`: Determines if more iterations needed

- **`models.py`**: Data models for workflow state
  - `IterationSession`: Tracks entire generation session
  - `Turn`: Represents single Writer-Reviewer exchange
  - `CompletionReason`: Enum for session completion (APPROVED, MAX_TURNS, ERROR)
  - `AgentRole`: Enum for agent identification (WRITER, REVIEWER)
  - `WorkflowMessage`: Communication format between agents

**Workflow Logic**:
1. Initialize session with user input
2. Loop until approval or max turns:
   - Writer generates slogan
   - Reviewer evaluates slogan
   - If "SHIP IT!" → approved, exit loop
   - If not approved → Writer creates new version with feedback
3. Complete session with final result

### 3. Agent Layer (`src/agents/`)

**Purpose**: Implements specialized agents with distinct roles

#### Writer Agent (`writer.py`)
- **Role**: Creative slogan generation
- **System Prompt**: Optimized for memorable, concise, engaging slogans
- **Behavior**: Generates initial slogan or refines based on feedback
- **Input**: User product description + optional reviewer feedback
- **Output**: New slogan proposal

#### Reviewer Agent (`reviewer.py`)
- **Role**: Quality evaluation and approval
- **System Prompt**: Evaluation criteria (memorability, clarity, conciseness, emotional appeal, uniqueness)
- **Behavior**: Evaluates slogan against criteria
- **Input**: Slogan to review
- **Output**: 
  - "SHIP IT!" (approval) OR
  - Constructive feedback for improvement

**Agent Communication**:
- Agents communicate via structured `WorkflowMessage` objects
- Asynchronous message passing pattern
- No direct agent-to-agent coupling
- Orchestration layer mediates all interactions

### 4. Configuration Layer (`src/config/`)

**Purpose**: Centralized configuration management

**Key Components**:
- **`settings.py`**: Pydantic-based configuration
  - `OllamaConfig`: All Ollama settings (URL, model, temperature, etc.)
  - `get_ollama_config()`: Cached config singleton
  - `get_available_models()`: Query Ollama for installed models

**Configuration Sources** (priority order):
1. **CLI Arguments**: Override all (e.g., `--model gemma2:2b`)
2. **Environment Variables**: `OLLAMA_*` prefix
3. **`.env` File**: Loaded automatically
4. **Defaults**: Fallback values

**Configuration Fields**:
| Field | Default | Description |
|-------|---------|-------------|
| `base_url` | `http://localhost:11434/v1` | Ollama API endpoint |
| `model_name` | `mistral:latest` | Default model |
| `temperature` | `0.7` | Sampling temperature (0.0-2.0) |
| `max_tokens` | `500` | Maximum response length |
| `timeout` | `30` | Request timeout (seconds) |
| `max_turns` | `5` | Maximum iteration turns |

---

## Technology Stack

### Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Programming language |
| **Ollama** | Latest | Local LLM runtime |
| **Microsoft Agent Framework** | - | Multi-agent pattern |
| **Pydantic** | 2.x | Data validation & settings |
| **FastAPI** | Latest | REST API framework |
| **Click** | 8.x | CLI framework |
| **httpx** | Latest | HTTP client (async) |
| **uv** | Latest | Package manager |

### LLM Models

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **gemma2:2b** | 2B params | ⚡⚡⚡ Fast | ⭐⭐ Good | Development, testing |
| **phi3:mini** | 3.8B params | ⚡⚡ Medium | ⭐⭐⭐ Very Good | Balanced performance |
| **mistral:latest** | 7B params | ⚡ Slower | ⭐⭐⭐⭐ Excellent | Production (default) |
| **llama3.2:latest** | 3B-70B params | ⚡-⚡⚡ Varies | ⭐⭐⭐⭐⭐ Outstanding | High-quality output |

### Development Tools

- **pytest**: Testing framework with fixtures and parametrization
- **Ruff**: Fast Python linter and formatter
- **mypy**: Static type checking
- **MkDocs**: Documentation generation (Material theme)
- **mkdocstrings**: API doc auto-generation

---

## Design Decisions

### 1. Multi-Agent Architecture

**Decision**: Separate Writer and Reviewer agents instead of single agent

**Rationale**:
- ✅ **Separation of Concerns**: Each agent has a single, focused responsibility
- ✅ **Better Prompts**: Specialized system prompts for each role
- ✅ **Improved Quality**: Dedicated reviewer ensures quality control
- ✅ **Extensibility**: Easy to add more agents (e.g., Editor, Marketer)
- ✅ **Microsoft Agent Framework**: Follows established pattern

**Trade-offs**:
- ❌ More LLM calls (2+ per iteration vs 1)
- ❌ Increased latency (but acceptable for quality gain)

### 2. Iterative Refinement Loop

**Decision**: Allow multiple Writer-Reviewer iterations

**Rationale**:
- ✅ **Quality Over Speed**: Iterative improvement yields better slogans
- ✅ **Feedback Integration**: Writer learns from reviewer's critique
- ✅ **Convergence**: Usually reaches approval within 2-3 turns
- ✅ **Configurable**: `max_turns` prevents infinite loops

**Implementation**:
- Default: 5 max turns (configurable)
- Exit conditions: Approval OR max turns reached
- Each turn tracked for transparency (verbose mode)

### 3. Local-First with Ollama

**Decision**: Use Ollama for local LLM execution

**Rationale**:
- ✅ **Privacy**: No data sent to external APIs
- ✅ **Cost**: No per-request charges
- ✅ **Speed**: Low latency (local network)
- ✅ **Offline**: Works without internet
- ✅ **Control**: Full control over models and settings

**Trade-offs**:
- ❌ Requires local setup (Ollama + models)
- ❌ Hardware requirements (GPU recommended)
- ❌ Model quality limited by local resources

### 4. Type-Safe Python with Pydantic

**Decision**: Use Pydantic for all data models and configuration

**Rationale**:
- ✅ **Validation**: Automatic data validation at runtime
- ✅ **Type Safety**: Full mypy compliance
- ✅ **Documentation**: Self-documenting schemas
- ✅ **IDE Support**: Better autocomplete and hints
- ✅ **FastAPI Integration**: Native Pydantic support

**Example**:
```python
class IterationSession(BaseModel):
    session_id: str
    user_input: str
    model_name: str
    turns: list[Turn] = []
    completion_reason: CompletionReason | None = None
```

### 5. Dual Interface (CLI + REST API)

**Decision**: Provide both CLI and REST API interfaces

**Rationale**:
- ✅ **Flexibility**: CLI for scripts/terminals, API for integrations
- ✅ **Different Use Cases**: Local development vs remote services
- ✅ **Same Core**: Both use identical orchestration layer
- ✅ **Progressive Enhancement**: Start with CLI, add API later

**Implementation**:
- Shared orchestration logic in `src/orchestration/`
- Interface-specific code in `src/cli/` and `src/api/`
- No duplication of business logic

### 6. Async-First API

**Decision**: Use async/await for REST API

**Rationale**:
- ✅ **Scalability**: Handle multiple concurrent requests
- ✅ **Non-Blocking**: Don't block on LLM calls
- ✅ **FastAPI Native**: FastAPI is async-first
- ✅ **Future-Proof**: Ready for async workflow if needed

**Implementation**:
```python
async def generate_slogan(request_body: GenerateRequest) -> GenerateResponse:
    session = await run_slogan_generation(...)
    return convert_session_to_response(session)
```

### 7. Comprehensive Error Handling

**Decision**: Detailed error handling at every layer

**Rationale**:
- ✅ **User Experience**: Clear error messages
- ✅ **Debugging**: Actionable error information
- ✅ **Production-Ready**: Graceful failure handling
- ✅ **Monitoring**: Structured logging for troubleshooting

**Error Categories**:
- **Connection Errors**: Ollama not running
- **Validation Errors**: Invalid input/configuration
- **Timeout Errors**: Generation exceeds limits
- **Model Errors**: Model not found/failed

---

## Data Flow

### CLI Request Flow

```
User Command
    ↓
CLI Parser (Click)
    ↓
Config Loading (Pydantic)
    ↓
Workflow Orchestration
    ↓
Agent Coordination Loop:
    Writer Agent → Slogan
    Reviewer Agent → Feedback/Approval
    (repeat until approved or max turns)
    ↓
Session Completion
    ↓
Output Formatter
    ↓
Terminal Display
```

### REST API Request Flow

```
HTTP Request
    ↓
FastAPI Router
    ↓
Request Validation (Pydantic)
    ↓
Middleware Stack:
    - Request Logging (UUID generation)
    - CORS Headers
    ↓
Endpoint Handler
    ↓
Workflow Orchestration (async)
    ↓
Agent Coordination Loop:
    Writer Agent → Slogan
    Reviewer Agent → Feedback/Approval
    (repeat until approved or max turns)
    ↓
Session Completion
    ↓
Response Serialization (Pydantic)
    ↓
Middleware Stack:
    - Response Logging
    - Request ID Header
    ↓
HTTP Response (JSON)
```

---

## Scalability Considerations

### Current Architecture

- **Single-Threaded CLI**: One request at a time
- **Multi-Request API**: FastAPI handles concurrent requests
- **Thread Pool**: API uses thread pool for sync workflow (10 workers)
- **Timeout Protection**: 600-second generation timeout

### Scaling Options

#### Horizontal Scaling
- **Load Balancer**: Distribute API requests across multiple instances
- **Stateless Design**: No shared state between API instances
- **Session Storage**: Sessions are ephemeral (no persistence required)

#### Vertical Scaling
- **GPU Acceleration**: Use NVIDIA GPU for faster inference
- **Larger Models**: Use more powerful models for better quality
- **Memory**: More RAM for concurrent requests

#### Performance Optimization
- **Model Caching**: Ollama keeps models in memory
- **Connection Pooling**: Reuse HTTP connections to Ollama
- **Async Workflow**: Convert orchestration to async (future work)

---

## Security Considerations

### Current State (Development)

- ✅ **CORS**: Configurable (default: all origins)
- ✅ **Input Validation**: Pydantic validates all inputs
- ✅ **Request Timeouts**: Prevent resource exhaustion
- ✅ **Error Sanitization**: Don't expose internal errors

### Production Recommendations

- 🔒 **API Authentication**: Add API key or OAuth2
- 🔒 **Rate Limiting**: Prevent abuse
- 🔒 **HTTPS**: Encrypt transport layer
- 🔒 **Input Sanitization**: Additional sanitization for prompts
- 🔒 **Logging**: Audit log for security events

---

## Extensibility

### Adding New Agents

```python
# src/agents/editor.py
async def create_editor_agent(config: OllamaConfig) -> Agent:
    """
    Editor agent for grammar and style improvements.
    """
    return Agent(
        name="editor",
        model=config.model_name,
        system_message="You are an expert editor...",
        # ...
    )
```

### Adding New Endpoints

```python
# src/api/routes/slogans.py
@router.post("/slogans/batch", response_model=BatchResponse)
async def generate_batch(request: BatchRequest) -> BatchResponse:
    """Generate multiple slogans in parallel."""
    # Implementation
```

### Adding New Configuration

```python
# src/config/settings.py
class OllamaConfig(BaseSettings):
    # Existing fields...
    
    # New field
    retry_attempts: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of retry attempts"
    )
```

---

## Monitoring and Observability

### Logging

- **Level**: INFO (default), configurable via `API_LOG_LEVEL`
- **Format**: Structured JSON logs (for production)
- **Request IDs**: UUID for request tracing
- **Components Logged**:
  - Request/response details
  - Workflow execution
  - Agent interactions
  - Errors and exceptions

### Metrics (Future)

Potential metrics to collect:
- Request count by endpoint
- Generation duration (p50, p95, p99)
- Turn count distribution
- Approval rate
- Error rate by type
- Model usage statistics

### Health Checks

- `/api/v1/health`: API and Ollama status
- Dependency checks (Ollama connectivity)
- Response time measurement

---

## Testing Strategy

### Unit Tests (`tests/unit/`)
- Isolated component testing
- Mock external dependencies (Ollama)
- Fast execution (< 1 second)

### Integration Tests (`tests/integration/`)
- End-to-end workflows
- Real Ollama integration (requires local setup)
- Slower execution (several seconds)

### API Tests (`tests/api/`)
- FastAPI endpoint testing
- Request/response validation
- Error handling scenarios

**Coverage Target**: > 80%

---

## Deployment Architecture

### Development

```
Developer Machine
    ├── Ollama (localhost:11434)
    ├── CLI (slogan-gen command)
    └── API (uvicorn localhost:8000)
```

### Production (Recommended)

```
┌──────────────────────────────────────────┐
│         Load Balancer / Reverse Proxy    │
│              (nginx/caddy)               │
└────────────┬─────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼────┐       ┌───▼────┐
│ API #1 │       │ API #2 │
│ (pod)  │       │ (pod)  │
└───┬────┘       └───┬────┘
    │                 │
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │  Ollama Service │
    │   (GPU node)    │
    └─────────────────┘
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install uv && uv sync

EXPOSE 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## See Also

- [Agents Architecture](agents.md) - Detailed agent design
- [Workflow Architecture](workflow.md) - Orchestration details
- [REST API Reference](../api-reference/rest-api.md) - API documentation
- [Development Guide](../guides/development.md) - Developer setup

