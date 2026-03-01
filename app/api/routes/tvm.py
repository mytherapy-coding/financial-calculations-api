"""Time Value of Money routes."""
from fastapi import APIRouter
from app.models.tvm import (
    FutureValueRequest,
    FutureValueResponse,
    PresentValueRequest,
    PresentValueResponse,
    AnnuityPaymentRequest,
    AnnuityPaymentResponse,
)
from app.services.tvm import (
    calculate_future_value as calc_fv,
    calculate_present_value as calc_pv,
    calculate_annuity_payment as calc_annuity,
)

router = APIRouter()


@router.post(
    "/v1/tvm/future-value",
    response_model=FutureValueResponse,
    summary="Calculate Future Value",
    description="Calculate the future value of an investment using compound interest.",
    response_description="Calculated future value",
    tags=["Time Value of Money"],
)
def calculate_future_value(payload: FutureValueRequest):
    """
    Calculate the future value of an investment using compound interest.
    
    Formula: FV = P × (1 + r/n)^(n×t)
    
    Where:
    - **P** = principal (initial amount)
    - **r** = annual interest rate (as decimal, e.g., 0.07 for 7%)
    - **n** = number of compounding periods per year
    - **t** = number of years
    """
    future_value = calc_fv(
        payload.principal,
        payload.annual_rate,
        payload.years,
        payload.compounds_per_year,
    )
    return {"ok": True, "future_value": future_value}


@router.post(
    "/v1/tvm/present-value",
    response_model=PresentValueResponse,
    summary="Calculate Present Value",
    description="Calculate the present value of a future amount using compound discounting.",
    response_description="Calculated present value",
    tags=["Time Value of Money"],
)
def calculate_present_value(payload: PresentValueRequest):
    """
    Calculate the present value of a future amount.

    Formula: PV = FV / (1 + r/n)^(n × t)
    """
    present_value = calc_pv(
        payload.future_value,
        payload.annual_rate,
        payload.years,
        payload.compounds_per_year,
    )
    return {"ok": True, "present_value": present_value}


@router.post(
    "/v1/tvm/annuity-payment",
    response_model=AnnuityPaymentResponse,
    summary="Calculate Annuity Payment",
    description="Calculate the level payment amount for a fixed-term annuity.",
    response_description="Annuity payment amount",
    tags=["Time Value of Money"],
)
def calculate_annuity_payment(payload: AnnuityPaymentRequest):
    """
    Calculate the level payment amount for a fixed-term annuity.

    Formula: Pmt = PV × [r(1+r)^n] / [(1+r)^n - 1]
    """
    payment = calc_annuity(
        payload.present_value,
        payload.annual_rate,
        payload.years,
        payload.payments_per_year,
    )
    return {"ok": True, "payment": payment}
