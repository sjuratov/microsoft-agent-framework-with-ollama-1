# Troubleshooting

Common issues and their solutions when using the Slogan Writer-Reviewer Agent System.

## Installation Issues

### Ollama Connection Error

**Error Message:**

```
❌ Error: Cannot connect to Ollama at http://localhost:11434
```

**Cause:** Ollama service is not running.

**Solution:**

1. Start the Ollama service:

```bash
ollama serve
```

2. Verify Ollama is running:

```bash
curl http://localhost:11434/api/tags
```

3. Check if another process is using port 11434:

```bash
lsof -i :11434  # macOS/Linux
netstat -ano | findstr :11434  # Windows
```

---

### Model Not Found

**Error Message:**

```
❌ Error: Model 'mistral' not found in Ollama
```

**Cause:** The specified model hasn't been downloaded.

**Solution:**

1. List installed models:

```bash
ollama list
```

2. Pull the missing model:

```bash
ollama pull mistral
```

3. Verify installation:

```bash
ollama list | grep mistral
```

---

### Command Not Found: slogan-gen

**Error Message:**

```
zsh: command not found: slogan-gen
```

**Cause:** Package not installed or virtual environment not activated.

**Solution:**

1. Activate virtual environment:

```bash
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

2. Reinstall package:

```bash
uv pip install -e .
```

3. Verify installation:

```bash
which slogan-gen  # Should show path in .venv
```

---

## Generation Issues

### Model Validation Errors (String Too Long)

**Error Message:**

```
❌ Workflow Error: 2 validation errors for Turn
slogan: String should have at most 500 characters
feedback: String should have at most 1000 characters
```

**Cause:** Smaller models (1B-2B parameters) like `gemma2:2b` or `gemma3:1b` may not follow instructions well and generate verbose output instead of concise slogans.

**Why This Happens:**

- Smaller models sometimes generate explanations instead of just the slogan
- They may provide overly detailed feedback with examples
- They don't consistently follow "concise output" instructions

**Solution:**

Use a larger, more instruction-following model:

```bash
# Recommended: Use mistral (7B parameters)
slogan-gen generate "coffee shop" --model mistral:latest

# Or use phi3:mini (3.8B parameters)
slogan-gen generate "coffee shop" --model phi3:mini
```

**Model Recommendations:**

| Model | Size | Instruction Following | Best For |
|-------|------|----------------------|----------|
| `gemma2:2b` | 2B | Fair | Quick testing only |
| `phi3:mini` | 3.8B | Good | Development |
| `mistral:latest` | 7B | Excellent | Production (default) |
| `llama3.2:latest` | 8B | Excellent | High quality output |

!!! note "Working as Designed"
    The validation limits (500 chars for slogans, 1000 chars for feedback) are intentionally strict to enforce quality output. Use appropriately-sized models.

---

### Slow Generation

**Issue:** Slogan generation takes too long.

**Causes:**

- Large model on CPU-only system
- Too many iterations
- System resource constraints

**Solutions:**

#### 1. Use a Smaller Model

```bash
# Fast: 2B model (5-10s for 2 turns)
slogan-gen generate "test" --model gemma2:2b

# Balanced: 7B model (15-30s for 2 turns)
slogan-gen generate "test" --model mistral
```

**Model Performance Comparison:**

| Model | Size | Typical Time (2 turns) | Quality |
|-------|------|------------------------|---------|
| `gemma2:2b` | 2B | ~5-10s | Good |
| `phi3:mini` | 3.8B | ~10-15s | Very Good |
| `mistral:latest` | 7B | ~15-30s | Excellent |
| `llama3:8b` | 8B | ~60-120s | Excellent |

#### 2. Reduce Iterations

```bash
# Limit to 3 turns instead of 5
slogan-gen generate "test" --max-turns 3
```

#### 3. Check System Resources

```bash
# Check CPU usage
top  # macOS/Linux
taskmgr  # Windows

# Close other applications
# Ensure adequate RAM available
```

#### 4. Use GPU Acceleration (If Available)

If you have an NVIDIA/AMD GPU, ensure Ollama is using it:

```bash
# Check if GPU is detected
ollama list

# Look for "Using GPU" in output
ollama serve
```

---

### Poor Quality Slogans

**Issue:** Generated slogans are generic or low quality.

**Solutions:**

#### 1. Use a Larger Model

```bash
slogan-gen generate "your input" --model llama3.2
```

#### 2. Provide More Specific Input

❌ **Vague:**
```bash
slogan-gen generate "business"
```

✅ **Specific:**
```bash
slogan-gen generate "eco-friendly cleaning products for environmentally conscious homeowners"
```

#### 3. Increase Iterations

```bash
slogan-gen generate "your input" --max-turns 7
```

#### 4. Adjust Temperature

```bash
# More creative
OLLAMA_TEMPERATURE=0.9 slogan-gen generate "your input"

