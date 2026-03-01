"""Mortgage calculation routes."""
from fastapi import APIRouter, status, HTTPException
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from app.models.mortgage import (
    MortgagePaymentRequest,
    MortgagePaymentResponse,
    AmortizationScheduleRequest,
    AmortizationScheduleResponse,
    MortgageSummaryRequest,
    MortgageSummaryResponse,
    MortgageWithExtraPaymentsRequest,
    MortgageWithExtraPaymentsResponse,
)
from app.services.mortgage import (
    calculate_mortgage_payment,
    generate_amortization_schedule,
    calculate_mortgage_summary,
    calculate_mortgage_with_extra_payments,
)
from app.core.config import MAX_AMORTIZATION_MONTHS, SOLVER_TIMEOUT_SECONDS

router = APIRouter()


@router.post(
    "/v1/mortgage/payment",
    response_model=MortgagePaymentResponse,
    summary="Calculate Mortgage Payment",
    description="Calculate the monthly payment for a fixed-rate mortgage.",
    response_description="Monthly payment amount",
    tags=["Mortgage"],
)
def calculate_mortgage_payment_endpoint(payload: MortgagePaymentRequest):
    """
    Calculate the monthly payment for a fixed-rate mortgage.
    
    Uses the standard mortgage payment formula:
    M = P × [r(1+r)^n] / [(1+r)^n - 1]
    """
    monthly_payment = calculate_mortgage_payment(
        payload.principal,
        payload.annual_rate,
        payload.years,
    )
    return {"ok": True, "monthly_payment": monthly_payment}


@router.post(
    "/v1/mortgage/amortization-schedule",
    response_model=AmortizationScheduleResponse,
    summary="Generate Amortization Schedule",
    description="Generate an amortization schedule for a mortgage. Limited to max_months (default: 600).",
    response_description="Amortization schedule",
    tags=["Mortgage"],
)
def generate_amortization_schedule_endpoint(payload: AmortizationScheduleRequest):
    """
    Generate an amortization schedule for a fixed-rate mortgage.
    
    Returns a detailed payment schedule showing principal and interest breakdown
    for each payment period.
    
    **Guards:**
    - Maximum 600 months (50 years) to prevent excessive output
    """
    # Guard: Check max_months
    if payload.max_months > MAX_AMORTIZATION_MONTHS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "ok": False,
                "error": {
                    "code": "TOO_MANY_MONTHS",
                    "message": f"Maximum {MAX_AMORTIZATION_MONTHS} months allowed",
                    "details": [f"Requested {payload.max_months} months"],
                },
            },
        )

    monthly_payment, total_payments, schedule = generate_amortization_schedule(
        payload.principal,
        payload.annual_rate,
        payload.years,
        payload.max_months,
    )

    return {
        "ok": True,
        "monthly_payment": monthly_payment,
        "total_payments": total_payments,
        "schedule": schedule,
    }


@router.post(
    "/v1/mortgage/summary",
    response_model=MortgageSummaryResponse,
    summary="Calculate Mortgage Summary",
    description=(
        "Calculate key mortgage metrics including monthly payment, total paid, "
        "total interest, and payoff month count/date."
    ),
    response_description="Mortgage summary",
    tags=["Mortgage"],
)
def mortgage_summary_endpoint(payload: MortgageSummaryRequest):
    """
    Mortgage summary endpoint.

    Returns human-friendly mortgage information:
    - `monthly_payment`: monthly payment amount
    - `total_paid`: total amount paid over the life of the loan
    - `total_interest`: interest portion of `total_paid`
    - `payoff_months`: number of months until payoff
    - `payoff_date`: estimated payoff date in `YYYY-MM` format
    """
    result = calculate_mortgage_summary(
        payload.principal,
        payload.annual_rate,
        payload.years,
    )
    return {"ok": True, **result}


@router.post(
    "/v1/mortgage/with-extra-payments",
    response_model=MortgageWithExtraPaymentsResponse,
    summary="Calculate Mortgage with Extra Payments",
    description="Calculate mortgage payoff impact of making extra principal payments each month.",
    response_description="Mortgage metrics with extra payments",
    tags=["Mortgage"],
)
def mortgage_with_extra_payments_endpoint(payload: MortgageWithExtraPaymentsRequest):
    """
    Calculate mortgage payoff with extra monthly payments.

    This endpoint shows the impact of making extra principal payments each month:
    - How many months you'll save
    - How much interest you'll save
    - New payoff date
    """
    result = calculate_mortgage_with_extra_payments(
        payload.principal,
        payload.annual_rate,
        payload.years,
        payload.extra_monthly_payment,
    )
    return {"ok": True, **result}
