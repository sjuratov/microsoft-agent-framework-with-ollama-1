# API Client Examples

This guide provides comprehensive examples for consuming the Slogan Writer-Reviewer API from various programming languages and tools.

## Quick Start

### Prerequisites

- API running at `http://localhost:8000`
- Ollama running with at least one model installed
- HTTP client library for your language

### Basic Request Flow

1. **Health Check**: Verify API is running
2. **List Models**: Get available models
3. **Generate Slogan**: Create a slogan with Writer-Reviewer workflow

---

## Python Examples

### Using httpx (Recommended)

#### Installation

```bash
pip install httpx
```

#### Basic Synchronous Example

```python
import httpx

# Configure API base URL
BASE_URL = "http://localhost:8000"

# Create client
client = httpx.Client(base_url=BASE_URL)

# Health check
health = client.get("/api/v1/health")
print(f"Status: {health.json()['status']}")

# List models
models = client.get("/api/v1/models")
print(f"Available models: {[m['name'] for m in models.json()['models']]}")

# Generate slogan
response = client.post(
    "/api/v1/slogans/generate",
    json={
        "input": "eco-friendly water bottles",
        "verbose": False
    }
)

result = response.json()
print(f"Slogan: {result['slogan']}")
print(f"Turns: {result['turn_count']}")
print(f"Duration: {result['total_duration_seconds']}s")

# Close client
client.close()
```

#### Async Example

```python
import asyncio
import httpx

async def generate_slogan(product: str) -> dict:
    """Generate a slogan asynchronously."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/slogans/generate",
            json={"input": product, "verbose": True}
        )
        response.raise_for_status()
        return response.json()

async def main():
    # Generate multiple slogans concurrently
    products = [
        "smart home devices",
        "organic coffee",
        "fitness tracker"
    ]
    
    tasks = [generate_slogan(p) for p in products]
    results = await asyncio.gather(*tasks)
    
    for product, result in zip(products, results):
        print(f"\n{product}:")
        print(f"  Slogan: {result['slogan']}")
        print(f"  Turns: {result['turn_count']}")

# Run async function
asyncio.run(main())
```

#### Error Handling

```python
import httpx

def generate_with_retry(product: str, max_retries: int = 3) -> dict:
    """Generate slogan with retry logic."""
    client = httpx.Client(timeout=620.0)  # Slightly > server timeout
    
    for attempt in range(max_retries):
        try:
            response = client.post(
                "http://localhost:8000/api/v1/slogans/generate",
                json={"input": product}
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 503:
                print(f"Attempt {attempt + 1}: Service unavailable")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
            elif e.response.status_code == 422:
                print(f"Validation error: {e.response.json()}")
                raise
            elif e.response.status_code == 504:
                print(f"Timeout: Generation took too long")
                raise
            else:
                print(f"HTTP error: {e.response.status_code}")
                raise
                
        except httpx.TimeoutException:
            print(f"Attempt {attempt + 1}: Request timeout")
            if attempt < max_retries - 1:
                continue
            raise
            
        except httpx.RequestError as e:
            print(f"Connection error: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise
    
    raise Exception("Max retries exceeded")
```

#### Context Manager

```python
import httpx
from contextlib import contextmanager

@contextmanager
def slogan_api_client(base_url: str = "http://localhost:8000"):
    """Context manager for API client."""
    client = httpx.Client(base_url=base_url, timeout=620.0)
    try:
        # Verify health
        health = client.get("/api/v1/health")
        if health.json()["status"] != "healthy":
            raise RuntimeError("API not healthy")
        yield client
    finally:
        client.close()

# Usage
with slogan_api_client() as client:
    response = client.post(
        "/api/v1/slogans/generate",
        json={"input": "cloud storage"}
    )
    print(response.json()["slogan"])
```

---

### Using requests

#### Installation

```bash
pip install requests
```

#### Basic Example

```python
import requests

# Generate slogan
response = requests.post(
    "http://localhost:8000/api/v1/slogans/generate",
    json={
        "input": "sustainable fashion",
        "model": "mistral:latest",
        "max_turns": 5,
        "verbose": True
    },
    timeout=620
)

# Check status
response.raise_for_status()

# Parse response
data = response.json()
print(f"Slogan: {data['slogan']}")

# Print iteration history
if data['turns']:
    print(f"\nIteration History ({len(data['turns'])} turns):")
    for turn in data['turns']:
        status = "✓" if turn['approved'] else "✗"
        print(f"  {status} Turn {turn['turn_number']}: {turn['slogan']}")
        if turn['feedback']:
            print(f"    Feedback: {turn['feedback']}")
```

