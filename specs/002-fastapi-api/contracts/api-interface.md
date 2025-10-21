# API Interface Contract

**Feature**: 002-fastapi-api  
**Date**: 2025-10-21  
**Interface Type**: REST API (FastAPI-based)  
**Base URL**: `http://localhost:8000/api/v1`  
**OpenAPI Version**: 3.1.0

## Overview

This document defines the complete REST API contract for the Slogan Generation API. All endpoints follow REST principles with JSON request/response formats. The API wraps the existing CLI orchestration layer to provide programmatic access to slogan generation functionality.

## API Metadata

```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "Slogan Writer-Reviewer API",
    "version": "1.0.0",
    "description": "Multi-agent slogan generation via Writer-Reviewer collaboration",
    "contact": {
      "name": "API Support"
    }
  },
  "servers": [
    {
      "url": "http://localhost:8000/api/v1",
      "description": "Development server"
    }
  ]
}
```

## Global Headers

### Request Headers

| Header | Required | Description | Example |
|--------|----------|-------------|---------|
| `Content-Type` | Yes (POST) | Request content type | `application/json` |
| `Accept` | No | Response content type | `application/json` |

### Response Headers (All Endpoints)

| Header | Always Present | Description | Example |
|--------|----------------|-------------|---------|
| `Content-Type` | Yes | Response content type | `application/json` |
| `X-Request-ID` | Yes | Unique request identifier (UUID v4) | `550e8400-e29b-41d4-a716-446655440000` |
| `Access-Control-Allow-Origin` | Yes | CORS origin (configurable) | `http://localhost:3000` |

---

## Endpoints

### 1. Root Endpoint

**Method**: `GET`  
**Path**: `/`  
**Summary**: API information and documentation links  
**Operation ID**: `get_root`  
**Tags**: `["info"]`

#### Request

**Query Parameters**: None  
**Request Body**: None

#### Responses

##### 200 OK - Success

**Description**: API metadata with documentation links

**Schema**:

```json
{
  "type": "object",
  "required": ["name", "version", "description", "documentation"],
  "properties": {
    "name": {
      "type": "string",
      "description": "API name",
      "example": "Slogan Writer-Reviewer API"
    },
    "version": {
      "type": "string",
      "description": "API version (semver)",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "example": "1.0.0"
    },
    "description": {
      "type": "string",
      "description": "API description",
      "example": "Multi-agent slogan generation via Writer-Reviewer collaboration"
    },
    "documentation": {
      "type": "object",
      "required": ["swagger", "redoc", "openapi"],
      "properties": {
        "swagger": {
          "type": "string",
          "description": "Swagger UI URL",
          "example": "/docs"
        },
        "redoc": {
          "type": "string",
          "description": "ReDoc URL",
          "example": "/redoc"
        },
        "openapi": {
          "type": "string",
          "description": "OpenAPI JSON schema URL",
          "example": "/openapi.json"
        }
      }
    }
  }
}
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

**Headers**:
- `X-Request-ID: 550e8400-e29b-41d4-a716-446655440000`

---

### 2. Health Check

**Method**: `GET`  
**Path**: `/api/v1/health`  
**Summary**: Check API and dependency health  
**Operation ID**: `get_health`  
**Tags**: `["monitoring"]`

#### Request

**Query Parameters**: None  
**Request Body**: None

#### Responses

##### 200 OK - Healthy

**Description**: All systems operational

**Schema**:

```json
{
  "type": "object",
  "required": ["status", "version", "timestamp", "dependencies"],
  "properties": {
    "status": {
      "type": "string",
      "enum": ["healthy"],
      "description": "Overall health status"
    },
    "version": {
      "type": "string",
      "description": "API version",
      "example": "1.0.0"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "Health check timestamp (ISO 8601)",
      "example": "2025-10-21T10:30:00.000Z"
    },
    "dependencies": {
      "type": "object",
      "required": ["ollama"],
      "properties": {
        "ollama": {
          "type": "object",
          "required": ["connected", "url"],
          "properties": {
            "connected": {
              "type": "boolean",
              "description": "Ollama connectivity status",
              "example": true
            },
            "url": {
              "type": "string",
              "format": "uri",
              "description": "Ollama base URL",
              "example": "http://localhost:11434"
            },
            "response_time_ms": {
              "type": "integer",
              "description": "Ollama response time in milliseconds",
              "minimum": 0,
              "example": 15
            }
          }
        }
      }
    }
  }
}
```

**Example Response**:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-10-21T10:30:00.000Z",
  "dependencies": {
    "ollama": {
      "connected": true,
      "url": "http://localhost:11434",
      "response_time_ms": 15
    }
  }
}
```

