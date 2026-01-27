"""API endpoint tests."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_health(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root(client):
    """Test root endpoint."""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    assert "message" in response.json()
