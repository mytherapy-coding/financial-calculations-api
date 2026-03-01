"""Integration tests for API endpoints."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_tvm_round_trip():
    """Test that present value and future value are inverse operations."""
    # Calculate future value
    fv_payload = {
        "principal": 10000,
        "annual_rate": 0.07,
        "years": 10,
        "compounds_per_year": 12
    }
    fv_response = client.post("/v1/tvm/future-value", json=fv_payload)
    assert fv_response.status_code == 200
    future_value = fv_response.json()["future_value"]
    
    # Calculate present value from that future value
    pv_payload = {
        "future_value": future_value,
        "annual_rate": 0.07,
        "years": 10,
        "compounds_per_year": 12
    }
    pv_response = client.post("/v1/tvm/present-value", json=pv_payload)
    assert pv_response.status_code == 200
    present_value = pv_response.json()["present_value"]
    
    # Should be approximately equal (within rounding)
    assert abs(present_value - 10000) < 1.0


def test_bond_price_yield_round_trip():
    """Test that bond price and yield are consistent."""
    # Calculate yield from price
    yield_payload = {
        "face_value": 1000,
        "coupon_rate": 0.05,
        "years_to_maturity": 10,
        "current_price": 950,
        "payments_per_year": 2
    }
    yield_response = client.post("/v1/bond/yield", json=yield_payload)
    assert yield_response.status_code == 200
    ytm = yield_response.json()["yield_to_maturity"]
    
    # Calculate price from that yield
    price_payload = {
        "face_value": 1000,
        "coupon_rate": 0.05,
        "years_to_maturity": 10,
        "yield_to_maturity": ytm,
        "payments_per_year": 2
    }
    price_response = client.post("/v1/bond/price", json=price_payload)
    assert price_response.status_code == 200
    price = price_response.json()["price"]
    
    # Should be approximately equal to original price (within rounding)
    assert abs(price - 950) < 5.0


def test_mortgage_summary_consistency():
    """Test that mortgage summary values are consistent."""
    payload = {
        "principal": 300000,
        "annual_rate": 0.04,
        "years": 30
    }
    response = client.post("/v1/mortgage/summary", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Check consistency
    assert data["total_paid"] == data["monthly_payment"] * data["payoff_months"]
    assert abs(data["total_paid"] - data["principal"] - data["total_interest"]) < 0.01


def test_mortgage_with_extra_payments_consistency():
    """Test that mortgage with extra payments values are consistent."""
    payload = {
        "principal": 300000,
        "annual_rate": 0.04,
        "years": 30,
        "extra_monthly_payment": 200
    }
    response = client.post("/v1/mortgage/with-extra-payments", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Check consistency
    assert data["total_monthly_payment"] == data["regular_monthly_payment"] + 200
    assert data["months_saved"] == data["original_payoff_months"] - data["new_payoff_months"]
    assert abs(data["interest_saved"] - (data["original_total_interest"] - data["new_total_interest"])) < 0.01
    assert data["interest_saved"] > 0
    assert data["months_saved"] > 0


def test_all_endpoints_return_ok_field():
    """Test that all successful endpoints return ok: true."""
    endpoints = [
        ("GET", "/v1/health", None),
        ("GET", "/v1/info", None),
        ("POST", "/v1/echo", {"message": "test"}),
        ("POST", "/v1/tvm/future-value", {
            "principal": 1000,
            "annual_rate": 0.05,
            "years": 1,
            "compounds_per_year": 1
        }),
        ("POST", "/v1/tvm/present-value", {
            "future_value": 1000,
            "annual_rate": 0.05,
            "years": 1,
            "compounds_per_year": 1
        }),
        ("POST", "/v1/tvm/annuity-payment", {
            "present_value": 1000,
            "annual_rate": 0.05,
            "years": 1,
            "payments_per_year": 12
        }),
        ("POST", "/v1/mortgage/payment", {
            "principal": 100000,
            "annual_rate": 0.04,
            "years": 30
        }),
        ("POST", "/v1/mortgage/summary", {
            "principal": 100000,
            "annual_rate": 0.04,
            "years": 30
        }),
    ]
    
    for method, path, payload in endpoints:
        if method == "GET":
            response = client.get(path)
        else:
            response = client.post(path, json=payload)
        
        assert response.status_code == 200, f"Failed for {method} {path}"
        data = response.json()
        assert data["ok"] is True, f"Missing ok:true in {path}"


def test_xirr_explain_contains_metadata():
    """Test that XIRR explain endpoint returns all expected metadata."""
    payload = {
        "cashflows": [
            {"amount": -10000, "date": "2024-01-01"},
            {"amount": 11000, "date": "2025-01-01"}
        ],
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
    assert isinstance(data["iterations"], int)
    assert isinstance(data["solver_type"], str)
    assert isinstance(data["warnings"], list)
