# REST API Reference

This page documents the FastAPI implementation of the Slogan Writer-Reviewer REST API.

## Overview

The REST API provides a FastAPI-based HTTP interface for slogan generation with:

- **Async/Await Architecture**: Non-blocking request handling
- **CORS Support**: Configurable cross-origin resource sharing
- **Request Logging**: Automatic request/response tracking with unique IDs
- **Error Handling**: Comprehensive exception handlers with detailed responses
- **OpenAPI Documentation**: Auto-generated interactive docs

**Base URL**: `http://localhost:8000` (development)

---

## FastAPI Application

::: src.api.main.app
    options:
      show_source: true
      heading_level: 3

**Purpose**: Main FastAPI application instance with middleware and routes configured.

### Application Configuration

| Property | Value | Description |
|----------|-------|-------------|
| Title | "Slogan Writer-Reviewer API" | API name |
| Version | "1.0.0" | Semantic version |
| Description | "Multi-agent slogan generation via Writer-Reviewer collaboration" | API purpose |

### Middleware Stack

1. **CORS Middleware**: Configurable cross-origin requests
2. **RequestLoggingMiddleware**: Request/response logging with UUIDs

### Registered Routes

- `/` - Root endpoint with API information
- `/api/v1/health` - Health check endpoint
- `/api/v1/models` - Available models endpoint
- `/api/v1/slogans/generate` - Slogan generation endpoint

---

## Endpoints

### Root Endpoint

::: src.api.main.get_root
    options:
      show_source: true
      heading_level: 4

**Purpose**: Provide API information and documentation links.

**HTTP Method**: `GET /`

**Response**: RootResponse with API name, version, description, and documentation URLs

**Example Request**:
```bash
curl http://localhost:8000/
```

**Example Response**:
```json
{
  "name": "Slogan Writer-Reviewer API",
  "version": "1.0.0",
  "description": "Multi-agent slogan generation via Writer-Reviewer collaboration",
  "documentation": {
    "swagger": "/docs",
    "redoc": "/redoc",
    "openapi": "/openapi.json"
  }
}
```

---

### Health Check Endpoint

::: src.api.routes.health.get_health
    options:
      show_source: true
      heading_level: 4

**Purpose**: Check API and Ollama dependency health.

**HTTP Method**: `GET /api/v1/health`

**Response Codes**:
- `200 OK`: API and dependencies healthy
- `503 Service Unavailable`: Ollama not connected

**Response**: HealthResponse with status, version, timestamp, and dependency details

**Example Request**:
```bash
curl http://localhost:8000/api/v1/health
```

**Example Response (Healthy)**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "dependencies": {
    "ollama": {
      "connected": true,
      "url": "http://localhost:11434",
      "response_time_ms": 45,
      "error": null
    }
  }
}
```

**Example Response (Degraded)**:
```json
{
  "status": "degraded",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "dependencies": {
    "ollama": {
      "connected": false,
      "url": "http://localhost:11434",
      "response_time_ms": null,
      "error": "Connection refused"
    }
  }
}
```

---

### Models Endpoint

::: src.api.routes.models.get_models
    options:
      show_source: true
      heading_level: 4

**Purpose**: List available Ollama models.

**HTTP Method**: `GET /api/v1/models`

**Response**: ModelsResponse with list of models, default model, and count

**Error Responses**:
- `503 Service Unavailable`: Ollama not accessible
- `500 Internal Server Error`: Other errors

**Example Request**:
```bash
curl http://localhost:8000/api/v1/models
```

**Example Response**:
```json
{
  "models": [
    {"name": "gemma2:2b", "display_name": "Gemma2 2B"},
    {"name": "mistral:latest", "display_name": "Mistral Latest"},
    {"name": "llama3.2:latest", "display_name": "Llama3.2 Latest"}
  ],
  "default_model": "mistral:latest",
  "count": 3
}
```

**Example Error (Service Unavailable)**:
```json
{
  "detail": {
    "error": "service_unavailable",
    "message": "Failed to connect to Ollama at http://localhost:11434/v1",
    "suggestion": "Ensure Ollama is running with 'ollama serve'"
  }
}
```

---

### Generate Slogan Endpoint

::: src.api.routes.generate.generate_slogan
    options:
      show_source: true
      heading_level: 4

**Purpose**: Generate a slogan via Writer-Reviewer collaboration.

**HTTP Method**: `POST /api/v1/slogans/generate`

**Request Body**: GenerateRequest with input, optional model, max_turns, verbose

**Response**: GenerateResponse with final slogan and metadata

**Timeout**: 600 seconds (10 minutes)

**Error Responses**:
- `400 Bad Request`: Invalid model specified
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Generation error
- `504 Gateway Timeout`: Generation timeout (>600s)

**Example Request (Basic)**:
```bash
curl -X POST http://localhost:8000/api/v1/slogans/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input": "eco-friendly water bottles"
  }'
