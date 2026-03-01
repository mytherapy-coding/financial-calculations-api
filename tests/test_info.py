"""Tests for the /v1/info endpoint."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_info_endpoint():
    """Test that the info endpoint returns correct metadata."""
    response = client.get("/v1/info")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["service"] == "finance-api"
    assert "version" in data
    assert "environment" in data
    assert "build_timestamp" in data
    assert "git_sha" in data


def test_info_response_structure():
    """Test that the info response has the expected structure."""
    response = client.get("/v1/info")
    assert response.status_code == 200
    data = response.json()
    
    # Check all required fields
    required_fields = ["ok", "service", "version", "environment", "build_timestamp", "git_sha"]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"
    
    # Check data types
    assert isinstance(data["ok"], bool)
    assert isinstance(data["service"], str)
    assert isinstance(data["version"], str)
    assert isinstance(data["environment"], str)
    assert isinstance(data["build_timestamp"], str)
    assert isinstance(data["git_sha"], str)
    
    # Check version format
    assert data["version"] == "1.0.0"
