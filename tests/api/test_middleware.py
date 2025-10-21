"""Tests for middleware and exception handlers."""

from fastapi.testclient import TestClient


def test_request_id_header_added(client: TestClient) -> None:
    """Test that X-Request-ID header is added to responses."""
    response = client.get("/")

    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"]  # Not empty


def test_custom_request_id_preserved(client: TestClient) -> None:
    """Test that custom X-Request-ID from request is preserved."""
    custom_id = "test-request-id-123"

    response = client.get("/", headers={"X-Request-ID": custom_id})

    assert response.headers.get("X-Request-ID") == custom_id


def test_validation_error_includes_request_id(client: TestClient) -> None:
    """Test that validation errors include X-Request-ID."""
    response = client.post(
        "/api/v1/slogans/generate",
        json={}  # Missing required 'input' field
    )

    assert response.status_code == 422
    assert "X-Request-ID" in response.headers


def test_http_error_includes_request_id(client: TestClient) -> None:
    """Test that HTTP errors include X-Request-ID."""
    response = client.get("/nonexistent-endpoint")

    assert response.status_code == 404
    assert "X-Request-ID" in response.headers


def test_cors_headers_present(client: TestClient) -> None:
    """Test that CORS headers are properly configured."""
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        }
    )

    # CORS headers should be present
    assert "access-control-allow-origin" in response.headers