# More focused
OLLAMA_TEMPERATURE=0.5 slogan-gen generate "your input"
```

---

## Runtime Errors

### Timeout Errors

**Error Message:**

```
❌ Error: Request timeout after 30 seconds
```

**Cause:** Generation took longer than configured timeout.

**Solution:**

Increase timeout:

```bash
export OLLAMA_TIMEOUT=60
slogan-gen generate "your input"
```

Or use a faster model:

```bash
slogan-gen generate "your input" --model gemma2:2b
```

---

### Max Turns Reached Without Approval

**Message:**

```
⚠️  Workflow completed without reviewer approval
📊 Reached maximum turns (5/5)
```

**Cause:** Reviewer didn't approve any slogan within iteration limit.

**This is not an error!** The system returns the best slogan from the iterations.

**To address:**

1. Increase max turns:

```bash
slogan-gen generate "your input" --max-turns 7
```

2. Use a better model:

```bash
slogan-gen generate "your input" --model mistral
```

3. Provide clearer input:

```bash
# More specific input helps
slogan-gen generate "premium organic coffee roastery targeting health-conscious millennials"
```

---

### JSON Decode Errors

**Error Message:**

```
❌ Error: Invalid JSON response from model
```

**Cause:** Model returned malformed JSON or non-JSON text.

**Solution:**

1. Use a more capable model:

```bash
slogan-gen generate "your input" --model mistral
```

2. Retry the generation:

```bash
# Sometimes works on second attempt
slogan-gen generate "your input"
```

---

## API-Specific Issues

### CORS Errors

**Error in Browser:**

```
Access to fetch at 'http://localhost:8000' has been blocked by CORS policy
```

**Solution:**

Configure CORS origins:

```bash
export API_CORS_ORIGINS="http://localhost:3000,https://yourdomain.com"
uvicorn src.api.main:app
```

---

### 422 Validation Error

**Error Response:**

```json
{
  "detail": [
    {
      "loc": ["body", "input"],
      "msg": "String should have at least 3 characters"
    }
  ]
}
```

**Cause:** Request body doesn't meet validation requirements.

**Solution:**

Check API requirements:

- `input`: 3-200 characters
- `max_turns`: 1-10
- `model`: Must be installed in Ollama

**Valid Request:**

```bash
curl -X POST http://localhost:8000/api/v1/slogans/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input": "coffee shop",
    "max_turns": 5,
    "model": "mistral:latest"
  }'
```

---

### API Timeout

**Error:**

```
504 Gateway Timeout
```

**Cause:** Generation took longer than API timeout.

**Solution:**

Increase timeout:

```bash
export API_GENERATION_TIMEOUT=900
export API_REQUEST_TIMEOUT=930
uvicorn src.api.main:app
```

Or use shorter timeout in client:

```python
import httpx

response = httpx.post(
    url,
    json=data,
    timeout=900.0  # 15 minutes
)
```

---

## Development Issues

### Import Errors

**Error Message:**

```
ModuleNotFoundError: No module named 'agents'
```

**Cause:** Package not installed in editable mode.

**Solution:**

```bash
uv pip install -e .
```

---

### Mypy Type Errors

**Error:**

```
error: Skipping analyzing "agents": module is installed, but missing library stubs
```

**Cause:** Missing `py.typed` marker files.

**Solution:**

Ensure these files exist:

```bash
touch src/py.typed
touch src/agents/py.typed
touch src/cli/py.typed
touch src/config/py.typed
touch src/orchestration/py.typed
```

---

### Test Failures

**Issue:** Tests fail with connection errors.

**Solution:**

Ensure Ollama is running:

```bash
ollama serve
```

Pull required test model:

```bash
ollama pull mistral:latest
```

---

## Platform-Specific Issues

### macOS: Permission Denied

**Error:**

```
Permission denied: '/usr/local/bin/slogan-gen'
```

**Solution:**

```bash
sudo chmod +x /usr/local/bin/slogan-gen
```

Or install in user directory:

```bash
uv pip install --user -e .
```

---

### Windows: Script Execution Policy

**Error:**

```
cannot be loaded because running scripts is disabled
```

**Solution:**

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### Linux: GLIBC Version Error

**Error:**

```
version 'GLIBC_2.XX' not found
```

**Cause:** System GLIBC too old for Ollama.

**Solution:**

Upgrade system or use Docker:

```bash
docker run -d -p 11434:11434 ollama/ollama
```

---

## Getting More Help

### Enable Debug Logging

```bash
# CLI
slogan-gen generate "test" --verbose

# API
export API_LOG_LEVEL=DEBUG
uvicorn src.api.main:app
```

### Check System Status

```bash
# Check Ollama
ollama list
curl http://localhost:11434/api/tags

# Check configuration
slogan-gen config show

# Check models
slogan-gen models
```

### Report an Issue

If you've tried everything and still have issues:

1. Check [existing issues on GitHub](https://github.com/your-repo/issues)
2. Create a new issue with:
   - Error message (full output)
   - Command you ran
   - System info (OS, Python version)
   - Ollama version: `ollama --version`
   - Configuration: `slogan-gen config show`

### Additional Resources

- [Installation Guide](getting-started/installation.md)
- [Configuration Guide](getting-started/configuration.md)
- [CLI Usage Guide](guides/cli-usage.md)
- [API Usage Guide](guides/api-usage.md)
- [Development Guide](guides/development.md)