**Headers**:
- `X-Request-ID: 550e8400-e29b-41d4-a716-446655440000`

##### 503 Service Unavailable - Degraded

**Description**: One or more dependencies unavailable

**Schema**:

```json
{
  "type": "object",
  "required": ["status", "version", "timestamp", "dependencies"],
  "properties": {
    "status": {
      "type": "string",
      "enum": ["degraded"],
      "description": "Overall health status"
    },
    "version": {
      "type": "string",
      "description": "API version",
      "example": "1.0.0"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "Health check timestamp (ISO 8601)"
    },
    "dependencies": {
      "type": "object",
      "required": ["ollama"],
      "properties": {
        "ollama": {
          "type": "object",
          "required": ["connected", "url", "error"],
          "properties": {
            "connected": {
              "type": "boolean",
              "description": "Ollama connectivity status",
              "example": false
            },
            "url": {
              "type": "string",
              "format": "uri",
              "description": "Ollama base URL",
              "example": "http://localhost:11434"
            },
            "error": {
              "type": "string",
              "description": "Error message",
              "example": "Connection refused"
            }
          }
        }
      }
    }
  }
}
```

**Example Response**:

```json
{
  "status": "degraded",
  "version": "1.0.0",
  "timestamp": "2025-10-21T10:30:00.000Z",
  "dependencies": {
    "ollama": {
      "connected": false,
      "url": "http://localhost:11434",
      "error": "Connection refused"
    }
  }
}
```

**Headers**:
- `X-Request-ID: 550e8400-e29b-41d4-a716-446655440000`

---

### 3. List Models

**Method**: `GET`  
**Path**: `/api/v1/models`  
**Summary**: List available Ollama models  
**Operation ID**: `list_models`  
**Tags**: `["models"]`

#### Request

**Query Parameters**: None  
**Request Body**: None

#### Responses

##### 200 OK - Success

**Description**: List of available models

**Schema**:

```json
{
  "type": "object",
  "required": ["models", "default_model", "total_count"],
  "properties": {
    "models": {
      "type": "array",
      "description": "Available Ollama models",
      "items": {
        "type": "object",
        "required": ["name", "display_name", "is_default"],
        "properties": {
          "name": {
            "type": "string",
            "description": "Model identifier (used in API requests)",
            "example": "mistral:latest"
          },
          "display_name": {
            "type": "string",
            "description": "Human-readable model name",
            "example": "Mistral 7B (Latest)"
          },
          "is_default": {
            "type": "boolean",
            "description": "Whether this is the default model",
            "example": true
          }
        }
      }
    },
    "default_model": {
      "type": "string",
      "description": "Default model identifier",
      "example": "mistral:latest"
    },
    "total_count": {
      "type": "integer",
      "description": "Total number of available models",
      "minimum": 0,
      "example": 3
    }
  }
}
```

**Example Response**:

```json
{
  "models": [
    {
      "name": "mistral:latest",
      "display_name": "Mistral 7B (Latest)",
      "is_default": true
    },
    {
      "name": "llama3.2:latest",
      "display_name": "Llama 3.2 (Latest)",
      "is_default": false
    },
    {
      "name": "phi3:mini",
      "display_name": "Phi-3 Mini",
      "is_default": false
    }
  ],
  "default_model": "mistral:latest",
  "total_count": 3
}
```

**Headers**:
- `X-Request-ID: 550e8400-e29b-41d4-a716-446655440000`

##### 503 Service Unavailable - Ollama Unavailable

**Description**: Cannot connect to Ollama

**Schema**:

```json
{
  "type": "object",
  "required": ["detail"],
  "properties": {
    "detail": {
      "type": "string",
      "description": "Error message",
      "example": "Cannot connect to Ollama service at http://localhost:11434"
    }
  }
}
```

**Example Response**:

```json
{
  "detail": "Cannot connect to Ollama service at http://localhost:11434"
}
```

