"""Mortgage calculation models."""
from typing import List
from pydantic import BaseModel, Field, field_validator
from app.core.config import MAX_AMOUNT, MAX_AMORTIZATION_MONTHS


class MortgagePaymentRequest(BaseModel):
    """Request model for mortgage payment calculation."""
    principal: float = Field(
        ...,
        ge=0,
        le=MAX_AMOUNT,
        description="Loan principal amount (must be >= 0 and <= MAX_AMOUNT)",
        examples=[300000, 500000],
    )
    annual_rate: float = Field(..., ge=0, le=1, description="Annual interest rate as decimal (e.g., 0.04 for 4%)", examples=[0.04, 0.05, 0.06])
    years: float = Field(..., gt=0, description="Loan term in years (must be > 0)", examples=[15, 30])
    
    @field_validator('annual_rate')
    @classmethod
    def validate_rate(cls, v):
        if v < 0:
            raise ValueError('annual_rate must be >= 0')
        if v > 1:
            raise ValueError('annual_rate must be <= 1 (100%)')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "principal": 300000,
                "annual_rate": 0.04,
                "years": 30
            }
        }


class MortgagePaymentResponse(BaseModel):
    """Response model for mortgage payment calculation."""
    ok: bool = Field(..., description="Indicates if the calculation was successful", examples=[True])
    monthly_payment: float = Field(..., description="Monthly payment amount rounded to 2 decimal places", examples=[1432.25, 2684.11])


class AmortizationScheduleRequest(BaseModel):
    """Request model for amortization schedule calculation."""
    principal: float = Field(
        ...,
        ge=0,
        le=MAX_AMOUNT,
        description="Loan principal amount (must be >= 0 and <= MAX_AMOUNT)",
        examples=[300000, 500000],
    )
    annual_rate: float = Field(..., ge=0, le=1, description="Annual interest rate as decimal", examples=[0.04, 0.05])
    years: float = Field(..., gt=0, description="Loan term in years (must be > 0)", examples=[15, 30])
    max_months: int = Field(MAX_AMORTIZATION_MONTHS, ge=1, le=MAX_AMORTIZATION_MONTHS, description="Maximum number of months to return (default: 600, max: 600)", examples=[360, 600])
    
    @field_validator('annual_rate')
    @classmethod
    def validate_rate(cls, v):
        if v < 0:
            raise ValueError('annual_rate must be >= 0')
        if v > 1:
            raise ValueError('annual_rate must be <= 1 (100%)')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "principal": 300000,
                "annual_rate": 0.04,
                "years": 30,
                "max_months": 360
            }
        }


class AmortizationPayment(BaseModel):
    """Single payment in amortization schedule."""
    month: int = Field(..., description="Payment number (1-indexed)")
    payment: float = Field(..., description="Total payment amount")
    principal_payment: float = Field(..., description="Principal portion of payment")
    interest_payment: float = Field(..., description="Interest portion of payment")
    remaining_balance: float = Field(..., description="Remaining loan balance")


class AmortizationScheduleResponse(BaseModel):
    """Response model for amortization schedule."""
    ok: bool = Field(..., description="Indicates if the calculation was successful", examples=[True])
    monthly_payment: float = Field(..., description="Monthly payment amount")
    total_payments: int = Field(..., description="Total number of payments")
    schedule: List[AmortizationPayment] = Field(..., description="Amortization schedule (limited by max_months)")


class MortgageSummaryRequest(MortgagePaymentRequest):
    """Request model for mortgage summary calculation.

    Reuses the same fields and validation as `MortgagePaymentRequest`.
    """


class MortgageSummaryResponse(BaseModel):
    """Response model for mortgage summary calculation."""

    ok: bool = Field(..., description="Indicates if the calculation was successful", examples=[True])
    monthly_payment: float = Field(..., description="Monthly payment amount", examples=[1432.25])
    total_paid: float = Field(..., description="Total amount paid over the life of the loan", examples=[515610.0])
    total_interest: float = Field(..., description="Total interest paid over the life of the loan", examples=[215610.0])
    payoff_months: int = Field(..., description="Number of months until payoff", examples=[360])
    payoff_date: str = Field(
        ...,
        description="Estimated payoff date in YYYY-MM format, assuming payments start this month",
        examples=["2054-01"],
    )


class MortgageWithExtraPaymentsRequest(BaseModel):
    """Request model for mortgage calculation with extra payments."""

    principal: float = Field(
        ...,
        ge=0,
        le=MAX_AMOUNT,
        description="Loan principal amount (must be >= 0 and <= MAX_AMOUNT)",
        examples=[300000, 500000],
    )
    annual_rate: float = Field(
        ...,
        ge=0,
        le=1,
        description="Annual interest rate as decimal (e.g., 0.04 for 4%)",
        examples=[0.04, 0.05, 0.06],
    )
    years: float = Field(..., gt=0, description="Loan term in years (must be > 0)", examples=[15, 30])
    extra_monthly_payment: float = Field(
        ...,
        ge=0,
        le=MAX_AMOUNT,
        description="Extra payment amount to apply to principal each month (must be >= 0)",
        examples=[100, 200, 500],
    )

    @field_validator("annual_rate")
    @classmethod
    def validate_rate(cls, v):
        if v < 0:
            raise ValueError("annual_rate must be >= 0")
        if v > 1:
            raise ValueError("annual_rate must be <= 1 (100%)")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "principal": 300000,
                "annual_rate": 0.04,
                "years": 30,
                "extra_monthly_payment": 200,
            }
        }


class MortgageWithExtraPaymentsResponse(BaseModel):
    """Response model for mortgage with extra payments calculation."""

    ok: bool = Field(..., description="Indicates if the calculation was successful", examples=[True])
    regular_monthly_payment: float = Field(
        ..., description="Regular monthly payment (without extra)", examples=[1432.25]
    )
    total_monthly_payment: float = Field(
        ..., description="Total monthly payment (regular + extra)", examples=[1632.25]
    )
    original_payoff_months: int = Field(
        ..., description="Original payoff months (without extra payments)", examples=[360]
    )
    new_payoff_months: int = Field(
        ..., description="New payoff months (with extra payments)", examples=[280]
    )
    months_saved: int = Field(..., description="Number of months saved", examples=[80])
    original_total_interest: float = Field(
        ..., description="Total interest paid without extra payments", examples=[215610.0]
    )
    new_total_interest: float = Field(
        ..., description="Total interest paid with extra payments", examples=[165432.0]
    )
    interest_saved: float = Field(..., description="Total interest saved", examples=[50178.0])
    new_payoff_date: str = Field(
        ...,
        description="Estimated payoff date with extra payments (YYYY-MM format)",
        examples=["2046-05"],
    )
