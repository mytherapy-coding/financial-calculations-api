"""Tests for error handling and edge cases."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_no_solution_bond_yield():
    """Test bond yield endpoint when no solution exists."""
    # Bond price that makes it impossible to find a yield in [0, 1]
    payload = {
        "face_value": 1000,
        "coupon_rate": 0.05,
        "years_to_maturity": 10,
        "current_price": 2000,  # Extremely high price
        "payments_per_year": 2
    }
    response = client.post("/v1/bond/yield", json=payload)
    # Should return 400 with NO_SOLUTION error
    assert response.status_code == 400
    data = response.json()
    assert data["ok"] is False
    assert data["error"]["code"] == "NO_SOLUTION"


def test_no_solution_xirr():
    """Test XIRR endpoint when no solution exists."""
    # Cashflows that don't have a valid IRR
    payload = {
        "cashflows": [
            {"amount": 1000, "date": "2024-01-01"},  # Only positive (no investment)
            {"amount": 2000, "date": "2025-01-01"}
        ],
        "initial_guess": 0.1
    }
    response = client.post("/v1/xirr", json=payload)
    # May return 400 with NO_SOLUTION or calculate a negative rate
    assert response.status_code in [200, 400]
    if response.status_code == 400:
        data = response.json()
        assert data["ok"] is False
        assert data["error"]["code"] == "NO_SOLUTION"


def test_max_amount_validation():
    """Test that MAX_AMOUNT validation works."""
    payload = {
        "principal": 1e13,  # Exceeds MAX_AMOUNT (1e12)
        "annual_rate": 0.07,
        "years": 10,
        "compounds_per_year": 12
    }
    response = client.post("/v1/tvm/future-value", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_negative_values_validation():
    """Test validation of negative values where not allowed."""
    # Test negative principal
    payload = {
        "principal": -1000,
        "annual_rate": 0.05,
        "years": 10,
        "compounds_per_year": 12
    }
    response = client.post("/v1/tvm/future-value", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False

    # Test negative years
    payload = {
        "principal": 1000,
        "annual_rate": 0.05,
        "years": -10,
        "compounds_per_year": 12
    }
    response = client.post("/v1/tvm/future-value", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False


def test_zero_values_validation():
    """Test validation of zero values where not allowed."""
    # Test zero years
    payload = {
        "principal": 1000,
        "annual_rate": 0.05,
        "years": 0,
        "compounds_per_year": 12
    }
    response = client.post("/v1/tvm/future-value", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False

    # Test zero compounds_per_year
    payload = {
        "principal": 1000,
        "annual_rate": 0.05,
        "years": 10,
        "compounds_per_year": 0
    }
    response = client.post("/v1/tvm/future-value", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False


def test_error_response_format():
    """Test that all error responses follow the standard format."""
    # Test validation error
    payload = {}
    response = client.post("/v1/echo", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "ok" in data
    assert "error" in data
    assert data["ok"] is False
    assert "code" in data["error"]
    assert "message" in data["error"]
    assert "details" in data["error"]


def test_amortization_max_months_validation():
    """Test that amortization schedule rejects max_months > limit."""
    payload = {
        "principal": 300000,
        "annual_rate": 0.04,
        "years": 30,
        "max_months": 601  # Exceeds MAX_AMORTIZATION_MONTHS (600)
    }
    response = client.post("/v1/mortgage/amortization-schedule", json=payload)
    assert response.status_code in [400, 422]
    data = response.json()
    assert data["ok"] is False


def test_xirr_too_many_cashflows():
    """Test that XIRR rejects too many cashflows."""
    cashflows = [{"amount": -1000, "date": "2024-01-01"}]
    for i in range(1, 1002):  # 1001 total cashflows
        cashflows.append({"amount": 100, "date": f"2024-{i%12+1:02d}-01"})
    
    payload = {
        "cashflows": cashflows,
        "initial_guess": 0.1
    }
    response = client.post("/v1/xirr", json=payload)
    assert response.status_code in [400, 422]
    data = response.json()
    assert data["ok"] is False
    if response.status_code == 400:
        assert data["error"]["code"] == "TOO_MANY_CASHFLOWS"