#### Session with Custom Headers

```python
import requests
import uuid

# Create session with custom headers
session = requests.Session()
session.headers.update({
    "X-Request-ID": str(uuid.uuid4()),
    "User-Agent": "MyApp/1.0"
})

# All requests use these headers
response = session.post(
    "http://localhost:8000/api/v1/slogans/generate",
    json={"input": "AI assistant"}
)

print(f"Request ID: {response.headers.get('X-Request-ID')}")
print(f"Slogan: {response.json()['slogan']}")

session.close()
```

---

## JavaScript/TypeScript Examples

### Using fetch (Browser/Node.js)

#### Basic Example

```javascript
const BASE_URL = 'http://localhost:8000';

async function generateSlogan(input, options = {}) {
  const response = await fetch(`${BASE_URL}/api/v1/slogans/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      input,
      model: options.model,
      max_turns: options.maxTurns,
      verbose: options.verbose || false
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(`API Error: ${JSON.stringify(error)}`);
  }

  return await response.json();
}

// Usage
(async () => {
  try {
    const result = await generateSlogan('smart home devices', {
      verbose: true
    });
    
    console.log(`Slogan: ${result.slogan}`);
    console.log(`Turns: ${result.turn_count}`);
    console.log(`Duration: ${result.total_duration_seconds}s`);
    
    if (result.turns) {
      console.log('\nIteration History:');
      result.turns.forEach(turn => {
        console.log(`  ${turn.approved ? '✓' : '✗'} Turn ${turn.turn_number}: ${turn.slogan}`);
      });
    }
  } catch (error) {
    console.error('Failed to generate slogan:', error);
  }
})();
```

#### TypeScript with Types

```typescript
interface GenerateRequest {
  input: string;
  model?: string;
  max_turns?: number;
  verbose?: boolean;
}

interface TurnDetail {
  turn_number: number;
  slogan: string;
  feedback: string | null;
  approved: boolean;
  timestamp: string;
}

interface GenerateResponse {
  slogan: string;
  input: string;
  completion_reason: 'approved' | 'max_turns' | 'error';
  turn_count: number;
  model_name: string;
  total_duration_seconds: number;
  average_duration_per_turn: number;
  turns: TurnDetail[] | null;
  created_at: string;
  request_id: string | null;
}

class SloganAPIClient {
  private baseURL: string;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.baseURL = baseURL;
  }

  async health(): Promise<any> {
    const response = await fetch(`${this.baseURL}/api/v1/health`);
    return await response.json();
  }

  async models(): Promise<any> {
    const response = await fetch(`${this.baseURL}/api/v1/models`);
    return await response.json();
  }

  async generate(request: GenerateRequest): Promise<GenerateResponse> {
    const response = await fetch(`${this.baseURL}/api/v1/slogans/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  }
}

// Usage
const client = new SloganAPIClient();

(async () => {
  // Check health
  const health = await client.health();
  console.log('API Status:', health.status);

  // Generate slogan
  const result = await client.generate({
    input: 'eco-friendly products',
    verbose: true
  });

  console.log('Slogan:', result.slogan);
})();
```

---

### Using axios

#### Installation

```bash
npm install axios
```

#### Example with Interceptors

```javascript
const axios = require('axios');

// Create axios instance
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 620000,  // 620 seconds
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor (add request ID)
api.interceptors.request.use(
  (config) => {
    config.headers['X-Request-ID'] = crypto.randomUUID();
    console.log(`→ ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor (logging)
api.interceptors.response.use(
  (response) => {
    console.log(`← ${response.status} (${response.headers['x-request-id']})`);
    return response;
  },
  (error) => {
    if (error.response) {
      console.error(`✗ ${error.response.status}: ${error.response.statusText}`);
    } else {
      console.error(`✗ Network error: ${error.message}`);
    }
    return Promise.reject(error);
  }
);

// Generate slogan
async function generateSlogan(input, options = {}) {
  try {
    const response = await api.post('/api/v1/slogans/generate', {
      input,
      ...options
    });
    return response.data;
  } catch (error) {
    if (error.response?.status === 503) {
      throw new Error('API service unavailable');
    } else if (error.response?.status === 422) {
      throw new Error(`Validation error: ${JSON.stringify(error.response.data)}`);
    }
    throw error;
  }
}

// Usage
(async () => {
  const result = await generateSlogan('coffee subscription', {
    model: 'mistral:latest',
    verbose: true
  });
  console.log('Slogan:', result.slogan);
})();
```

---

## cURL Examples

### Basic Request

```bash
# Health check
curl http://localhost:8000/api/v1/health

# List models
curl http://localhost:8000/api/v1/models

# Generate slogan (basic)
curl -X POST http://localhost:8000/api/v1/slogans/generate \
  -H "Content-Type: application/json" \
  -d '{"input": "eco-friendly water bottles"}'
```

### Verbose Mode

```bash
curl -X POST http://localhost:8000/api/v1/slogans/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input": "smart home devices",
    "verbose": true
  }' | jq .
```

### Custom Model and Turns

```bash
curl -X POST http://localhost:8000/api/v1/slogans/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input": "organic skincare",
    "model": "gemma2:2b",
    "max_turns": 3
  }' | jq '{slogan: .slogan, turns: .turn_count}'
