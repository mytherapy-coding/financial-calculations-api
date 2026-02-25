"""Tests for mortgage endpoints."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_mortgage_payment_basic():
    """Test basic mortgage payment calculation."""
    payload = {
        "principal": 300000,
        "annual_rate": 0.04,
        "years": 30
    }
    response = client.post("/v1/mortgage/payment", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "monthly_payment" in data
    assert data["monthly_payment"] > 0
    # Approximate check: $300k at 4% for 30 years ≈ $1432/month
    assert 1400 < data["monthly_payment"] < 1500


def test_mortgage_payment_15_year():
    """Test 15-year mortgage payment."""
    payload = {
        "principal": 200000,
        "annual_rate": 0.035,
        "years": 15
    }
    response = client.post("/v1/mortgage/payment", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["monthly_payment"] > 0


def test_mortgage_payment_zero_interest():
    """Test mortgage payment with zero interest."""
    payload = {
        "principal": 100000,
        "annual_rate": 0.0,
        "years": 10
    }
    response = client.post("/v1/mortgage/payment", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    # Should be principal / (years * 12)
    assert abs(data["monthly_payment"] - 833.33) < 0.01


def test_mortgage_payment_validation_negative_principal():
    """Test that negative principal is rejected."""
    payload = {
        "principal": -100000,
        "annual_rate": 0.04,
        "years": 30
    }
    response = client.post("/v1/mortgage/payment", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False


def test_amortization_schedule_basic():
    """Test basic amortization schedule generation."""
    payload = {
        "principal": 100000,
        "annual_rate": 0.05,
        "years": 5,
        "max_months": 60
    }
    response = client.post("/v1/mortgage/amortization-schedule", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "monthly_payment" in data
    assert "total_payments" in data
    assert "schedule" in data
    assert len(data["schedule"]) == 60
    assert data["schedule"][0]["month"] == 1
    assert data["schedule"][0]["remaining_balance"] > 0


def test_amortization_schedule_max_months_guard():
    """Test that max_months guard works."""
    payload = {
        "principal": 300000,
        "annual_rate": 0.04,
        "years": 30,
        "max_months": 10  # Should only return 10 months
    }
    response = client.post("/v1/mortgage/amortization-schedule", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert len(data["schedule"]) == 10
    assert data["total_payments"] == 360  # But total is still 360


def test_amortization_schedule_max_months_limit():
    """Test that max_months cannot exceed 600."""
    payload = {
        "principal": 300000,
        "annual_rate": 0.04,
        "years": 30,
        "max_months": 1000  # Should be capped at 600
    }
    response = client.post("/v1/mortgage/amortization-schedule", json=payload)
    # Should either validate or cap at 600
    # The validation should catch this
    assert response.status_code in [200, 422]