**Headers**:
- `X-Request-ID: 550e8400-e29b-41d4-a716-446655440000`

---

### 4. Generate Slogan

**Method**: `POST`  
**Path**: `/api/v1/slogans/generate`  
**Summary**: Generate a slogan through Writer-Reviewer collaboration  
**Operation ID**: `generate_slogan`  
**Tags**: `["slogans"]`

#### Request

**Query Parameters**: None

**Request Body**: Required

**Content-Type**: `application/json`

**Schema**:

```json
{
  "type": "object",
  "required": ["input"],
  "properties": {
    "input": {
      "type": "string",
      "description": "Product/topic description for slogan generation",
      "minLength": 1,
      "maxLength": 500,
      "example": "eco-friendly water bottle"
    },
    "model": {
      "type": "string",
      "description": "Ollama model name (optional, uses default if not specified)",
      "example": "mistral:latest",
      "default": "mistral:latest"
    },
    "max_turns": {
      "type": "integer",
      "description": "Maximum iteration turns (optional)",
      "minimum": 1,
      "maximum": 10,
      "default": 5,
      "example": 5
    },
    "verbose": {
      "type": "boolean",
      "description": "Include all iteration turns in response (optional)",
      "default": false,
      "example": false
    }
  }
}
```

**Example Request**:

```json
{
  "input": "eco-friendly water bottle",
  "model": "mistral:latest",
  "max_turns": 5,
  "verbose": true
}
```

#### Responses

##### 200 OK - Success

**Description**: Slogan generated successfully

**Schema**:

```json
{
  "type": "object",
  "required": [
    "slogan",
    "input",
    "completion_reason",
    "turn_count",
    "model_name",
    "total_duration_seconds",
    "created_at"
  ],
  "properties": {
    "slogan": {
      "type": "string",
      "description": "Final approved slogan",
      "maxLength": 500,
      "example": "Hydrate Responsibly, Live Sustainably"
    },
    "input": {
      "type": "string",
      "description": "Original user input",
      "example": "eco-friendly water bottle"
    },
    "completion_reason": {
      "type": "string",
      "enum": ["approved", "max_turns", "error"],
      "description": "Reason for generation completion",
      "example": "approved"
    },
    "turn_count": {
      "type": "integer",
      "description": "Number of iterations performed",
      "minimum": 1,
      "example": 3
    },
    "model_name": {
      "type": "string",
      "description": "Model used for generation",
      "example": "mistral:latest"
    },
    "total_duration_seconds": {
      "type": "number",
      "description": "Total generation time in seconds",
      "minimum": 0,
      "example": 45.3
    },
    "average_duration_per_turn": {
      "type": "number",
      "description": "Average time per iteration in seconds",
      "minimum": 0,
      "example": 15.1
    },
    "turns": {
      "type": "array",
      "description": "Iteration history (only if verbose=true)",
      "items": {
        "type": "object",
        "required": ["turn_number", "slogan", "approved", "timestamp"],
        "properties": {
          "turn_number": {
            "type": "integer",
            "description": "Iteration number (1-indexed)",
            "minimum": 1,
            "example": 1
          },
          "slogan": {
            "type": "string",
            "description": "Slogan proposed in this turn",
            "example": "Drink Green, Stay Clean"
          },
          "feedback": {
            "type": ["string", "null"],
            "description": "Reviewer feedback (null if approved)",
            "example": "Good concept but lacks emotional appeal. Consider emphasizing sustainability impact."
          },
          "approved": {
            "type": "boolean",
            "description": "Whether slogan was approved",
            "example": false
          },
          "timestamp": {
            "type": "string",
            "format": "date-time",
            "description": "Turn timestamp (ISO 8601)",
            "example": "2025-10-21T10:30:15.000Z"
          }
        }
      }
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "Request timestamp (ISO 8601)",
      "example": "2025-10-21T10:30:00.000Z"
    },
    "request_id": {
      "type": "string",
      "format": "uuid",
      "description": "Request identifier (UUID v4)",
      "example": "550e8400-e29b-41d4-a716-446655440000"
    }
  }
}
```

**Example Response (verbose=false)**:

