"""End-to-end integration tests for the API."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_api_root_and_health_flow(client: TestClient) -> None:
    """Test basic API discovery flow: root -> health check."""
    # Step 1: Get API info from root
    root_response = client.get("/")
    assert root_response.status_code == 200

    root_data = root_response.json()
    assert root_data["name"] == "Slogan Writer-Reviewer API"
    assert root_data["version"] == "1.0.0"
    assert "swagger" in root_data["documentation"]

    # Verify X-Request-ID is present
    assert "X-Request-ID" in root_response.headers

    # Step 2: Check health status
    health_response = client.get("/api/v1/health")
    assert health_response.status_code in [200, 503]  # Healthy or degraded

    health_data = health_response.json()
    assert health_data["status"] in ["healthy", "degraded"]
    assert "dependencies" in health_data
    assert "ollama" in health_data["dependencies"]


@pytest.mark.integration
def test_models_discovery_and_validation(client: TestClient) -> None:
    """Test model discovery flow: list models -> validate against generation."""
    # Step 1: Get available models
    models_response = client.get("/api/v1/models")

    # Should succeed even if Ollama is unavailable (will return error)
    if models_response.status_code == 200:
        models_data = models_response.json()
        assert "models" in models_data
        assert "default_model" in models_data
        assert isinstance(models_data["models"], list)

        # If models available, try using the default model
        if models_data["models"]:
            default_model = models_data["default_model"]
            assert default_model  # Should not be empty


@pytest.mark.integration
def test_full_generation_flow_with_verbose(client: TestClient) -> None:
    """Test complete generation flow with verbose output."""
    # This test requires Ollama to be running, so we mock it
    from unittest.mock import patch

    from src.orchestration.models import CompletionReason, IterationSession

    # Create a realistic mock session
    session = IterationSession(
        user_input="innovative smartphone",
        model_name="mistral:latest",
    )

    session.add_turn(
        slogan="Smart. Simple. Powerful.",
        feedback="Good start but too generic",
        approved=False,
    )
    session.add_turn(
        slogan="Innovation in Your Pocket",
        feedback=None,
        approved=True,
    )
    session.complete(CompletionReason.APPROVED)

    with patch("src.api.routes.generate.run_generation_async") as mock_run:
        mock_run.return_value = session

        # Step 1: Submit generation request with verbose mode
        response = client.post(
            "/api/v1/slogans/generate",
            json={
                "input": "innovative smartphone",
                "verbose": True,
                "max_turns": 5
            }
        )

        assert response.status_code == 200
        assert "X-Request-ID" in response.headers

        data = response.json()

        # Verify response structure
        assert data["slogan"] == "Innovation in Your Pocket"
        assert data["input"] == "innovative smartphone"
        assert data["completion_reason"] == "approved"
        assert data["turn_count"] == 2
        assert data["model_name"] == "mistral:latest"

        # Verify verbose mode includes turns
        assert "turns" in data
        assert data["turns"] is not None
        assert len(data["turns"]) == 2

        # Verify turn details
        first_turn = data["turns"][0]
        assert first_turn["turn_number"] == 1
        assert first_turn["slogan"] == "Smart. Simple. Powerful."
        assert first_turn["approved"] is False

        second_turn = data["turns"][1]
        assert second_turn["turn_number"] == 2
        assert second_turn["approved"] is True


@pytest.mark.integration
def test_error_handling_flow(client: TestClient) -> None:
    """Test error handling across different endpoints."""
    # Test 1: Validation error (422)
    validation_response = client.post(
        "/api/v1/slogans/generate",
        json={"input": ""}  # Empty input
    )
    assert validation_response.status_code == 422
    assert "X-Request-ID" in validation_response.headers
    assert "detail" in validation_response.json()

    # Test 2: Invalid model (400)
    from unittest.mock import patch

    with patch("src.api.routes.generate.get_available_models") as mock_models:
        mock_models.return_value = ["mistral:latest", "llama2:7b"]

        invalid_model_response = client.post(
            "/api/v1/slogans/generate",
            json={
                "input": "test product",
                "model": "nonexistent-model"
            }
        )
        assert invalid_model_response.status_code == 400
        assert "X-Request-ID" in invalid_model_response.headers
        assert "nonexistent-model" in invalid_model_response.json()["detail"]

    # Test 3: Not found (404)
    not_found_response = client.get("/nonexistent")
    assert not_found_response.status_code == 404
    assert "X-Request-ID" in not_found_response.headers


@pytest.mark.integration
def test_request_id_propagation(client: TestClient) -> None:
    """Test that request ID propagates through the entire request lifecycle."""
    custom_request_id = "test-integration-flow-123"

    # Make request with custom X-Request-ID
    response = client.get(
        "/api/v1/health",
        headers={"X-Request-ID": custom_request_id}
    )

    # Verify same ID is returned
    assert response.headers.get("X-Request-ID") == custom_request_id


@pytest.mark.integration
def test_cors_preflight_request(client: TestClient) -> None:
    """Test CORS preflight (OPTIONS) request handling."""
    response = client.options(
        "/api/v1/models",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type",
        }
    )

    # Should allow the request
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


@pytest.mark.integration
def test_openapi_schema_available(client: TestClient) -> None:
    """Test that OpenAPI schema is accessible."""
    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()

    # Verify basic OpenAPI structure
    assert "openapi" in schema
    assert "info" in schema
    assert schema["info"]["title"] == "Slogan Writer-Reviewer API"
    assert schema["info"]["version"] == "1.0.0"

    # Verify our endpoints are documented
    assert "paths" in schema
    assert "/" in schema["paths"]
    assert "/api/v1/health" in schema["paths"]
    assert "/api/v1/models" in schema["paths"]
    assert "/api/v1/slogans/generate" in schema["paths"]


@pytest.mark.integration
def test_swagger_ui_available(client: TestClient) -> None:
    """Test that Swagger UI documentation is accessible."""
    response = client.get("/docs")

    assert response.status_code == 200
    assert "swagger" in response.text.lower()


@pytest.mark.integration
def test_redoc_ui_available(client: TestClient) -> None:
    """Test that ReDoc documentation is accessible."""
    response = client.get("/redoc")

    assert response.status_code == 200
    assert "redoc" in response.text.lower()
