# API Usage Guide

Complete reference for using the Slogan Writer-Reviewer REST API for programmatic slogan generation.

## Overview

The FastAPI REST API provides HTTP endpoints for integrating slogan generation into web applications, services, and automation workflows. It offers the same Writer-Reviewer collaboration functionality as the CLI, accessible via HTTP requests.

**Base URL**: `http://localhost:8000` (default local development)

## Quick Start

### Starting the API Server

**Development Mode** (with auto-reload):

```bash
uvicorn src.api.main:app --reload
```

**Production Mode** (with multiple workers):

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**With Custom Configuration**:

```bash
export API_CORS_ORIGINS="https://myapp.com"
export API_LOG_LEVEL="INFO"
export API_GENERATION_TIMEOUT=300

uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:

- **Local**: `http://localhost:8000`
- **Network**: `http://<your-local-ip>:8000`

---

## Interactive Documentation

FastAPI automatically generates interactive API documentation:

### Swagger UI

**URL**: http://localhost:8000/docs

Features:
- Interactive endpoint testing
- Request/response examples
- Schema validation
- "Try it out" functionality

![Swagger UI](https://fastapi.tiangolo.com/img/index/index-01-swagger-ui-simple.png)

### ReDoc

**URL**: http://localhost:8000/redoc

Features:
- Clean, readable documentation
- Schema explorer
- Code samples
- Printable format

### OpenAPI Specification

**URL**: http://localhost:8000/openapi.json

The complete OpenAPI 3.0 specification in JSON format.

**Export for Code Generation:**

```bash
# Export OpenAPI spec
curl http://localhost:8000/openapi.json > docs/openapi.json

# Use with code generators
npx @openapitools/openapi-generator-cli generate \
  -i docs/openapi.json \
  -g typescript-fetch \
  -o ./generated-client
```

---

## API Endpoints

### Root Endpoint

Get API information and available endpoints.

**Request:**

```bash
curl http://localhost:8000/
```

**Response:**

```json
{
  "message": "AI Slogan Generator API",
  "version": "1.0.0",
  "endpoints": {
    "health": "/api/v1/health",
    "models": "/api/v1/models",
    "generate": "/api/v1/slogans/generate"
  }
}
```

---

### Health Check

Verify API and Ollama connectivity.

**Endpoint**: `GET /api/v1/health`

**Request:**

```bash
curl http://localhost:8000/api/v1/health
```

**Response (Healthy):**

```json
{
  "status": "healthy",
  "timestamp": "2025-10-22T10:30:00Z",
  "ollama": {
    "status": "connected",
    "base_url": "http://localhost:11434/v1"
  }
}
```

**Response (Unhealthy):**

```json
{
  "status": "unhealthy",
  "timestamp": "2025-10-22T10:30:00Z",
  "ollama": {
    "status": "disconnected",
    "base_url": "http://localhost:11434/v1",
    "error": "Connection refused"
  }
}
```

**Status Codes:**

- `200 OK`: API and Ollama healthy
- `503 Service Unavailable`: Ollama unreachable

---

### List Available Models

Get list of installed Ollama models.

**Endpoint**: `GET /api/v1/models`

**Request:**

```bash
curl http://localhost:8000/api/v1/models
```

**Response:**

```json
{
  "models": [
    {
      "id": "gemma2:2b",
      "name": "Gemma 2 2B",
      "size": "2B",
      "description": "Fast and lightweight model"
    },
    {
      "id": "mistral:latest",
      "name": "Mistral 7B",
      "size": "7B",
      "description": "Fast and capable instruction-following model"
    },
    {
      "id": "llama3.2:latest",
      "name": "Llama 3.2",
      "size": "8B",
      "description": "Latest Llama model with improved capabilities"
    }
  ],
  "total": 3,
  "default_model": "mistral:latest"
}
```

**Status Codes:**

- `200 OK`: Models retrieved successfully
- `503 Service Unavailable`: Cannot connect to Ollama

---

### Generate Slogan

Generate a slogan through Writer-Reviewer collaboration.

**Endpoint**: `POST /api/v1/slogans/generate`

#### Request

**Headers:**

```
Content-Type: application/json
```

**Body Schema:**

```json
{
  "input": "string (3-200 chars)",
  "model": "string (optional)",
  "max_turns": "integer (1-10, optional)",
  "verbose": "boolean (optional)"
}
```

**Parameters:**

| Field | Type | Required | Default | Constraints | Description |
|-------|------|----------|---------|-------------|-------------|
| `input` | string | ✅ Yes | - | 3-200 chars | Product/service description |
| `model` | string | No | `mistral:latest` | Must exist in Ollama | Model to use |
| `max_turns` | integer | No | `5` | 1-10 | Max iteration rounds |
| `verbose` | boolean | No | `false` | - | Include turn details |

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/v1/slogans/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input": "coffee shop",
    "model": "mistral:latest",
    "max_turns": 5,
    "verbose": false
  }'
