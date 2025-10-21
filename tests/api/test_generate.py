"""Tests for the generate endpoint."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.orchestration.models import CompletionReason, IterationSession


@pytest.fixture
def mock_session() -> IterationSession:
    """Create a mock completed iteration session."""
    session = IterationSession(
        user_input="eco-friendly water bottle",
        model_name="mistral:latest",
    )

    # Add turns
    session.add_turn(
        slogan="Drink Green, Stay Clean",
        feedback="Good concept but lacks emotional appeal",
        approved=False,
    )
    session.add_turn(
        slogan="Hydrate Responsibly, Live Sustainably",
        feedback=None,
        approved=True,
    )

    # Complete session
    session.complete(CompletionReason.APPROVED)

    return session


def test_generate_endpoint_success(client: TestClient, mock_session: IterationSession) -> None:
    """Test successful slogan generation."""
    with patch("src.api.routes.generate.run_generation_async") as mock_run:
        mock_run.return_value = mock_session

        response = client.post(
            "/api/v1/slogans/generate",
            json={"input": "eco-friendly water bottle"}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify required fields
        assert data["slogan"] == "Hydrate Responsibly, Live Sustainably"
        assert data["input"] == "eco-friendly water bottle"
        assert data["completion_reason"] == "approved"
        assert data["turn_count"] == 2
        assert data["model_name"] == "mistral:latest"
        assert "total_duration_seconds" in data
        assert "average_duration_per_turn" in data
        assert "created_at" in data


def test_generate_endpoint_verbose_mode(client: TestClient, mock_session: IterationSession) -> None:
    """Test generation with verbose=true includes turn details."""
    with patch("src.api.routes.generate.run_generation_async") as mock_run:
        mock_run.return_value = mock_session

        response = client.post(
            "/api/v1/slogans/generate",
            json={
                "input": "eco-friendly water bottle",
                "verbose": True
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Should include turns array
        assert "turns" in data
        assert data["turns"] is not None
        assert len(data["turns"]) == 2

        # Verify turn structure
        first_turn = data["turns"][0]
        assert first_turn["turn_number"] == 1
        assert first_turn["slogan"] == "Drink Green, Stay Clean"
        assert first_turn["feedback"] is not None
        assert first_turn["approved"] is False

        second_turn = data["turns"][1]
        assert second_turn["turn_number"] == 2
        assert second_turn["slogan"] == "Hydrate Responsibly, Live Sustainably"
        assert second_turn["feedback"] is None
        assert second_turn["approved"] is True


def test_generate_endpoint_non_verbose_mode(
    client: TestClient, mock_session: IterationSession
) -> None:
    """Test generation with verbose=false excludes turn details."""
    with patch("src.api.routes.generate.run_generation_async") as mock_run:
        mock_run.return_value = mock_session

        response = client.post(
            "/api/v1/slogans/generate",
            json={
                "input": "eco-friendly water bottle",
                "verbose": False
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Should not include turns or it should be null
        assert data.get("turns") is None


def test_generate_endpoint_with_custom_model(
    client: TestClient, mock_session: IterationSession
) -> None:
    """Test generation with custom model specification."""
    with patch("src.api.routes.generate.run_generation_async") as mock_run, \
         patch("src.api.routes.generate.get_available_models") as mock_models:

        mock_models.return_value = ["mistral:latest", "llama2:7b"]
        mock_run.return_value = mock_session

        response = client.post(
            "/api/v1/slogans/generate",
            json={
                "input": "eco-friendly water bottle",
                "model": "llama2:7b"
            }
        )

        assert response.status_code == 200
        # Verify model validation was called
        mock_models.assert_called_once()


def test_generate_endpoint_invalid_model(client: TestClient) -> None:
    """Test generation with non-existent model returns 400."""
    with patch("src.api.routes.generate.get_available_models") as mock_models:
        mock_models.return_value = ["mistral:latest", "llama2:7b"]

        response = client.post(
            "/api/v1/slogans/generate",
            json={
                "input": "eco-friendly water bottle",
                "model": "invalid-model"
            }
        )

        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        assert response.status_code == 400
        data = response.json()
        assert "invalid-model" in data["detail"]
        assert "mistral:latest" in data["detail"]


def test_generate_endpoint_validation_error_empty_input(client: TestClient) -> None:
    """Test validation error for empty input."""
    response = client.post(
        "/api/v1/slogans/generate",
        json={"input": ""}
    )

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_generate_endpoint_validation_error_missing_input(client: TestClient) -> None:
    """Test validation error for missing input field."""
    response = client.post(
        "/api/v1/slogans/generate",
        json={}
    )

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_generate_endpoint_validation_error_input_too_long(client: TestClient) -> None:
    """Test validation error for input exceeding max length."""
    long_input = "x" * 501  # Max is 500

    response = client.post(
        "/api/v1/slogans/generate",
        json={"input": long_input}
    )

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_generate_endpoint_validation_error_max_turns_out_of_range(client: TestClient) -> None:
    """Test validation error for max_turns out of valid range."""
    response = client.post(
        "/api/v1/slogans/generate",
        json={
            "input": "test product",
            "max_turns": 11  # Max is 10
        }
    )

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_generate_endpoint_timeout(client: TestClient) -> None:
    """Test generation timeout returns 504."""
    with patch("src.api.routes.generate.run_generation_async") as mock_run:
        mock_run.side_effect = TimeoutError(
            "Slogan generation exceeded maximum time limit (600 seconds)"
        )

        response = client.post(
            "/api/v1/slogans/generate",
            json={"input": "test product"}
        )

        assert response.status_code == 504
        data = response.json()
        assert "detail" in data
        detail = data["detail"]
        assert detail["error"] == "generation_timeout"


def test_generate_endpoint_connection_error(client: TestClient) -> None:
    """Test generation with Ollama unavailable returns 503."""
    with patch("src.api.routes.generate.run_generation_async") as mock_run:
        mock_run.side_effect = ConnectionError("Unable to connect to Ollama")

        response = client.post(
            "/api/v1/slogans/generate",
            json={"input": "test product"}
        )

        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
        detail = data["detail"]
        assert detail["error"] == "service_unavailable"


def test_generate_endpoint_max_turns_completion(client: TestClient) -> None:
    """Test generation that completes due to max_turns."""
    # Create session that hit max turns
    session = IterationSession(
        user_input="test product",
        model_name="mistral:latest",
    )

    for i in range(5):
        session.add_turn(
            slogan=f"Slogan attempt {i+1}",
            feedback="Not quite right" if i < 4 else None,
            approved=False,
        )

    session.complete(CompletionReason.MAX_TURNS)

    with patch("src.api.routes.generate.run_generation_async") as mock_run:
        mock_run.return_value = session

        response = client.post(
            "/api/v1/slogans/generate",
            json={"input": "test product"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["completion_reason"] == "max_turns"
        assert data["turn_count"] == 5


def test_generate_endpoint_duration_metrics(
    client: TestClient, mock_session: IterationSession
) -> None:
    """Test that duration metrics are calculated correctly."""
    with patch("src.api.routes.generate.run_generation_async") as mock_run:
        mock_run.return_value = mock_session

        response = client.post(
            "/api/v1/slogans/generate",
            json={"input": "eco-friendly water bottle"}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify duration fields exist and are valid
        assert isinstance(data["total_duration_seconds"], (int, float))
        assert data["total_duration_seconds"] >= 0
        assert isinstance(data["average_duration_per_turn"], (int, float))
        assert data["average_duration_per_turn"] >= 0

        # Average should be total / turn_count
        expected_avg = data["total_duration_seconds"] / data["turn_count"]
        assert abs(data["average_duration_per_turn"] - expected_avg) < 0.01