```json
{
  "slogan": "Hydrate Responsibly, Live Sustainably",
  "input": "eco-friendly water bottle",
  "completion_reason": "approved",
  "turn_count": 3,
  "model_name": "mistral:latest",
  "total_duration_seconds": 45.3,
  "average_duration_per_turn": 15.1,
  "created_at": "2025-10-21T10:30:00.000Z",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Example Response (verbose=true)**:

```json
{
  "slogan": "Hydrate Responsibly, Live Sustainably",
  "input": "eco-friendly water bottle",
  "completion_reason": "approved",
  "turn_count": 3,
  "model_name": "mistral:latest",
  "total_duration_seconds": 45.3,
  "average_duration_per_turn": 15.1,
  "turns": [
    {
      "turn_number": 1,
      "slogan": "Drink Green, Stay Clean",
      "feedback": "Good concept but lacks emotional appeal. Consider emphasizing sustainability impact.",
      "approved": false,
      "timestamp": "2025-10-21T10:30:15.000Z"
    },
    {
      "turn_number": 2,
      "slogan": "Eco Sip, Earth's Gift",
      "feedback": "Better but too poetic. Make it more actionable and direct.",
      "approved": false,
      "timestamp": "2025-10-21T10:30:30.000Z"
    },
    {
      "turn_number": 3,
      "slogan": "Hydrate Responsibly, Live Sustainably",
      "feedback": null,
      "approved": true,
      "timestamp": "2025-10-21T10:30:45.000Z"
    }
  ],
  "created_at": "2025-10-21T10:30:00.000Z",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Headers**:
- `X-Request-ID: 550e8400-e29b-41d4-a716-446655440000`

##### 202 Accepted - Request Queued

**Description**: Request queued due to concurrency limit (10 concurrent requests already in progress)

**Schema**:

```json
{
  "type": "object",
  "required": ["request_id", "status", "estimated_wait_seconds", "message"],
  "properties": {
    "request_id": {
      "type": "string",
      "format": "uuid",
      "description": "Request identifier (UUID v4) for tracking",
      "example": "550e8400-e29b-41d4-a716-446655440000"
    },
    "status": {
      "type": "string",
      "enum": ["queued"],
      "description": "Request status",
      "example": "queued"
    },
    "estimated_wait_seconds": {
      "type": "integer",
      "description": "Estimated wait time before processing starts",
      "minimum": 0,
      "example": 300
    },
    "message": {
      "type": "string",
      "description": "Human-readable status message",
      "example": "Request queued. Maximum concurrent requests reached."
    }
  }
}
```

**Example Response**:

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "estimated_wait_seconds": 300,
  "message": "Request queued. Maximum concurrent requests reached."
}
```

**Headers**:
- `X-Request-ID: 550e8400-e29b-41d4-a716-446655440000`

**Note**: This response is logged at WARNING level with details: request_id, queue depth, estimated wait time.

##### 400 Bad Request - Invalid Model

**Description**: Specified model does not exist

**Schema**:

```json
{
  "type": "object",
  "required": ["detail"],
  "properties": {
    "detail": {
      "type": "string",
      "description": "Error message with available models",
      "example": "Model 'invalid-model' not found. Available models: mistral:latest, llama3.2:latest, phi3:mini"
    }
  }
}
```

**Example Response**:

```json
{
  "detail": "Model 'invalid-model' not found. Available models: mistral:latest, llama3.2:latest, phi3:mini"
}
```

**Headers**:
- `X-Request-ID: 550e8400-e29b-41d4-a716-446655440000`

##### 422 Unprocessable Entity - Validation Error

**Description**: Request body validation failed

**Schema**:

```json
{
  "type": "object",
  "required": ["detail"],
  "properties": {
    "detail": {
      "type": "array",
      "description": "List of validation errors",
      "items": {
        "type": "object",
        "required": ["loc", "msg", "type"],
        "properties": {
          "loc": {
            "type": "array",
            "description": "Error location path",
            "items": {
              "type": ["string", "integer"]
            },
            "example": ["body", "input"]
          },
          "msg": {
            "type": "string",
            "description": "Error message",
            "example": "String should have at least 1 character"
          },
          "type": {
            "type": "string",
            "description": "Error type",
            "example": "string_too_short"
          }
        }
      }
    }
  }
}
```

**Example Response (missing input)**:

```json
{
  "detail": [
    {
      "loc": ["body", "input"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

**Example Response (input too long)**:

```json
{
  "detail": [
    {
      "loc": ["body", "input"],
      "msg": "String should have at most 500 characters",
      "type": "string_too_long"
    }
  ]
}
```

**Example Response (max_turns out of range)**:

```json
{
  "detail": [
    {
      "loc": ["body", "max_turns"],
      "msg": "Input should be greater than or equal to 1",
      "type": "greater_than_equal"
    }
  ]
}
```

**Headers**:
- `X-Request-ID: 550e8400-e29b-41d4-a716-446655440000`

##### 503 Service Unavailable - Ollama Unavailable

**Description**: Cannot connect to Ollama service

**Schema**:

```json
{
  "type": "object",
  "required": ["detail"],
  "properties": {
    "detail": {
      "type": "string",
      "description": "Error message",
      "example": "Ollama service unavailable. Please ensure Ollama is running at http://localhost:11434"
    }
  }
}
```

**Example Response**:

```json
{
  "detail": "Ollama service unavailable. Please ensure Ollama is running at http://localhost:11434"
}
```

**Headers**:
- `X-Request-ID: 550e8400-e29b-41d4-a716-446655440000`

##### 500 Internal Server Error - Unexpected Error

**Description**: Unexpected error during generation

**Schema**:

```json
{
  "type": "object",
  "required": ["detail"],
  "properties": {
    "detail": {
      "type": "string",
      "description": "Error message",
      "example": "An unexpected error occurred during slogan generation"
    }
  }
}
```

**Example Response**:

```json
{
  "detail": "An unexpected error occurred during slogan generation"
}
```

**Headers**:
- `X-Request-ID: 550e8400-e29b-41d4-a716-446655440000`

---

## Pydantic Models

These models correspond to the JSON schemas above and should be implemented in `src/api/schemas/`.

### Request Models (`requests.py`)

```python
from pydantic import BaseModel, Field

class SloganRequest(BaseModel):
    """Request schema for slogan generation."""
    
    input: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Product/topic description for slogan generation",
        examples=["eco-friendly water bottle"]
    )
    model: str | None = Field(
        default=None,
        description="Ollama model name (uses default if not specified)",
        examples=["mistral:latest"]
    )
    max_turns: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum iteration turns",
        examples=[5]
    )
    verbose: bool = Field(
        default=False,
        description="Include all iteration turns in response",
        examples=[False]
    )
```

### Response Models (`responses.py`)

```python
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field
from uuid import UUID

class TurnInfo(BaseModel):
    """Information about a single iteration turn."""
    
    turn_number: int = Field(..., ge=1, description="Iteration number (1-indexed)")
    slogan: str = Field(..., description="Slogan proposed in this turn")
    feedback: str | None = Field(None, description="Reviewer feedback (null if approved)")
    approved: bool = Field(..., description="Whether slogan was approved")
    timestamp: datetime = Field(..., description="Turn timestamp (ISO 8601)")

class SloganResponse(BaseModel):
    """Response schema for successful slogan generation."""
    
    slogan: str = Field(..., max_length=500, description="Final approved slogan")
    input: str = Field(..., description="Original user input")
    completion_reason: Literal["approved", "max_turns", "error"] = Field(
        ..., description="Reason for generation completion"
    )
    turn_count: int = Field(..., ge=1, description="Number of iterations performed")
    model_name: str = Field(..., description="Model used for generation")
    total_duration_seconds: float = Field(..., ge=0, description="Total generation time")
    average_duration_per_turn: float | None = Field(
        None, ge=0, description="Average time per iteration"
    )
    turns: list[TurnInfo] | None = Field(
        None, description="Iteration history (only if verbose=true)"
    )
    created_at: datetime = Field(..., description="Request timestamp (ISO 8601)")
    request_id: UUID = Field(..., description="Request identifier (UUID v4)")

class QueuedResponse(BaseModel):
    """Response schema for queued requests (202 Accepted)."""
    
    request_id: UUID = Field(..., description="Request identifier (UUID v4)")
    status: Literal["queued"] = Field(..., description="Request status")
    estimated_wait_seconds: int = Field(
        ..., ge=0, description="Estimated wait time before processing"
    )
    message: str = Field(..., description="Human-readable status message")

class ModelInfo(BaseModel):
    """Information about an available model."""
    
    name: str = Field(..., description="Model identifier")
    display_name: str = Field(..., description="Human-readable model name")
    is_default: bool = Field(..., description="Whether this is the default model")

class ModelsResponse(BaseModel):
    """Response schema for model listing."""
    
    models: list[ModelInfo] = Field(..., description="Available Ollama models")
    default_model: str = Field(..., description="Default model identifier")
    total_count: int = Field(..., ge=0, description="Total number of models")

class DependencyStatus(BaseModel):
    """Status of a single dependency."""
    
    connected: bool = Field(..., description="Connection status")
    url: str = Field(..., description="Dependency URL")
    response_time_ms: int | None = Field(None, ge=0, description="Response time (if connected)")
    error: str | None = Field(None, description="Error message (if not connected)")

class HealthResponse(BaseModel):
    """Response schema for health check."""
    
    status: Literal["healthy", "degraded"] = Field(..., description="Overall health status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(..., description="Health check timestamp")
    dependencies: dict[str, DependencyStatus] = Field(..., description="Dependency statuses")

class RootResponse(BaseModel):
    """Response schema for root endpoint."""
    
    name: str = Field(..., description="API name")
    version: str = Field(..., description="API version (semver)")
    description: str = Field(..., description="API description")
    documentation: dict[str, str] = Field(..., description="Documentation links")
```

---

## Error Handling Conventions

### Error Response Format

All error responses follow FastAPI's standard format:

```json
{
  "detail": "Error message or validation error array"
}
```

### HTTP Status Code Usage

| Code | Usage | When |
|------|-------|------|
| 200 | OK | Successful request |
| 202 | Accepted | Request queued (concurrency limit) |
| 400 | Bad Request | Invalid model name or business logic error |
| 422 | Unprocessable Entity | Request validation failed (Pydantic) |
| 500 | Internal Server Error | Unexpected server error |
| 503 | Service Unavailable | Dependency unavailable (Ollama) |

### Validation Error Details

Pydantic validation errors include:
- `loc`: Path to the invalid field (e.g., `["body", "input"]`)
- `msg`: Human-readable error message
- `type`: Error type identifier (e.g., `string_too_short`, `missing`)

---

## CORS Configuration

### Allowed Origins (Development)

Default: `http://localhost:3000, http://localhost:8080`  
Configurable via: `API_CORS_ORIGINS` environment variable

### Allowed Methods

- `GET`
- `POST`
- `OPTIONS`

### Allowed Headers

- `Content-Type`
- `Accept`
- `X-Request-ID` (optional in request, always in response)

---

## Rate Limiting & Concurrency

### Concurrency Limits

- **Maximum concurrent requests**: 10 simultaneous slogan generation requests
- **Overflow behavior**: Return 202 Accepted with queuing information
- **Timeout per request**: 600 seconds (10 minutes)
- **Overall request timeout**: 630 seconds (10.5 minutes)

### Rate Limiting

**Not implemented in v1** - deferred to future versions.

---

## Versioning Strategy

### URL-Based Versioning

- Current version: `/api/v1`
- Future versions: `/api/v2`, `/api/v3`, etc.
- Root endpoint (`/`) is unversioned

### Breaking Changes

Breaking changes require a new major version (`/api/v2`). Non-breaking changes (new optional fields, new endpoints) can be added to existing versions.

---

## Testing Checklist

### Contract Validation

- [ ] All request/response schemas match OpenAPI spec
- [ ] Pydantic models enforce validation rules correctly
- [ ] Error responses follow standard format
- [ ] HTTP status codes used correctly
- [ ] Headers present in all responses (X-Request-ID, CORS)

### Edge Cases

- [ ] Empty request body returns 422
- [ ] Missing required fields return 422 with details
- [ ] String length validation enforced (1-500 chars)
- [ ] Integer range validation enforced (max_turns: 1-10)
- [ ] Invalid model name returns 400 with available models
- [ ] Ollama unavailable returns 503
- [ ] Concurrent request limit returns 202 with queue info
- [ ] Timeout after 600 seconds returns error
- [ ] Request ID present in all responses (header + body where applicable)

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-21  
**Status**: Draft (Pending Approval)