```

#### Response

**Success (200 OK):**

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "input": "coffee shop",
  "final_slogan": "☕ Brew Happiness, One Cup at a Time",
  "completion_reason": "approved",
  "turn_count": 2,
  "max_turns": 5,
  "total_duration_seconds": 4.2,
  "average_duration_per_turn": 2.1,
  "model_used": "mistral:latest",
  "turns": []
}
```

**With Verbose=true:**

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "input": "coffee shop",
  "final_slogan": "☕ Brew Happiness, One Cup at a Time",
  "completion_reason": "approved",
  "turn_count": 2,
  "max_turns": 5,
  "total_duration_seconds": 4.2,
  "average_duration_per_turn": 2.1,
  "model_used": "mistral:latest",
  "turns": [
    {
      "turn_number": 1,
      "slogan": "Coffee Perfection in Every Cup",
      "feedback": "Good start, but needs more emotional appeal...",
      "approved": false,
      "duration_seconds": 2.1,
      "timestamp": "2025-10-22T10:30:00Z"
    },
    {
      "turn_number": 2,
      "slogan": "☕ Brew Happiness, One Cup at a Time",
      "feedback": "SHIP IT! Perfect combination of warmth and clarity.",
      "approved": true,
      "duration_seconds": 2.1,
      "timestamp": "2025-10-22T10:30:05Z"
    }
  ]
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `request_id` | string | Unique request identifier (UUID) |
| `input` | string | Original input description |
| `final_slogan` | string | Generated slogan (if successful) |
| `completion_reason` | string | `approved`, `max_turns_reached`, or `error` |
| `turn_count` | integer | Number of iterations performed |
| `max_turns` | integer | Maximum turns allowed |
| `total_duration_seconds` | float | Total generation time |
| `average_duration_per_turn` | float | Average time per iteration |
| `model_used` | string | Model identifier used |
| `turns` | array | Turn-by-turn details (only if `verbose=true`) |
| `error` | string | Error message (only if failed) |

#### Error Responses

**Validation Error (422):**

```json
{
  "detail": [
    {
      "loc": ["body", "input"],
      "msg": "String should have at least 3 characters",
      "type": "string_too_short",
      "input": "ab"
    }
  ]
}
```

**Model Not Found (400):**

```json
{
  "detail": "Model 'unknown' not found in Ollama. Available models: gemma2:2b, mistral:latest",
  "status_code": 400
}
```

**Generation Timeout (504):**

```json
{
  "detail": "Generation timeout: exceeded 600 seconds",
  "status_code": 504
}
```

**Internal Server Error (500):**

```json
{
  "detail": "An unexpected error occurred during generation",
  "status_code": 500
}
```

**Status Codes:**

| Code | Meaning |
|------|---------|
| `200` | Success - slogan generated |
| `400` | Bad Request - invalid model or parameters |
| `422` | Validation Error - request body invalid |
| `500` | Internal Server Error - unexpected failure |
| `503` | Service Unavailable - Ollama unreachable |
| `504` | Gateway Timeout - generation exceeded timeout |

---

## Client Examples

### Python (httpx)

**Basic Request:**

```python
import httpx

response = httpx.post(
    "http://localhost:8000/api/v1/slogans/generate",
    json={
        "input": "coffee shop",
        "model": "mistral:latest",
        "max_turns": 5
    },
    timeout=630.0  # 10.5 minutes (matches API timeout)
)

result = response.json()
print(f"Slogan: {result['final_slogan']}")
print(f"Took {result['turn_count']} turns in {result['total_duration_seconds']:.1f}s")
```

**With Error Handling:**

