"""Time Value of Money models."""
from pydantic import BaseModel, Field, field_validator
from app.core.config import MAX_AMOUNT


class FutureValueRequest(BaseModel):
    """Request model for compound interest future value calculation.
    
    Calculates the future value of an investment using compound interest.
    Formula: FV = P * (1 + r/n)^(n*t)
    
    Note: annual_rate is a decimal (e.g., 0.07 for 7%, not 7).
    """
    principal: float = Field(
        ...,
        ge=0,
        le=MAX_AMOUNT,
        description="Initial principal amount (must be >= 0 and <= MAX_AMOUNT)",
        examples=[10000, 5000, 25000],
    )
    annual_rate: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Annual interest rate as decimal (e.g., 0.07 for 7%, 0.05 for 5%)",
        examples=[0.07, 0.05, 0.10]
    )
    years: float = Field(
        ..., 
        gt=0, 
        description="Number of years (must be > 0)",
        examples=[10, 5, 20, 30]
    )
    compounds_per_year: int = Field(
        ..., 
        gt=0, 
        description="Number of compounding periods per year (e.g., 12 for monthly, 4 for quarterly, 1 for annually)",
        examples=[12, 4, 1, 365]
    )
    
    @field_validator('annual_rate')
    @classmethod
    def validate_rate(cls, v):
        """Validate that rate is reasonable (0-100% as decimal)."""
        if v < 0:
            raise ValueError('annual_rate must be >= 0')
        if v > 1:
            raise ValueError('annual_rate must be <= 1 (100%). If you meant a percentage, convert to decimal (e.g., 7% = 0.07)')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "principal": 10000,
                "annual_rate": 0.07,
                "years": 10,
                "compounds_per_year": 12
            }
        }


class FutureValueResponse(BaseModel):
    """Response model for future value calculation."""
    ok: bool = Field(..., description="Indicates if the calculation was successful", examples=[True])
    future_value: float = Field(..., description="Calculated future value rounded to 2 decimal places", examples=[19671.51, 12762.82])


class PresentValueRequest(BaseModel):
    """Request model for present value calculation from a future value.

    Note: annual_rate is a decimal (e.g., 0.07 for 7%, not 7).
    """

    future_value: float = Field(
        ...,
        ge=0,
        le=MAX_AMOUNT,
        description="Future value amount (must be >= 0 and <= MAX_AMOUNT)",
        examples=[10000, 5000, 25000],
    )
    annual_rate: float = Field(
        ...,
        ge=0,
        le=1,
        description="Annual discount rate as decimal (e.g., 0.07 for 7%)",
        examples=[0.07, 0.05, 0.10],
    )
    years: float = Field(
        ...,
        gt=0,
        description="Number of years (must be > 0)",
        examples=[10, 5, 20, 30],
    )
    compounds_per_year: int = Field(
        ...,
        gt=0,
        description="Number of compounding periods per year (e.g., 12 for monthly, 4 for quarterly, 1 for annually)",
        examples=[12, 4, 1, 365],
    )

    @field_validator("annual_rate")
    @classmethod
    def validate_rate(cls, v):
        if v < 0:
            raise ValueError("annual_rate must be >= 0")
        if v > 1:
            raise ValueError("annual_rate must be <= 1 (100%). If you meant a percentage, convert to decimal (e.g., 7% = 0.07)")
        return v


class PresentValueResponse(BaseModel):
    """Response model for present value calculation."""

    ok: bool = Field(..., description="Indicates if the calculation was successful", examples=[True])
    present_value: float = Field(..., description="Calculated present value rounded to 2 decimal places", examples=[5083.49])


class AnnuityPaymentRequest(BaseModel):
    """Request model for level annuity payment calculation."""

    present_value: float = Field(
        ...,
        ge=0,
        le=MAX_AMOUNT,
        description="Present value (PV) of the annuity (must be >= 0 and <= MAX_AMOUNT)",
        examples=[10000, 50000],
    )
    annual_rate: float = Field(
        ...,
        ge=0,
        le=1,
        description="Annual interest rate as decimal (e.g., 0.05 for 5%)",
        examples=[0.05, 0.07],
    )
    years: float = Field(
        ...,
        gt=0,
        description="Number of years (must be > 0)",
        examples=[5, 10, 30],
    )
    payments_per_year: int = Field(
        ...,
        gt=0,
        description="Number of annuity payments per year (e.g., 12 for monthly, 4 for quarterly, 1 for annually)",
        examples=[12, 4, 1],
    )

    @field_validator("annual_rate")
    @classmethod
    def validate_rate(cls, v):
        if v < 0:
            raise ValueError("annual_rate must be >= 0")
        if v > 1:
            raise ValueError("annual_rate must be <= 1 (100%). If you meant a percentage, convert to decimal (e.g., 7% = 0.07)")
        return v


class AnnuityPaymentResponse(BaseModel):
    """Response model for level annuity payment calculation."""

    ok: bool = Field(..., description="Indicates if the calculation was successful", examples=[True])
    payment: float = Field(..., description="Level payment amount rounded to 2 decimal places", examples=[212.13])
