"""Tests for the /v1/tvm/future-value endpoint."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_future_value_basic():
    """Test basic future value calculation."""
    payload = {
        "principal": 10000,
        "annual_rate": 0.07,
        "years": 10,
        "compounds_per_year": 12
    }
    response = client.post("/v1/tvm/future-value", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "future_value" in data
    # Expected value: 10000 * (1 + 0.07/12)^(12*10) ≈ 19671.51
    assert abs(data["future_value"] - 19671.51) < 0.01


def test_future_value_annually():
    """Test future value with annual compounding."""
    payload = {
        "principal": 1000,
        "annual_rate": 0.05,
        "years": 5,
        "compounds_per_year": 1
    }
    response = client.post("/v1/tvm/future-value", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    # Expected: 1000 * (1.05)^5 ≈ 1276.28
    assert abs(data["future_value"] - 1276.28) < 0.01


def test_future_value_response_structure():
    """Test that future value response has the expected structure."""
    payload = {
        "principal": 5000,
        "annual_rate": 0.06,
        "years": 3,
        "compounds_per_year": 4
    }
    response = client.post("/v1/tvm/future-value", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "ok" in data
    assert "future_value" in data
    assert isinstance(data["ok"], bool)
    assert isinstance(data["future_value"], (int, float))
    assert data["future_value"] > 0


def test_future_value_validation_negative_principal():
    """Test that negative principal is rejected."""
    payload = {
        "principal": -1000,
        "annual_rate": 0.07,
        "years": 10,
        "compounds_per_year": 12
    }
    response = client.post("/v1/tvm/future-value", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_future_value_validation_zero_years():
    """Test that zero years is rejected."""
    payload = {
        "principal": 10000,
        "annual_rate": 0.07,
        "years": 0,
        "compounds_per_year": 12
    }
    response = client.post("/v1/tvm/future-value", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_future_value_validation_negative_years():
    """Test that negative years is rejected."""
    payload = {
        "principal": 10000,
        "annual_rate": 0.07,
        "years": -5,
        "compounds_per_year": 12
    }
    response = client.post("/v1/tvm/future-value", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_future_value_validation_zero_compounds():
    """Test that zero compounds_per_year is rejected."""
    payload = {
        "principal": 10000,
        "annual_rate": 0.07,
        "years": 10,
        "compounds_per_year": 0
    }
    response = client.post("/v1/tvm/future-value", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_future_value_validation_rate_over_100_percent():
    """Test that rate over 100% (1.0) is rejected."""
    payload = {
        "principal": 10000,
        "annual_rate": 1.5,  # 150%
        "years": 10,
        "compounds_per_year": 12
    }
    response = client.post("/v1/tvm/future-value", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_future_value_missing_fields():
    """Test that missing required fields return validation error."""
    payload = {
        "principal": 10000,
        # Missing other required fields
    }
    response = client.post("/v1/tvm/future-value", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"