```python
import httpx

def generate_slogan(input_text: str, model: str = "mistral:latest") -> dict:
    """Generate slogan with proper error handling."""
    try:
        response = httpx.post(
            "http://localhost:8000/api/v1/slogans/generate",
            json={
                "input": input_text,
                "model": model,
                "max_turns": 5,
                "verbose": True
            },
            timeout=630.0
        )
        response.raise_for_status()
        return response.json()
    
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 422:
            print(f"Validation error: {e.response.json()}")
        elif e.response.status_code == 400:
            print(f"Bad request: {e.response.json()['detail']}")
        elif e.response.status_code == 503:
            print("Ollama service unavailable")
        else:
            print(f"HTTP error {e.response.status_code}: {e}")
        raise
    
    except httpx.TimeoutException:
        print("Request timed out")
        raise
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

# Usage
try:
    result = generate_slogan("eco-friendly water bottle")
    print(result["final_slogan"])
except Exception:
    print("Failed to generate slogan")
```

**Async Version:**

```python
import httpx
import asyncio

async def generate_slogan_async(input_text: str) -> dict:
    """Async slogan generation."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/slogans/generate",
            json={"input": input_text, "max_turns": 5},
            timeout=630.0
        )
        response.raise_for_status()
        return response.json()

# Usage
result = asyncio.run(generate_slogan_async("coffee shop"))
print(result["final_slogan"])
```

### JavaScript (Fetch API)

**Basic Request:**

```javascript
async function generateSlogan(input, model = 'mistral:latest') {
  const response = await fetch('http://localhost:8000/api/v1/slogans/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      input: input,
      model: model,
      max_turns: 5,
      verbose: false
    })
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  const result = await response.json();
  return result;
}

// Usage
generateSlogan('coffee shop')
  .then(result => {
    console.log(`Slogan: ${result.final_slogan}`);
    console.log(`Took ${result.turn_count} turns`);
  })
  .catch(error => console.error('Error:', error));
```

**With Error Handling:**

```javascript
async function generateSloganSafe(input) {
  try {
    const response = await fetch('http://localhost:8000/api/v1/slogans/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input, max_turns: 5 })
    });
    
    if (response.status === 422) {
      const error = await response.json();
      console.error('Validation error:', error.detail);
      return null;
    }
    
    if (response.status === 503) {
      console.error('Ollama service unavailable');
      return null;
    }
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Request failed:', error);
    return null;
  }
}

// Usage
const result = await generateSloganSafe('eco-friendly water bottle');
if (result) {
  console.log(result.final_slogan);
}
```

### cURL

**Basic Generation:**

```bash
curl -X POST http://localhost:8000/api/v1/slogans/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input": "coffee shop",
    "max_turns": 5
  }'
```

**With All Options:**

```bash
curl -X POST http://localhost:8000/api/v1/slogans/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input": "eco-friendly water bottle",
    "model": "mistral:latest",
    "max_turns": 7,
    "verbose": true
  }' | jq '.'
```

**Save Response to File:**

```bash
curl -X POST http://localhost:8000/api/v1/slogans/generate \
  -H "Content-Type: application/json" \
  -d '{"input": "coffee shop"}' \
  -o slogan-result.json
```

---

## Configuration

### Environment Variables

Configure the API using environment variables:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `API_CORS_ORIGINS` | string | `http://localhost:3000,http://localhost:8080` | Comma-separated allowed origins |
| `API_GENERATION_TIMEOUT` | integer | `600` | Max generation time (seconds) |
| `API_REQUEST_TIMEOUT` | integer | `630` | Total request timeout (seconds) |
| `API_LOG_LEVEL` | string | `WARNING` | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `API_MAX_CONCURRENT_REQUESTS` | integer | `10` | Max simultaneous generations |

### Configuration Examples

**Development (.env file):**

```bash
# .env
API_CORS_ORIGINS=http://localhost:3000,http://localhost:5173
API_LOG_LEVEL=DEBUG
API_GENERATION_TIMEOUT=300
API_MAX_CONCURRENT_REQUESTS=5
```

**Production:**

```bash
export API_CORS_ORIGINS="https://myapp.com,https://www.myapp.com"
export API_LOG_LEVEL=INFO
export API_GENERATION_TIMEOUT=600
export API_REQUEST_TIMEOUT=630
export API_MAX_CONCURRENT_REQUESTS=20

uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Load Configuration:**

```bash
# From .env file
uvicorn src.api.main:app --env-file .env

# From environment
set -a && source config.env && set +a
uvicorn src.api.main:app
```

---

## CORS Configuration

### Understanding CORS

Cross-Origin Resource Sharing (CORS) allows web applications on different domains to access your API.

**Default Allowed Origins:**

- `http://localhost:3000` (React, Next.js)
- `http://localhost:8080` (Vue.js)

### Configuring CORS

**Allow Specific Origins:**

```bash
export API_CORS_ORIGINS="https://myapp.com,https://staging.myapp.com"
```