```

### With Custom Request ID

```bash
REQUEST_ID=$(uuidgen)
curl -X POST http://localhost:8000/api/v1/slogans/generate \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: $REQUEST_ID" \
  -d '{"input": "coffee roastery"}' \
  | jq -r '.slogan'

echo "Request ID: $REQUEST_ID"
```

### Save Response to File

```bash
curl -X POST http://localhost:8000/api/v1/slogans/generate \
  -H "Content-Type: application/json" \
  -d '{"input": "digital art marketplace", "verbose": true}' \
  -o response.json

# Pretty print
jq . response.json
```

### Error Handling

```bash
# Check exit code
curl -f -X POST http://localhost:8000/api/v1/slogans/generate \
  -H "Content-Type: application/json" \
  -d '{"input": "test"}' \
  || echo "Request failed with exit code $?"

# Show error details
curl -X POST http://localhost:8000/api/v1/slogans/generate \
  -H "Content-Type: application/json" \
  -d '{"input": ""}' \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | jq .
```

---

## Shell Script Example

### Batch Slogan Generation

```bash
#!/bin/bash

# batch_generate.sh - Generate slogans for multiple products

API_URL="http://localhost:8000/api/v1/slogans/generate"
OUTPUT_DIR="./slogans"
MODEL="mistral:latest"
MAX_TURNS=5

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Products list
products=(
  "eco-friendly water bottles"
  "smart home devices"
  "organic coffee"
  "fitness tracker"
  "cloud storage"
)

# Check API health
echo "Checking API health..."
health_status=$(curl -s http://localhost:8000/api/v1/health | jq -r '.status')

if [ "$health_status" != "healthy" ]; then
  echo "Error: API is not healthy (status: $health_status)"
  exit 1
fi

echo "API is healthy. Starting batch generation..."
echo

# Generate slogans
for product in "${products[@]}"; do
  echo "Generating slogan for: $product"
  
  # Generate filename
  filename="${OUTPUT_DIR}/$(echo "$product" | tr ' ' '_').json"
  
  # Make request
  response=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d "{
      \"input\": \"$product\",
      \"model\": \"$MODEL\",
      \"max_turns\": $MAX_TURNS,
      \"verbose\": true
    }")
  
  # Check if successful
  if echo "$response" | jq -e '.slogan' > /dev/null 2>&1; then
    # Save to file
    echo "$response" | jq . > "$filename"
    
    # Extract slogan
    slogan=$(echo "$response" | jq -r '.slogan')
    turns=$(echo "$response" | jq -r '.turn_count')
    
    echo "  ✓ Slogan: $slogan"
    echo "  ✓ Turns: $turns"
    echo "  ✓ Saved to: $filename"
  else
    echo "  ✗ Failed: $response"
  fi
  
  echo
done

