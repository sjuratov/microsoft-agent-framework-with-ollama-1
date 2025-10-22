# OpenAPI Specification

This page provides access to the OpenAPI specification for the Slogan Writer-Reviewer API.

## Interactive Documentation

The API provides multiple ways to explore and interact with the OpenAPI specification:

### Swagger UI (Recommended)

**URL**: [`http://localhost:8000/docs`](http://localhost:8000/docs)

Interactive documentation with:
- Try-it-out functionality for all endpoints
- Request/response examples
- Schema definitions
- Authentication testing
- Download OpenAPI spec

**Features**:
- ✅ Test endpoints directly from browser
- ✅ See request/response in real-time
- ✅ Explore schemas and models
- ✅ Copy cURL commands

### ReDoc

**URL**: [`http://localhost:8000/redoc`](http://localhost:8000/redoc)

Clean, responsive documentation with:
- Three-column layout
- Search functionality
- Deep linking
- Code samples in multiple languages

**Features**:
- ✅ Better for reading/browsing
- ✅ More polished UI
- ✅ Mobile-friendly
- ✅ Printable format

### Raw OpenAPI Spec

**URL**: [`http://localhost:8000/openapi.json`](http://localhost:8000/openapi.json)

Download the raw OpenAPI 3.1.0 specification in JSON format for:
- Code generation (client libraries)
- API testing tools (Postman, Insomnia)
- Documentation generators
- Contract testing

---

## API Overview

**API Name**: Slogan Writer-Reviewer API  
**Version**: 1.0.0  
**OpenAPI Version**: 3.1.0  
**Base URL**: `http://localhost:8000`

### Endpoints

| Method | Path | Description | Tags |
|--------|------|-------------|------|
| `GET` | `/` | API information and documentation links | info |
| `GET` | `/api/v1/health` | Health check for API and dependencies | monitoring |
| `GET` | `/api/v1/models` | List available Ollama models | models |
| `POST` | `/api/v1/slogans/generate` | Generate slogan via Writer-Reviewer | slogans |

### Request/Response Formats

**Content Type**: `application/json`

**Request Schemas**:
- `GenerateRequest`: Slogan generation request

**Response Schemas**:
- `RootResponse`: API information
- `HealthResponse`: Health check status
- `ModelsResponse`: Available models list
- `GenerateResponse`: Generated slogan with metadata
- `DependencyStatus`: Dependency health status
- `ModelInfo`: Model information
- `TurnDetail`: Iteration turn details

**Error Schemas**:
- `HTTPValidationError`: Pydantic validation errors (422)
- Standard HTTP error responses (400, 500, 503, 504)

---

## Using the OpenAPI Spec

### Swagger UI Examples

#### 1. Try the Health Endpoint

1. Go to [`http://localhost:8000/docs`](http://localhost:8000/docs)
2. Expand `GET /api/v1/health`
3. Click **"Try it out"**
4. Click **"Execute"**
5. View the response

#### 2. Generate a Slogan

1. Go to [`http://localhost:8000/docs`](http://localhost:8000/docs)
2. Expand `POST /api/v1/slogans/generate`
3. Click **"Try it out"**
4. Edit the request body:
   ```json
   {
     "input": "eco-friendly water bottles",
     "verbose": true
   }
   ```
5. Click **"Execute"**
6. View the generated slogan and turn history

#### 3. Test Different Models

1. First, get available models from `GET /api/v1/models`
2. Note the model names (e.g., `gemma2:2b`, `mistral:latest`)
3. Use a model in `POST /api/v1/slogans/generate`:
   ```json
   {
     "input": "smart home devices",
     "model": "gemma2:2b",
     "max_turns": 3
   }
   ```

### ReDoc Examples

#### Browse API Structure

1. Go to [`http://localhost:8000/redoc`](http://localhost:8000/redoc)
2. Use left sidebar to navigate between endpoints
3. Click any endpoint to see details
4. Expand **"Schema"** sections to see data models
5. Use search (Ctrl/Cmd + K) to find specific endpoints or schemas

#### Copy Code Samples

1. Navigate to any endpoint in ReDoc
2. Scroll to **"Code samples"** section
3. Switch between languages (cURL, Python, JavaScript, etc.)
4. Click **"Copy"** to copy the code sample
5. Paste into your application

### Download OpenAPI Spec

#### For Code Generation

```bash
# Download the spec
curl http://localhost:8000/openapi.json > openapi.json

# Generate Python client
openapi-generator-cli generate \
  -i openapi.json \
  -g python \
  -o ./client

# Generate TypeScript client
openapi-generator-cli generate \
  -i openapi.json \
  -g typescript-axios \
  -o ./client
```

#### For Postman/Insomnia

1. Download spec: `curl http://localhost:8000/openapi.json > openapi.json`
2. **Postman**:
   - File → Import
   - Select `openapi.json`
   - Choose "OpenAPI 3.0"
   - All endpoints imported as collection
3. **Insomnia**:
   - Application → Import/Export → Import Data
   - Select `openapi.json`
   - All endpoints imported

#### For API Testing

```bash
# Using dredd (API contract testing)
dredd openapi.json http://localhost:8000

# Using schemathesis (property-based testing)
schemathesis run http://localhost:8000/openapi.json
```

---

## OpenAPI Schema Details

### Security

**Current Status**: No authentication required (development)

**Future**: Will support API key authentication

```yaml
# Planned security scheme
securitySchemes:
  ApiKeyAuth:
    type: apiKey
    in: header
    name: X-API-Key
```

### Tags

Endpoints are organized by tags:

| Tag | Description | Endpoints |
|-----|-------------|-----------|
| `info` | API information | `/` |
| `monitoring` | Health checks | `/api/v1/health` |
| `models` | Model management | `/api/v1/models` |
| `slogans` | Slogan generation | `/api/v1/slogans/generate` |

### Servers

**Development**:
```yaml
servers:
  - url: http://localhost:8000
    description: Local development server
```

**Production** (example):
```yaml
servers:
  - url: https://api.example.com
    description: Production server
  - url: https://staging-api.example.com
    description: Staging server
```

---

## Validating the OpenAPI Spec

### Using OpenAPI Validator

```bash
# Install validator
npm install -g @apidevtools/swagger-cli

# Validate spec
swagger-cli validate http://localhost:8000/openapi.json
```

### Using Spectral (OpenAPI Linter)

```bash
# Install Spectral
npm install -g @stoplight/spectral-cli

# Lint the spec
spectral lint http://localhost:8000/openapi.json
```

### Using online validators

1. **Swagger Editor**: https://editor.swagger.io/
   - Paste spec JSON
   - See validation errors in right panel
   - Preview documentation

2. **Redocly Editor**: https://redocly.com/docs/api-reference-docs/
   - Upload `openapi.json`
   - Get detailed validation report
   - Preview interactive docs

---

## Extending the OpenAPI Spec

### Adding Examples

Edit endpoint docstrings in source code:

```python
@router.post("/slogans/generate", response_model=GenerateResponse)
async def generate_slogan(request_body: GenerateRequest) -> GenerateResponse:
    """
    Generate a slogan through Writer-Reviewer collaboration.
    
    Example request:
    ```json
    {
      "input": "eco-friendly water bottles",
      "verbose": true
    }
    ```
    
    Example response:
    ```json
    {
      "slogan": "Stay Hydrated, Save the Planet",
      "completion_reason": "approved",
      "turn_count": 2
    }
    ```
    """
    ...
```

### Adding Security Definitions

In `src/api/main.py`:

```python
from fastapi import FastAPI, Security
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

app = FastAPI(
    title="Slogan Writer-Reviewer API",
    version="1.0.0",
    # Add security schemes
    openapi_tags=[
        {"name": "slogans", "description": "Slogan generation operations"}
    ]
)

@app.post("/api/v1/slogans/generate")
async def generate_slogan(
    request_body: GenerateRequest,
    api_key: str = Security(api_key_header)  # Require API key
):
    ...
```

### Customizing OpenAPI Output

```python
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Slogan Writer-Reviewer API",
        version="1.0.0",
        description="Multi-agent slogan generation",
        routes=app.routes,
    )
    
    # Add custom fields
    openapi_schema["info"]["x-logo"] = {
        "url": "https://example.com/logo.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

---

## Troubleshooting

### Swagger UI Not Loading

**Problem**: `/docs` shows blank page or 404

**Solution**:
```bash
# Ensure FastAPI is running
uvicorn src.api.main:app --reload

# Check if Swagger UI is enabled
# In src/api/main.py, ensure docs_url is not disabled:
app = FastAPI(
    title="...",
    docs_url="/docs",  # Must not be None
    redoc_url="/redoc"
)
```

### OpenAPI Spec Invalid

**Problem**: Validation errors in spec

**Solution**:
```bash
# Regenerate spec
curl http://localhost:8000/openapi.json > openapi.json

# Validate
swagger-cli validate openapi.json

# Fix validation errors in source code docstrings
```

### CORS Errors in Swagger UI

**Problem**: "Failed to fetch" errors when trying endpoints

**Solution**:
```bash
# Set CORS origins to allow Swagger UI
export API_CORS_ORIGINS="*"

# Or specific origin
export API_CORS_ORIGINS="http://localhost:8000"

# Restart API
uvicorn src.api.main:app --reload
```

### Missing Schemas

**Problem**: Schemas not showing in OpenAPI spec

**Solution**:
```python
# Ensure response_model is specified
@app.get("/endpoint", response_model=MyResponse)
async def endpoint() -> MyResponse:  # Type hint required
    ...

# Ensure Pydantic models have proper Config
class MyResponse(BaseModel):
    field: str
    
    class Config:
        json_schema_extra = {
            "example": {"field": "example value"}
        }
```

---

## See Also

- [REST API Reference](rest-api.md) - Detailed REST API documentation
- [API Usage Guide](../guides/api-usage.md) - How to use the API
- [Development Guide](../guides/development.md) - API development setup
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - FastAPI framework docs
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html) - OpenAPI standard
