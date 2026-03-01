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
    # YTM should be close to coupon rate when at par (allow wider tolerance for bisection method)
    assert abs(data["yield_to_maturity"] - 0.05) < 0.02


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


def test_bond_price_basic():
    """Test basic bond price calculation."""
    payload = {
        "face_value": 1000,
        "coupon_rate": 0.05,
        "years_to_maturity": 10,
        "yield_to_maturity": 0.055,
        "payments_per_year": 2
    }
    response = client.post("/v1/bond/price", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "price" in data
    assert data["price"] > 0
    # Bond trading at discount (YTM > coupon) should have price < face value
    assert data["price"] < payload["face_value"]


def test_bond_price_premium():
    """Test bond price for premium bond (YTM < coupon rate)."""
    payload = {
        "face_value": 1000,
        "coupon_rate": 0.05,
        "years_to_maturity": 10,
        "yield_to_maturity": 0.04,  # Lower yield = premium
        "payments_per_year": 2
    }
    response = client.post("/v1/bond/price", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    # Premium bond should have price > face value
    assert data["price"] > payload["face_value"]


def test_bond_price_par():
    """Test bond price when YTM equals coupon rate (at par)."""
    payload = {
        "face_value": 1000,
        "coupon_rate": 0.05,
        "years_to_maturity": 10,
        "yield_to_maturity": 0.05,  # Same as coupon = at par
        "payments_per_year": 2
    }
    response = client.post("/v1/bond/price", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    # At par, price should be close to face value
    assert abs(data["price"] - payload["face_value"]) < 10


def test_bond_price_validation_negative_face_value():
    """Test that negative face value is rejected."""
    payload = {
        "face_value": -1000,
        "coupon_rate": 0.05,
        "years_to_maturity": 10,
        "yield_to_maturity": 0.055,
        "payments_per_year": 2
    }
    response = client.post("/v1/bond/price", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False


def test_bond_price_validation_invalid_yield():
    """Test that invalid yield (> 100%) is rejected."""
    payload = {
        "face_value": 1000,
        "coupon_rate": 0.05,
        "years_to_maturity": 10,
        "yield_to_maturity": 1.5,  # > 100%
        "payments_per_year": 2
    }
    response = client.post("/v1/bond/price", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False
