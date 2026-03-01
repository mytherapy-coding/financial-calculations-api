"""Tests for edge cases and boundary conditions."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_very_small_principal():
    """Test calculations with very small principal amounts."""
    payload = {
        "principal": 0.01,
        "annual_rate": 0.05,
        "years": 1,
        "compounds_per_year": 12
    }
    response = client.post("/v1/tvm/future-value", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["future_value"] > 0


def test_very_large_principal():
    """Test calculations with very large (but valid) principal amounts."""
    payload = {
        "principal": 1e11,  # Large but within MAX_AMOUNT
        "annual_rate": 0.05,
        "years": 1,
        "compounds_per_year": 1
    }
    response = client.post("/v1/tvm/future-value", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["future_value"] > payload["principal"]


def test_very_high_rate():
    """Test calculations with very high (but valid) interest rate."""
    payload = {
        "principal": 1000,
        "annual_rate": 0.99,  # 99% - near maximum
        "years": 1,
        "compounds_per_year": 12
    }
    response = client.post("/v1/tvm/future-value", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["future_value"] > payload["principal"] * 2  # Should more than double


def test_very_long_term():
    """Test calculations with very long time periods."""
    payload = {
        "principal": 1000,
        "annual_rate": 0.05,
        "years": 100,  # Very long term
        "compounds_per_year": 12
    }
    response = client.post("/v1/tvm/future-value", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["future_value"] > payload["principal"] * 100  # Should grow significantly


def test_daily_compounding():
    """Test calculations with daily compounding."""
    payload = {
        "principal": 1000,
        "annual_rate": 0.05,
        "years": 1,
        "compounds_per_year": 365  # Daily compounding
    }
    response = client.post("/v1/tvm/future-value", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    # Daily compounding should give slightly higher result than monthly
    monthly_payload = {**payload, "compounds_per_year": 12}
    monthly_response = client.post("/v1/tvm/future-value", json=monthly_payload)
    monthly_fv = monthly_response.json()["future_value"]
    assert data["future_value"] >= monthly_fv


def test_mortgage_very_short_term():
    """Test mortgage calculation with very short term."""
    payload = {
        "principal": 100000,
        "annual_rate": 0.04,
        "years": 1  # 1 year mortgage
    }
    response = client.post("/v1/mortgage/payment", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    # Monthly payment should be significant portion of principal
    assert data["monthly_payment"] > payload["principal"] / 12


def test_mortgage_very_long_term():
    """Test mortgage calculation with very long term."""
    payload = {
        "principal": 100000,
        "annual_rate": 0.04,
        "years": 50  # 50 year mortgage
    }
    response = client.post("/v1/mortgage/payment", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    # Monthly payment should be relatively small
    assert data["monthly_payment"] < payload["principal"] / 200


def test_bond_zero_coupon():
    """Test bond calculation with zero coupon rate."""
    payload = {
        "face_value": 1000,
        "coupon_rate": 0.0,  # Zero coupon bond
        "years_to_maturity": 10,
        "current_price": 500,
        "payments_per_year": 2
    }
    response = client.post("/v1/bond/yield", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["yield_to_maturity"] > 0


def test_xirr_single_cashflow():
    """Test XIRR with minimal cashflows (2 entries)."""
    payload = {
        "cashflows": [
            {"amount": -1000, "date": "2024-01-01"},
            {"amount": 1100, "date": "2024-12-31"}
        ],
        "initial_guess": 0.1
    }
    response = client.post("/v1/xirr", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert abs(data["xirr"] - 0.10) < 0.02  # Approximately 10%


def test_xirr_many_cashflows():
    """Test XIRR with many cashflows (near limit)."""
    cashflows = [{"amount": -10000, "date": "2024-01-01"}]
    for i in range(1, 1000):  # 999 more cashflows
        cashflows.append({"amount": 10, "date": f"2024-{(i%12)+1:02d}-01"})
    
    payload = {
        "cashflows": cashflows,
        "initial_guess": 0.1
    }
    response = client.post("/v1/xirr", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "xirr" in data


def test_annuity_payment_zero_rate():
    """Test annuity payment calculation with zero interest rate."""
    payload = {
        "present_value": 12000,
        "annual_rate": 0.0,
        "years": 1,
        "payments_per_year": 12
    }
    response = client.post("/v1/tvm/annuity-payment", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    # With zero rate, payment should be PV / total_payments
    assert abs(data["payment"] - 1000) < 0.01  # 12000 / 12


def test_present_value_zero_rate():
    """Test present value calculation with zero discount rate."""
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
