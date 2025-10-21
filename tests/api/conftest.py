"""Pytest fixtures for API testing."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client() -> TestClient:
    """Provide a FastAPI TestClient for testing."""
    return TestClient(app)
