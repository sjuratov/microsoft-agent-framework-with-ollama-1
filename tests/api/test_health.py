"""Tests for health check endpoint."""

import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test root endpoint returns API metadata."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Slogan Writer-Reviewer API"
    assert data["version"] == "1.0.0"
    assert "documentation" in data
    assert data["documentation"]["swagger"] == "/docs"
    assert data["documentation"]["redoc"] == "/redoc"
    assert data["documentation"]["openapi"] == "/openapi.json"


def test_root_response_schema(client: TestClient):
    """Test root endpoint response matches schema."""
    response = client.get("/")
    data = response.json()

    # Verify required fields present
    assert "name" in data
    assert "version" in data
    assert "description" in data
    assert "documentation" in data


def test_health_endpoint_response_structure(client: TestClient):
    """Test health endpoint returns expected structure."""
    response = client.get("/api/v1/health")

    # Should return either 200 or 503 depending on Ollama availability
    assert response.status_code in [200, 503]

    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "degraded"]
    assert "version" in data
    assert "timestamp" in data
    assert "dependencies" in data
    assert "ollama" in data["dependencies"]

    ollama = data["dependencies"]["ollama"]
    assert "connected" in ollama
    assert "url" in ollama
    assert isinstance(ollama["connected"], bool)


def test_health_response_schema_when_healthy(client: TestClient):
    """Test health response includes response_time_ms when connected."""
    response = client.get("/api/v1/health")
    data = response.json()

    ollama = data["dependencies"]["ollama"]
    if ollama["connected"]:
        # When connected, should have response_time_ms
        assert "response_time_ms" in ollama
        assert isinstance(ollama["response_time_ms"], int)
        assert ollama["response_time_ms"] >= 0
        assert response.status_code == 200
        assert data["status"] == "healthy"


def test_health_response_schema_when_degraded(client: TestClient):
    """Test health response includes error when not connected."""
    response = client.get("/api/v1/health")
    data = response.json()

    ollama = data["dependencies"]["ollama"]
    if not ollama["connected"]:
        # When not connected, should have error message
        assert "error" in ollama
        assert isinstance(ollama["error"], str)
        assert response.status_code == 503
        assert data["status"] == "degraded"
