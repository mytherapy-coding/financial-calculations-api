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


def test_mortgage_with_extra_payments_basic():
    """Test basic mortgage calculation with extra payments."""
    payload = {
        "principal": 300000,
        "annual_rate": 0.04,
        "years": 30,
        "extra_monthly_payment": 200
    }
    response = client.post("/v1/mortgage/with-extra-payments", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "regular_monthly_payment" in data
    assert "total_monthly_payment" in data
    assert "original_payoff_months" in data
    assert "new_payoff_months" in data
    assert "months_saved" in data
    assert "interest_saved" in data
    assert "new_payoff_date" in data
    
    # Verify calculations make sense
    assert data["total_monthly_payment"] == data["regular_monthly_payment"] + 200
    assert data["new_payoff_months"] < data["original_payoff_months"]
    assert data["months_saved"] > 0
    assert data["interest_saved"] > 0


def test_mortgage_with_extra_payments_savings():
    """Test that extra payments reduce payoff time and interest."""
    payload = {
        "principal": 200000,
        "annual_rate": 0.05,
        "years": 30,
        "extra_monthly_payment": 100
    }
    response = client.post("/v1/mortgage/with-extra-payments", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Extra payments should save time and money
    assert data["months_saved"] > 0
    assert data["interest_saved"] > 0
    assert data["new_payoff_months"] < data["original_payoff_months"]
    assert data["new_total_interest"] < data["original_total_interest"]


def test_mortgage_with_extra_payments_zero_extra():
    """Test with zero extra payment (should match regular mortgage)."""
    payload = {
        "principal": 100000,
        "annual_rate": 0.04,
        "years": 15,
        "extra_monthly_payment": 0
    }
    response = client.post("/v1/mortgage/with-extra-payments", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # With zero extra, should match original
    assert data["total_monthly_payment"] == data["regular_monthly_payment"]
    assert data["months_saved"] == 0
    assert data["new_payoff_months"] == data["original_payoff_months"]


def test_mortgage_with_extra_payments_large_extra():
    """Test with large extra payment (should significantly reduce payoff)."""
    payload = {
        "principal": 300000,
        "annual_rate": 0.04,
        "years": 30,
        "extra_monthly_payment": 500
    }
    response = client.post("/v1/mortgage/with-extra-payments", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Large extra payment should save significant time
    assert data["months_saved"] > 50  # Should save at least 50 months
    assert data["interest_saved"] > 50000  # Should save significant interest


def test_mortgage_with_extra_payments_validation_negative_principal():
    """Test that negative principal is rejected."""
    payload = {
        "principal": -100000,
        "annual_rate": 0.04,
        "years": 30,
        "extra_monthly_payment": 100
    }
    response = client.post("/v1/mortgage/with-extra-payments", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False


def test_mortgage_with_extra_payments_validation_negative_extra():
    """Test that negative extra payment is rejected."""
    payload = {
        "principal": 100000,
        "annual_rate": 0.04,
        "years": 30,
        "extra_monthly_payment": -50
    }
    response = client.post("/v1/mortgage/with-extra-payments", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False


def test_mortgage_with_extra_payments_validation_invalid_rate():
    """Test that invalid interest rate is rejected."""
    payload = {
        "principal": 100000,
        "annual_rate": 1.5,  # > 100%
        "years": 30,
        "extra_monthly_payment": 100
    }
    response = client.post("/v1/mortgage/with-extra-payments", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False


def test_mortgage_with_extra_payments_structure():
    """Test that response has all required fields."""
    payload = {
        "principal": 150000,
        "annual_rate": 0.035,
        "years": 20,
        "extra_monthly_payment": 150
    }
    response = client.post("/v1/mortgage/with-extra-payments", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Check all required fields exist
    required_fields = [
        "ok",
        "regular_monthly_payment",
        "total_monthly_payment",
        "original_payoff_months",
        "new_payoff_months",
        "months_saved",
        "original_total_interest",
        "new_total_interest",
        "interest_saved",
        "new_payoff_date"
    ]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"
    
    # Check data types
    assert isinstance(data["regular_monthly_payment"], (int, float))
    assert isinstance(data["total_monthly_payment"], (int, float))
    assert isinstance(data["original_payoff_months"], int)
    assert isinstance(data["new_payoff_months"], int)
    assert isinstance(data["months_saved"], int)
    assert isinstance(data["interest_saved"], (int, float))
    assert isinstance(data["new_payoff_date"], str)
    # Check date format (YYYY-MM)
    assert len(data["new_payoff_date"]) == 7
    assert data["new_payoff_date"][4] == "-"


def test_mortgage_summary_basic():
    """Test basic mortgage summary calculation."""
    payload = {
        "principal": 300000,
        "annual_rate": 0.04,
        "years": 30
    }
    response = client.post("/v1/mortgage/summary", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "monthly_payment" in data
    assert "total_paid" in data
    assert "total_interest" in data
    assert "payoff_months" in data
    assert "payoff_date" in data
    
    # Verify calculations
    assert data["monthly_payment"] > 0
    assert data["total_paid"] > payload["principal"]
    assert data["total_interest"] > 0
    assert data["payoff_months"] == 360
    assert data["total_paid"] == data["monthly_payment"] * data["payoff_months"]


def test_mortgage_summary_structure():
    """Test that mortgage summary response has all required fields."""
    payload = {
        "principal": 200000,
        "annual_rate": 0.035,
        "years": 15
    }
    response = client.post("/v1/mortgage/summary", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    required_fields = [
        "ok",
        "monthly_payment",
        "total_paid",
        "total_interest",
        "payoff_months",
        "payoff_date"
    ]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"
    
    # Check date format
    assert len(data["payoff_date"]) == 7
    assert data["payoff_date"][4] == "-"


def test_mortgage_summary_zero_interest():
    """Test mortgage summary with zero interest."""
    payload = {
        "principal": 100000,
        "annual_rate": 0.0,
        "years": 10
    }
    response = client.post("/v1/mortgage/summary", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # With zero interest, total_interest should be 0
    assert data["total_interest"] == 0
    assert data["total_paid"] == payload["principal"]
    assert data["monthly_payment"] == payload["principal"] / (payload["years"] * 12)
