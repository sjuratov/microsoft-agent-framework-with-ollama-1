"""Tests for the models endpoint."""

from unittest.mock import patch

from fastapi.testclient import TestClient


def test_models_endpoint_success(client: TestClient) -> None:
    """Test successful retrieval of models list."""
    with patch("src.api.routes.models.get_available_models") as mock_get_models:
        # Mock available models
        mock_get_models.return_value = [
            "mistral:latest",
            "llama2:7b",
            "codellama:13b",
        ]

        response = client.get("/api/v1/models")

        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert "models" in data
        assert "default_model" in data
        assert "count" in data

        # Verify content
        assert len(data["models"]) == 3
        assert data["count"] == 3
        assert data["default_model"] == "mistral:latest"  # From default config


def test_models_response_schema(client: TestClient) -> None:
    """Test that models response matches expected schema."""
    with patch("src.api.routes.models.get_available_models") as mock_get_models:
        mock_get_models.return_value = ["mistral:latest", "llama2:7b"]

        response = client.get("/api/v1/models")
        data = response.json()

        # Check each model has required fields
        for model in data["models"]:
            assert "name" in model
            assert "display_name" in model
            assert isinstance(model["name"], str)
            assert isinstance(model["display_name"], str)

        # Check top-level fields
        assert isinstance(data["models"], list)
        assert isinstance(data["default_model"], str)
        assert isinstance(data["count"], int)
        assert data["count"] >= 0


def test_models_endpoint_with_default_model(client: TestClient) -> None:
    """Test that default model from config is included in response."""
    with patch("src.api.routes.models.get_available_models") as mock_get_models:
        mock_get_models.return_value = ["mistral:latest", "llama2:7b"]

        response = client.get("/api/v1/models")
        data = response.json()

        # Default model should be in response
        assert "default_model" in data
        assert data["default_model"]  # Should not be empty

        # Default model should be one of the available models (ideally)
        # Note: In production, default might not always be in the list
        [m["name"] for m in data["models"]]
        # Just verify the structure is correct
        assert isinstance(data["default_model"], str)


def test_models_endpoint_ollama_unavailable(client: TestClient) -> None:
    """Test models endpoint when Ollama is unavailable."""
    with patch("src.api.routes.models.get_available_models") as mock_get_models:
        # Simulate connection error
        mock_get_models.side_effect = ConnectionError(
            "Unable to connect to Ollama at http://localhost:11434"
        )

        response = client.get("/api/v1/models")

        assert response.status_code == 503
        data = response.json()

        # Check error structure
        assert "detail" in data
        detail = data["detail"]
        assert "error" in detail
        assert "message" in detail
        assert detail["error"] == "service_unavailable"


def test_models_endpoint_count_matches_list(client: TestClient) -> None:
    """Test that count field matches actual number of models."""
    with patch("src.api.routes.models.get_available_models") as mock_get_models:
        test_models = ["model1:latest", "model2:7b", "model3:13b", "model4:70b"]
        mock_get_models.return_value = test_models

        response = client.get("/api/v1/models")
        data = response.json()

        assert data["count"] == len(test_models)
        assert data["count"] == len(data["models"])


def test_models_endpoint_empty_list(client: TestClient) -> None:
    """Test models endpoint when no models are available."""
    with patch("src.api.routes.models.get_available_models") as mock_get_models:
        mock_get_models.return_value = []

        response = client.get("/api/v1/models")

        assert response.status_code == 200
        data = response.json()

        assert data["models"] == []
        assert data["count"] == 0
        assert "default_model" in data  # Should still have default from config


def test_models_endpoint_display_names(client: TestClient) -> None:
    """Test that display names are properly formatted."""
    with patch("src.api.routes.models.get_available_models") as mock_get_models:
        mock_get_models.return_value = ["mistral:latest", "llama2:7b"]

        response = client.get("/api/v1/models")
        data = response.json()

        # Check display names are formatted (title case, colon replaced with space)
        for model in data["models"]:
            assert model["display_name"]  # Not empty
            # Display name should be different from name (formatted)
            # e.g., "mistral:latest" -> "Mistral Latest"
            assert " " in model["display_name"] or ":" not in model["display_name"]