echo "Batch generation complete!"
echo "Results saved in: $OUTPUT_DIR"
```

---

## Go Example

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "net/http"
    "time"
)

type GenerateRequest struct {
    Input    string `json:"input"`
    Model    string `json:"model,omitempty"`
    MaxTurns int    `json:"max_turns,omitempty"`
    Verbose  bool   `json:"verbose,omitempty"`
}

type GenerateResponse struct {
    Slogan                 string  `json:"slogan"`
    Input                  string  `json:"input"`
    CompletionReason       string  `json:"completion_reason"`
    TurnCount              int     `json:"turn_count"`
    ModelName              string  `json:"model_name"`
    TotalDurationSeconds   float64 `json:"total_duration_seconds"`
    AverageDurationPerTurn float64 `json:"average_duration_per_turn"`
    CreatedAt              string  `json:"created_at"`
    RequestID              string  `json:"request_id"`
}

type SloganClient struct {
    BaseURL    string
    HTTPClient *http.Client
}

func NewSloganClient(baseURL string) *SloganClient {
    return &SloganClient{
        BaseURL: baseURL,
        HTTPClient: &http.Client{
            Timeout: 620 * time.Second,
        },
    }
}

func (c *SloganClient) Generate(req GenerateRequest) (*GenerateResponse, error) {
    // Marshal request
    body, err := json.Marshal(req)
    if err != nil {
        return nil, fmt.Errorf("marshal request: %w", err)
    }

    // Create HTTP request
    httpReq, err := http.NewRequest(
        "POST",
        c.BaseURL+"/api/v1/slogans/generate",
        bytes.NewBuffer(body),
    )
    if err != nil {
        return nil, fmt.Errorf("create request: %w", err)
    }

    httpReq.Header.Set("Content-Type", "application/json")

    // Send request
    resp, err := c.HTTPClient.Do(httpReq)
    if err != nil {
        return nil, fmt.Errorf("send request: %w", err)
    }
    defer resp.Body.Close()

    // Read response
    respBody, err := io.ReadAll(resp.Body)
    if err != nil {
        return nil, fmt.Errorf("read response: %w", err)
    }

    // Check status
    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("API error %d: %s", resp.StatusCode, string(respBody))
    }

    // Parse response
    var result GenerateResponse
    if err := json.Unmarshal(respBody, &result); err != nil {
        return nil, fmt.Errorf("unmarshal response: %w", err)
    }

    return &result, nil
}

func main() {
    client := NewSloganClient("http://localhost:8000")

    result, err := client.Generate(GenerateRequest{
        Input:   "eco-friendly water bottles",
        Verbose: false,
    })
    if err != nil {
        fmt.Printf("Error: %v\n", err)
        return
    }

    fmt.Printf("Slogan: %s\n", result.Slogan)
    fmt.Printf("Turns: %d\n", result.TurnCount)
    fmt.Printf("Duration: %.2fs\n", result.TotalDurationSeconds)
}
```

---

## Best Practices

### 1. Always Check Health First

```python
# Python
def ensure_api_ready(client):
    health = client.get("/api/v1/health").json()
    if health["status"] != "healthy":
        raise RuntimeError("API not ready")
```

```bash
# Shell
if [ "$(curl -s http://localhost:8000/api/v1/health | jq -r '.status')" != "healthy" ]; then
  echo "API not ready"
  exit 1
fi
```

### 2. Use Appropriate Timeouts

```python
# Slightly longer than server timeout (600s)
client = httpx.Client(timeout=620.0)
```

### 3. Handle Errors Gracefully

```javascript
try {
  const result = await generateSlogan(input);
} catch (error) {
  if (error.response?.status === 503) {
    console.error('Service unavailable. Is Ollama running?');
  } else if (error.response?.status === 422) {
    console.error('Validation error:', error.response.data);
  } else {
    console.error('Unexpected error:', error);
  }
}
```

### 4. Use Request IDs for Tracking

```python
import uuid

request_id = str(uuid.uuid4())
response = client.post(
    url,
    json={"input": text},
    headers={"X-Request-ID": request_id}
)
# Log request_id for debugging
```

### 5. Retry with Backoff

```python
import time

for attempt in range(3):
    try:
        result = client.post(url, json=data)
        break
    except ConnectionError:
        if attempt < 2:
            time.sleep(2 ** attempt)  # 1s, 2s, 4s
            continue
        raise
```

---

## See Also

- [REST API Reference](../api-reference/rest-api.md) - API endpoint documentation
- [OpenAPI Spec](../api-reference/openapi.md) - Interactive API documentation
- [API Usage Guide](api-usage.md) - Complete API usage guide
- [Development Guide](development.md) - API development setup
