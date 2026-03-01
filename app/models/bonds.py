"""Bond calculation models."""
from pydantic import BaseModel, Field, field_validator
from app.core.config import MAX_AMOUNT


class BondYieldRequest(BaseModel):
    """Request model for bond yield calculation."""
    face_value: float = Field(
        ...,
        gt=0,
        le=MAX_AMOUNT,
        description="Face value of the bond (must be > 0 and <= MAX_AMOUNT)",
        examples=[1000, 10000],
    )
    coupon_rate: float = Field(..., ge=0, le=1, description="Annual coupon rate as decimal (e.g., 0.05 for 5%)", examples=[0.05, 0.06])
    years_to_maturity: float = Field(..., gt=0, description="Years to maturity (must be > 0)", examples=[5, 10, 30])
    current_price: float = Field(
        ...,
        gt=0,
        le=MAX_AMOUNT,
        description="Current market price of the bond (must be > 0 and <= MAX_AMOUNT)",
        examples=[950, 1050],
    )
    payments_per_year: int = Field(2, ge=1, le=12, description="Number of coupon payments per year (default: 2 for semi-annual)", examples=[2, 4, 12])
    
    @field_validator('coupon_rate')
    @classmethod
    def validate_rate(cls, v):
        if v < 0:
            raise ValueError('coupon_rate must be >= 0')
        if v > 1:
            raise ValueError('coupon_rate must be <= 1 (100%)')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "face_value": 1000,
                "coupon_rate": 0.05,
                "years_to_maturity": 10,
                "current_price": 950,
                "payments_per_year": 2
            }
        }


class BondYieldResponse(BaseModel):
    """Response model for bond yield calculation."""
    ok: bool = Field(..., description="Indicates if the calculation was successful", examples=[True])
    yield_to_maturity: float = Field(..., description="Yield to maturity as decimal (e.g., 0.055 for 5.5%)", examples=[0.055, 0.062])


class BondPriceRequest(BaseModel):
    """Request model for bond price calculation from yield."""

    face_value: float = Field(
        ...,
        gt=0,
        le=MAX_AMOUNT,
        description="Face value of the bond (must be > 0 and <= MAX_AMOUNT)",
        examples=[1000, 10000],
    )
    coupon_rate: float = Field(
        ...,
        ge=0,
        le=1,
        description="Annual coupon rate as decimal (e.g., 0.05 for 5%)",
        examples=[0.05, 0.06],
    )
    years_to_maturity: float = Field(..., gt=0, description="Years to maturity (must be > 0)", examples=[5, 10, 30])
    yield_to_maturity: float = Field(
        ...,
        ge=0,
        le=1,
        description="Yield to maturity as decimal (e.g., 0.055 for 5.5%)",
        examples=[0.055, 0.062],
    )
    payments_per_year: int = Field(
        2,
        ge=1,
        le=12,
        description="Number of coupon payments per year (default: 2 for semi-annual)",
        examples=[2, 4, 12],
    )

    @field_validator("coupon_rate", "yield_to_maturity")
    @classmethod
    def validate_rates(cls, v: float) -> float:
        if v < 0:
            raise ValueError("rate must be >= 0")
        if v > 1:
            raise ValueError("rate must be <= 1 (100%)")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "face_value": 1000,
                "coupon_rate": 0.05,
                "years_to_maturity": 10,
                "yield_to_maturity": 0.055,
                "payments_per_year": 2,
            }
        }


class BondPriceResponse(BaseModel):
    """Response model for bond price calculation."""

    ok: bool = Field(..., description="Indicates if the calculation was successful", examples=[True])
    price: float = Field(..., description="Bond price", examples=[980.50, 1020.25])
