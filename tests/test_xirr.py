"""Tests for XIRR endpoint."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_xirr_basic():
    """Test basic XIRR calculation."""
    payload = {
        "cashflows": [
            {"amount": -10000, "date": "2024-01-01"},
            {"amount": 2000, "date": "2024-06-30"},
            {"amount": 3000, "date": "2024-12-31"},
            {"amount": 5000, "date": "2025-12-31"}
        ],
        "max_cashflows": 1000,
        "initial_guess": 0.1
    }
    response = client.post("/v1/xirr", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "xirr" in data
    assert isinstance(data["xirr"], (int, float))


def test_xirr_simple_investment():
    """Test XIRR for simple investment scenario."""
    payload = {
        "cashflows": [
            {"amount": -1000, "date": "2024-01-01"},
            {"amount": 1100, "date": "2025-01-01"}
        ],
        "max_cashflows": 1000,
        "initial_guess": 0.1
    }
    response = client.post("/v1/xirr", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    # Should be approximately 10% return (allow wider tolerance for bisection method)
    assert abs(data["xirr"] - 0.10) < 0.02


def test_xirr_validation_min_cashflows():
    """Test that XIRR requires at least 2 cashflows."""
    payload = {
        "cashflows": [
            {"amount": -1000, "date": "2024-01-01"}
        ],
        "max_cashflows": 1000,
        "initial_guess": 0.1
    }
    response = client.post("/v1/xirr", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False


def test_xirr_validation_invalid_date():
    """Test that invalid date format is rejected."""
    payload = {
        "cashflows": [
            {"amount": -1000, "date": "2024/01/01"},  # Wrong format
            {"amount": 1100, "date": "2025-01-01"}
        ],
        "max_cashflows": 1000,
        "initial_guess": 0.1
    }
    response = client.post("/v1/xirr", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False


def test_xirr_max_cashflows_guard():
    """Test that max_cashflows guard works."""
    # Create 1001 cashflows (exceeds limit)
    cashflows = [{"amount": -1000, "date": "2024-01-01"}]
    for i in range(1, 1002):
        cashflows.append({"amount": 100, "date": f"2024-{i%12+1:02d}-01"})
    
    payload = {
        "cashflows": cashflows,
        "max_cashflows": 1000,
        "initial_guess": 0.1
    }
    response = client.post("/v1/xirr", json=payload)
    # Should be rejected by validation
    assert response.status_code in [400, 422]
    data = response.json()
    assert data["ok"] is False


def test_xirr_explain_basic():
    """Test basic XIRR explain endpoint."""
    payload = {
        "cashflows": [
            {"amount": -10000, "date": "2024-01-01"},
            {"amount": 2000, "date": "2024-06-30"},
            {"amount": 3000, "date": "2024-12-31"},
            {"amount": 5000, "date": "2025-12-31"}
        ],
        "max_cashflows": 1000,
        "initial_guess": 0.1
    }
    response = client.post("/v1/xirr/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "xirr" in data
    assert "iterations" in data
    assert "solver_type" in data
    assert "warnings" in data
    
    # Check data types
    assert isinstance(data["xirr"], (int, float))
    assert isinstance(data["iterations"], int)
    assert isinstance(data["solver_type"], str)
    assert isinstance(data["warnings"], list)


def test_xirr_explain_solver_type():
    """Test that solver_type is returned."""
    payload = {
        "cashflows": [
            {"amount": -1000, "date": "2024-01-01"},
            {"amount": 1100, "date": "2025-01-01"}
        ],
        "max_cashflows": 1000,
        "initial_guess": 0.1
    }
    response = client.post("/v1/xirr/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Solver type should be one of the expected values
    assert data["solver_type"] in ["scipy-brentq", "scipy-fsolve", "bisection", ""]
    assert data["xirr"] > 0


def test_xirr_explain_warnings():
    """Test that warnings array is returned (may be empty)."""
    payload = {
        "cashflows": [
            {"amount": -1000, "date": "2024-01-01"},
            {"amount": 1100, "date": "2025-01-01"}
        ],
        "max_cashflows": 1000,
        "initial_guess": 0.1
    }
    response = client.post("/v1/xirr/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Warnings should be a list (may be empty)
    assert isinstance(data["warnings"], list)
    # All warnings should be strings
    for warning in data["warnings"]:
        assert isinstance(warning, str)


def test_xirr_explain_validation_min_cashflows():
    """Test that XIRR explain requires at least 2 cashflows."""
    payload = {
        "cashflows": [
            {"amount": -1000, "date": "2024-01-01"}
        ],
        "max_cashflows": 1000,
        "initial_guess": 0.1
    }
    response = client.post("/v1/xirr/explain", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False


def test_xirr_explain_max_cashflows_guard():
    """Test that max_cashflows guard works for explain endpoint."""
    cashflows = [{"amount": -1000, "date": "2024-01-01"}]
    for i in range(1, 1002):
        cashflows.append({"amount": 100, "date": f"2024-{i%12+1:02d}-01"})
    
    payload = {
        "cashflows": cashflows,
        "max_cashflows": 1000,
        "initial_guess": 0.1
    }
    response = client.post("/v1/xirr/explain", json=payload)
    assert response.status_code in [400, 422]
    data = response.json()
    assert data["ok"] is False
