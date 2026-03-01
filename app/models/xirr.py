"""XIRR calculation models."""
from typing import List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from app.core.config import MAX_AMOUNT, MAX_XIRR_CASHFLOWS


class CashFlow(BaseModel):
    """Single cash flow entry."""
    amount: float = Field(
        ...,
        description="Cash flow amount (negative for outflow, positive for inflow, abs(amount) <= MAX_AMOUNT)",
    )
    date: str = Field(..., description="Date in YYYY-MM-DD format", examples=["2024-01-01", "2024-12-31"])
    
    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError('date must be in YYYY-MM-DD format')
        return v
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if abs(v) > MAX_AMOUNT:
            raise ValueError(f"amount absolute value must be <= {MAX_AMOUNT}")
        return v


class XIRRRequest(BaseModel):
    """Request model for XIRR calculation."""
    cashflows: List[CashFlow] = Field(..., min_length=2, description="List of cash flows (must have at least 2)")
    max_cashflows: int = Field(MAX_XIRR_CASHFLOWS, ge=2, le=MAX_XIRR_CASHFLOWS, description="Maximum number of cash flows allowed (default: 1000, max: 1000)")
    initial_guess: float = Field(0.1, description="Initial guess for IRR (default: 0.1)", examples=[0.1, 0.05])
    
    @field_validator('cashflows')
    @classmethod
    def validate_cashflows(cls, v):
        if len(v) < 2:
            raise ValueError('cashflows must have at least 2 entries')
        if len(v) > MAX_XIRR_CASHFLOWS:
            raise ValueError(f'cashflows cannot exceed {MAX_XIRR_CASHFLOWS} entries')
        # First cashflow should typically be negative (investment)
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "cashflows": [
                    {"amount": -10000, "date": "2024-01-01"},
                    {"amount": 2000, "date": "2024-06-30"},
                    {"amount": 3000, "date": "2024-12-31"},
                    {"amount": 5000, "date": "2025-12-31"}
                ],
                "max_cashflows": 1000,
                "initial_guess": 0.1
            }
        }


class XIRRResponse(BaseModel):
    """Response model for XIRR calculation."""
    ok: bool = Field(..., description="Indicates if the calculation was successful", examples=[True])
    xirr: float = Field(..., description="Extended Internal Rate of Return as decimal (e.g., 0.15 for 15%)", examples=[0.15, 0.20])


class XIRRExplainResponse(BaseModel):
    """Response model for XIRR explanation."""

    ok: bool = Field(..., description="Indicates if the calculation was successful", examples=[True])
    xirr: float = Field(..., description="Computed XIRR as decimal (e.g., 0.15 for 15%)", examples=[0.15])
    iterations: int = Field(..., description="Number of iterations used by the solver", examples=[25])
    solver_type: str = Field(
        ...,
        description="Solver used (e.g., 'scipy-brentq' or 'bisection')",
        examples=["scipy-brentq"],
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="List of warnings about the solution (e.g., potential multiple IRRs).",
    )