```

**Example Response (Basic)**:
```json
{
  "slogan": "Stay Hydrated, Save the Planet",
  "input": "eco-friendly water bottles",
  "completion_reason": "approved",
  "turn_count": 3,
  "model_name": "mistral:latest",
  "total_duration_seconds": 12.45,
  "average_duration_per_turn": 4.15,
  "turns": null,
  "created_at": "2024-01-15T10:30:00Z",
  "request_id": "a1b2c3d4-e5f6-7890-ab12-cd34ef567890"
}
```

**Example Request (Verbose with Options)**:
```bash
curl -X POST http://localhost:8000/api/v1/slogans/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input": "AI-powered productivity tools",
    "model": "llama3.2:latest",
    "max_turns": 5,
    "verbose": true
  }'
```

**Example Response (Verbose)**:
```json
{
  "slogan": "Work Smarter, Not Harder with AI",
  "input": "AI-powered productivity tools",
  "completion_reason": "approved",
  "turn_count": 2,
  "model_name": "llama3.2:latest",
  "total_duration_seconds": 8.73,
  "average_duration_per_turn": 4.37,
  "turns": [
    {
      "turn_number": 1,
      "slogan": "Supercharge Your Workflow with AI",
      "feedback": "Good start but 'supercharge' is overused...",
      "approved": false,
      "timestamp": "2024-01-15T10:30:05Z"
    },
    {
      "turn_number": 2,
      "slogan": "Work Smarter, Not Harder with AI",
      "feedback": null,
      "approved": true,
      "timestamp": "2024-01-15T10:30:09Z"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "request_id": "b2c3d4e5-f6g7-8901-bc23-de45fg678901"
}
```

**Example Error (Validation)**:
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "input"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {"min_length": 1}
    }
  ]
}
```

**Example Error (Invalid Model)**:
```json
{
  "detail": {
    "error": "invalid_model",
    "message": "Model 'nonexistent:latest' not found",
    "available_models": ["gemma2:2b", "mistral:latest", "llama3.2:latest"]
  }
}
```

---

## Request/Response Schemas

### Request Models

#### GenerateRequest

::: src.api.schemas.requests.GenerateRequest
    options:
      show_source: true
      heading_level: 5

**Fields**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `input` | str | ✅ | 1-500 chars | Product/topic description |
| `model` | str \| None | ❌ | | Ollama model (uses default if omitted) |
| `max_turns` | int \| None | ❌ | 1-10 | Max iterations (uses config default if omitted) |
| `verbose` | bool | ❌ | | Include turn details (default: false) |

---

### Response Models

#### RootResponse

::: src.api.schemas.responses.RootResponse
    options:
      show_source: true
      heading_level: 5

#### HealthResponse

::: src.api.schemas.responses.HealthResponse
    options:
      show_source: true
      heading_level: 5

#### DependencyStatus

::: src.api.schemas.responses.DependencyStatus
    options:
      show_source: true
      heading_level: 5

#### ModelsResponse

::: src.api.schemas.responses.ModelsResponse
    options:
      show_source: true
      heading_level: 5

#### ModelInfo

::: src.api.schemas.responses.ModelInfo
    options:
      show_source: true
      heading_level: 5

#### GenerateResponse

::: src.api.schemas.responses.GenerateResponse
    options:
      show_source: true
      heading_level: 5

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `slogan` | str | Final approved slogan |
| `input` | str | Original user input |
| `completion_reason` | "approved" \| "max_turns" \| "error" | Why generation stopped |
| `turn_count` | int | Number of iterations |
| `model_name` | str | Model used |
| `total_duration_seconds` | float | Total time |
| `average_duration_per_turn` | float | Average time per turn |
| `turns` | list[TurnDetail] \| None | Turn history (verbose only) |
| `created_at` | datetime | Request timestamp |
| `request_id` | UUID \| None | Request identifier |

#### TurnDetail

::: src.api.schemas.responses.TurnDetail
    options:
      show_source: true
      heading_level: 5

---

## Middleware

### RequestLoggingMiddleware

::: src.api.middleware.RequestLoggingMiddleware
    options:
      show_source: true
      heading_level: 4

**Purpose**: Log all HTTP requests/responses with unique tracking IDs.

**Features**:

- Generates `X-Request-ID` header (UUID v4)
- Logs request method, path, query params, client IP
- Logs response status code, duration
- Adds request ID to response headers
- Stores request ID in `request.state` for endpoint access

**Log Example**:
```
INFO Request started: POST /api/v1/slogans/generate
  request_id=a1b2c3d4-e5f6-7890-ab12-cd34ef567890
  method=POST
  path=/api/v1/slogans/generate
  query_params=
  client_host=127.0.0.1

INFO Request completed: POST /api/v1/slogans/generate - 200
  request_id=a1b2c3d4-e5f6-7890-ab12-cd34ef567890
  method=POST
  path=/api/v1/slogans/generate
  status_code=200
  duration_ms=12450.67
```

---

## CORS Configuration

The API supports CORS (Cross-Origin Resource Sharing) configuration via environment variable:

**Environment Variable**: `API_CORS_ORIGINS`

**Format**: Comma-separated list of allowed origins

**Default**: `*` (all origins, development only)

**Examples**:

```bash
# Allow all origins (development)
API_CORS_ORIGINS="*"

# Allow specific origins (production)
API_CORS_ORIGINS="https://app.example.com,https://admin.example.com"

# Allow localhost variants (development)
API_CORS_ORIGINS="http://localhost:3000,http://127.0.0.1:3000"
```

**CORS Settings**:

| Setting | Value | Description |
|---------|-------|-------------|
| `allow_credentials` | `true` | Allow cookies/auth headers |
| `allow_methods` | `["*"]` | All HTTP methods allowed |
| `allow_headers` | `["*"]` | All headers allowed |

**Implementation**:

- When `API_CORS_ORIGINS="*"`: Uses `allow_origin_regex="https?://.*"` (regex match for all)
- Otherwise: Uses `allow_origins=[...]` (specific origin list)

---

## Error Handling

The API has comprehensive error handlers for different exception types:

### Validation Errors (422)

Handled by `validation_exception_handler` for Pydantic validation failures:

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "input"],
      "msg": "String should have at least 1 character",
      "input": ""
    }
  ]
}
```

### HTTP Exceptions (4xx, 5xx)

Handled by `http_exception_handler` for FastAPI/Starlette HTTP exceptions:

```json
{
  "detail": {
    "error": "service_unavailable",
    "message": "Ollama not accessible",
    "suggestion": "Ensure Ollama is running"
  }
}
```

### Unhandled Exceptions (500)

Handled by `unhandled_exception_handler` for unexpected errors:

```json
{
  "detail": {
    "error": "internal_server_error",
    "message": "An unexpected error occurred"
  }
}
```

---

## Usage Patterns

### Python Client (httpx)

```python
import httpx

