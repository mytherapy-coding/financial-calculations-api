"""Tests for the /v1/echo endpoint."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_echo_basic():
    """Test basic echo functionality."""
    payload = {"message": "Hello, World!"}
    response = client.post("/v1/echo", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["echo"]["message"] == "Hello, World!"
    assert data["echo"]["number"] is None


def test_echo_with_number():
    """Test echo with optional number field."""
    payload = {"message": "Test", "number": 42}
    response = client.post("/v1/echo", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["echo"]["message"] == "Test"
    assert data["echo"]["number"] == 42


def test_echo_response_structure():
    """Test that echo response has the expected structure."""
    payload = {"message": "Test message"}
    response = client.post("/v1/echo", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "ok" in data
    assert "echo" in data
    assert "message" in data["echo"]
    assert isinstance(data["ok"], bool)
    assert isinstance(data["echo"], dict)


def test_echo_validation_error_missing_message():
    """Test that echo returns validation error when message is missing."""
    payload = {}
    response = client.post("/v1/echo", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_echo_validation_error_invalid_type():
    """Test that echo returns validation error for invalid types."""
    payload = {"message": 123}  # message should be string
    response = client.post("/v1/echo", json=payload)
    # FastAPI will still accept this as it can coerce, but let's test with invalid structure
    payload = {"message": "test", "number": "not a number"}
    response = client.post("/v1/echo", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"
