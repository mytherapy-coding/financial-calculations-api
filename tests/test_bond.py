"""Tests for bond yield endpoint."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_bond_yield_basic():
    """Test basic bond yield calculation."""
    payload = {
        "face_value": 1000,
        "coupon_rate": 0.05,
        "years_to_maturity": 10,
        "current_price": 950,
        "payments_per_year": 2
    }
    response = client.post("/v1/bond/yield", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "yield_to_maturity" in data
    assert data["yield_to_maturity"] > 0
    # Bond trading at discount should have YTM > coupon rate
    assert data["yield_to_maturity"] > 0.05


def test_bond_yield_premium():
    """Test bond yield for premium bond."""
    payload = {
        "face_value": 1000,
        "coupon_rate": 0.04,
        "years_to_maturity": 5,
        "current_price": 1050,
        "payments_per_year": 2
    }
    response = client.post("/v1/bond/yield", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["yield_to_maturity"] > 0
    # Bond trading at premium should have YTM < coupon rate
    assert data["yield_to_maturity"] < 0.04


def test_bond_yield_par():
    """Test bond yield when trading at par."""
    payload = {
        "face_value": 1000,
        "coupon_rate": 0.05,
        "years_to_maturity": 10,
        "current_price": 1000,
        "payments_per_year": 2
    }
    response = client.post("/v1/bond/yield", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    # YTM should be close to coupon rate when at par
    assert abs(data["yield_to_maturity"] - 0.05) < 0.01


def test_bond_yield_validation():
    """Test bond yield validation."""
    payload = {
        "face_value": -1000,  # Invalid
        "coupon_rate": 0.05,
        "years_to_maturity": 10,
        "current_price": 950,
        "payments_per_year": 2
    }
    response = client.post("/v1/bond/yield", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False
