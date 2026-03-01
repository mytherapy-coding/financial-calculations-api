"""Tests for TVM (Time Value of Money) endpoints."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_present_value_basic():
    """Test basic present value calculation."""
    payload = {
        "future_value": 10000,
        "annual_rate": 0.07,
        "years": 10,
        "compounds_per_year": 12
    }
    response = client.post("/v1/tvm/present-value", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "present_value" in data
    assert data["present_value"] > 0
    # Future value should be greater than present value
    assert data["present_value"] < payload["future_value"]


def test_present_value_zero_rate():
    """Test present value with zero interest rate."""
    payload = {
        "future_value": 10000,
        "annual_rate": 0.0,
        "years": 10,
        "compounds_per_year": 12
    }
    response = client.post("/v1/tvm/present-value", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    # With zero rate, PV should equal FV
    assert abs(data["present_value"] - 10000) < 0.01


def test_present_value_validation_negative_future_value():
    """Test that negative future value is rejected."""
    payload = {
        "future_value": -10000,
        "annual_rate": 0.07,
        "years": 10,
        "compounds_per_year": 12
    }
    response = client.post("/v1/tvm/present-value", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False


def test_present_value_validation_zero_years():
    """Test that zero years is rejected."""
    payload = {
        "future_value": 10000,
        "annual_rate": 0.07,
        "years": 0,
        "compounds_per_year": 12
    }
    response = client.post("/v1/tvm/present-value", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False


def test_annuity_payment_basic():
    """Test basic annuity payment calculation."""
    payload = {
        "present_value": 10000,
        "annual_rate": 0.05,
        "years": 5,
        "payments_per_year": 12
    }
    response = client.post("/v1/tvm/annuity-payment", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "payment" in data
    assert data["payment"] > 0
    # Payment should be reasonable (less than PV per month)
    assert data["payment"] < payload["present_value"]


def test_annuity_payment_zero_rate():
    """Test annuity payment with zero interest rate."""
    payload = {
        "present_value": 10000,
        "annual_rate": 0.0,
        "years": 5,
        "payments_per_year": 12
    }
    response = client.post("/v1/tvm/annuity-payment", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    # With zero rate, payment should be PV / total_payments
    expected = 10000 / (5 * 12)
    assert abs(data["payment"] - expected) < 0.01


def test_annuity_payment_validation_negative_present_value():
    """Test that negative present value is rejected."""
    payload = {
        "present_value": -10000,
        "annual_rate": 0.05,
        "years": 5,
        "payments_per_year": 12
    }
    response = client.post("/v1/tvm/annuity-payment", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False


def test_annuity_payment_validation_zero_payments():
    """Test that zero payments_per_year is rejected."""
    payload = {
        "present_value": 10000,
        "annual_rate": 0.05,
        "years": 5,
        "payments_per_year": 0
    }
    response = client.post("/v1/tvm/annuity-payment", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False


def test_present_value_response_structure():
    """Test that present value response has correct structure."""
    payload = {
        "future_value": 5000,
        "annual_rate": 0.06,
        "years": 5,
        "compounds_per_year": 4
    }
    response = client.post("/v1/tvm/present-value", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "ok" in data
    assert "present_value" in data
    assert isinstance(data["ok"], bool)
    assert isinstance(data["present_value"], (int, float))


def test_annuity_payment_response_structure():
    """Test that annuity payment response has correct structure."""
    payload = {
        "present_value": 5000,
        "annual_rate": 0.06,
        "years": 5,
        "payments_per_year": 4
    }
    response = client.post("/v1/tvm/annuity-payment", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "ok" in data
    assert "payment" in data
    assert isinstance(data["ok"], bool)
    assert isinstance(data["payment"], (int, float))