# Async client
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/slogans/generate",
        json={"input": "smart home devices", "verbose": True}
    )
    data = response.json()
    print(data["slogan"])
```

### JavaScript/TypeScript (fetch)

```javascript
const response = await fetch('http://localhost:8000/api/v1/slogans/generate', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    input: 'cloud storage solutions',
    model: 'mistral:latest',
    max_turns: 5
  })
});

const data = await response.json();
console.log(data.slogan);
```

### cURL

```bash
# Health check
curl http://localhost:8000/api/v1/health

# List models
curl http://localhost:8000/api/v1/models

# Generate slogan
curl -X POST http://localhost:8000/api/v1/slogans/generate \
  -H "Content-Type: application/json" \
  -d '{"input": "sustainable fashion brand"}'

# Generate with custom request ID
curl -X POST http://localhost:8000/api/v1/slogans/generate \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: my-custom-id-123" \
  -d '{"input": "coffee subscription service", "verbose": true}'
```

---

## Running the API

### Development Server

```bash
# With uv (recommended)
uv run fastapi dev src/api/main.py

# With uvicorn directly
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Server

```bash
# With gunicorn + uvicorn workers
gunicorn src.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000

# With uvicorn
uvicorn src.api.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4
```

### Environment Configuration

```bash
# .env
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL_NAME=mistral:latest
OLLAMA_MAX_TURNS=5

API_CORS_ORIGINS=https://app.example.com
API_LOG_LEVEL=INFO
API_GENERATION_TIMEOUT=600
API_REQUEST_TIMEOUT=30
```

---

## Best Practices

### Use Verbose Mode Sparingly

✅ **Do**:
```python
# Only use verbose for debugging/analysis
response = client.post("/api/v1/slogans/generate", 
    json={"input": "test", "verbose": True})
```

❌ **Don't**:
```python
# Don't use verbose in production for all requests (larger responses)
for item in items:
    response = client.post(..., json={"input": item, "verbose": True})
```

### Handle Timeouts

✅ **Do**:
```python
try:
    response = await client.post(
        url, 
        json={"input": text},
        timeout=620.0  # Slightly > 600s server timeout
    )
except httpx.TimeoutException:
    print("Generation took too long")
```

### Check Health Before Operations

✅ **Do**:
```python
# Verify API health before batch operations
health = await client.get("/api/v1/health")
if health.json()["status"] != "healthy":
    print("API not ready")
    return
```

### Use Request IDs for Tracking

✅ **Do**:
```python
# Provide custom request ID for tracking
request_id = str(uuid.uuid4())
response = await client.post(
    url,
    json={"input": text},
    headers={"X-Request-ID": request_id}
)
# Log or store request_id for debugging
```

---

## See Also

- [API Usage Guide](../guides/api-usage.md) - User guide for REST API
- [Configuration API Reference](config.md) - Configuration management
- [Orchestration API Reference](orchestration.md) - Workflow implementation
- [Development Guide](../guides/development.md) - API development setup
