"""Tests for the /v1/health endpoint."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test that the health endpoint returns correct status."""
    response = client.get("/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["service"] == "finance-api"
    assert data["version"] == "v1"


def test_health_response_structure():
    """Test that the health response has the expected structure."""
    response = client.get("/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "ok" in data
    assert "service" in data
    assert "version" in data
    assert isinstance(data["ok"], bool)
    assert isinstance(data["service"], str)
    assert isinstance(data["version"], str)