**Allow All Origins (Development Only!):**

```bash
export API_CORS_ORIGINS="*"
```

!!! warning "Security Warning"
    Never use `API_CORS_ORIGINS="*"` in production. Always specify exact origins.

### Testing CORS

```bash
# Preflight request
curl -X OPTIONS http://localhost:8000/api/v1/slogans/generate \
  -H "Origin: https://myapp.com" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

---

## Rate Limiting & Concurrency

The API limits concurrent requests to prevent resource exhaustion:

- **Default**: 10 concurrent requests
- **Configurable**: `API_MAX_CONCURRENT_REQUESTS`

**When Limit Reached:**

```json
{
  "detail": "Too many concurrent requests. Please try again later.",
  "status_code": 503
}
```

---

## Request Tracking

Every request receives a unique `X-Request-ID` header for debugging and logging:

**Request:**

```bash
curl -i http://localhost:8000/api/v1/health
```

**Response Headers:**

```
HTTP/1.1 200 OK
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json
```

Use this ID when reporting issues or tracking requests in logs.

---

## Dev Tunnels (Public Access)

Expose your local API to the internet for testing and sharing.

### Setup Steps

**1. Install Dev Tunnels:**

```bash
# macOS (Homebrew)
brew install devtunnel

# Or download from Microsoft
```

**2. Authenticate:**

```bash
devtunnel user login
```

**3. Create Tunnel:**

```bash
devtunnel create -a
# Note the tunnel name, e.g., "fancy-fog-6mp2hnq"
```

**4. Create Port Mapping:**

```bash
devtunnel port create -p 8000
```

**5. Start Hosting:**

```bash
# In terminal 1
devtunnel host fancy-fog-6mp2hnq

# In terminal 2
uvicorn src.api.main:app --reload
```

**6. Access Public URL:**

You'll receive a URL like: `https://f61krm0p-8000.euw.devtunnels.ms`

**7. Test Public Endpoint:**

```bash
curl https://your-tunnel-url.devtunnels.ms/api/v1/health

curl -X POST https://your-tunnel-url.devtunnels.ms/api/v1/slogans/generate \
  -H "Content-Type: application/json" \
  -d '{"input": "coffee shop"}'
```

!!! note "Development Only"
    Dev Tunnels are for development and testing. For production, use proper hosting (Azure, AWS, etc.).

---

## Performance Considerations

### Timeouts

- **Generation Timeout**: 600s (10 minutes) - max time for slogan generation
- **Request Timeout**: 630s (10.5 minutes) - total request time including overhead

**Adjust for Large Models:**

```bash
export API_GENERATION_TIMEOUT=900  # 15 minutes
export API_REQUEST_TIMEOUT=930     # 15.5 minutes
```

### Concurrent Requests

- **Default Limit**: 10 concurrent generations
- **Recommendation**: 5-10 for CPU, 20+ for GPU

```bash
export API_MAX_CONCURRENT_REQUESTS=5  # Conservative
```

### Model Selection

Choose models based on throughput needs:

| Model | Speed | Concurrent Capacity (CPU) | Use Case |
|-------|-------|---------------------------|----------|
| `gemma2:2b` | ⚡⚡⚡ | 10-15 requests | High throughput |
| `mistral:latest` | ⚡ | 5-10 requests | Balanced |
| `llama3.2:latest` | 🐌 | 2-5 requests | Quality focused |

---

## Monitoring & Logging

### Log Levels

Control API logging verbosity:

```bash
export API_LOG_LEVEL=DEBUG  # All messages
export API_LOG_LEVEL=INFO   # General info
export API_LOG_LEVEL=WARNING  # Warnings and errors (default)
export API_LOG_LEVEL=ERROR  # Errors only
```

### Log Format

```
2025-10-22 10:30:00 INFO     [550e8400] POST /api/v1/slogans/generate
2025-10-22 10:30:05 INFO     [550e8400] Generation complete: 2 turns, 4.2s
```

### Health Monitoring

**Automated Health Checks:**

```bash
# Every 30 seconds
while true; do
  curl -s http://localhost:8000/api/v1/health | jq '.status'
  sleep 30
done
```

---

## See Also

- [CLI Usage Guide](cli-usage.md) - Command-line alternative
- [Configuration Guide](../getting-started/configuration.md) - Environment variables and settings
- [Troubleshooting Guide](../troubleshooting.md) - Common API issues
- [Development Guide](development.md) - Contributing and extending the API
