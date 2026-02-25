from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

app = FastAPI(
    title="Finance Calculations API",
    version="1.0.0",
    description="Stateless JSON API for financial calculations"
)

# CORS Middleware - Allow requests from GitHub Pages and localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://mytherapy-coding.github.io",
        "https://*.github.io",  # Allow all GitHub Pages domains
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Standard Error Response Models
class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list = []

class ErrorResponse(BaseModel):
    ok: bool = False
    error: ErrorDetail

# Request/Response Models
class EchoRequest(BaseModel):
    message: str
    number: int | None = None

class EchoResponse(BaseModel):
    ok: bool
    echo: EchoRequest

# Time Value of Money Models
class FutureValueRequest(BaseModel):
    """Request model for compound interest future value calculation.
    
    Note: annual_rate is a decimal (e.g., 0.07 for 7%, not 7).
    """
    principal: float = Field(..., ge=0, description="Initial principal amount (must be >= 0)")
    annual_rate: float = Field(..., ge=0, le=1, description="Annual interest rate as decimal (e.g., 0.07 for 7%)")
    years: float = Field(..., gt=0, description="Number of years (must be > 0)")
    compounds_per_year: int = Field(..., gt=0, description="Number of compounding periods per year (must be > 0)")
    
    @field_validator('annual_rate')
    @classmethod
    def validate_rate(cls, v):
        """Validate that rate is reasonable (0-100% as decimal)."""
        if v < 0:
            raise ValueError('annual_rate must be >= 0')
        if v > 1:
            raise ValueError('annual_rate must be <= 1 (100%). If you meant a percentage, convert to decimal (e.g., 7% = 0.07)')
        return v

class FutureValueResponse(BaseModel):
    ok: bool
    future_value: float

# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle FastAPI validation errors and return consistent error format."""
    details = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        details.append(f"{field}: {error['msg']}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "ok": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": details
            }
        }
    )

@app.get("/v1/health")
def health():
    return {"ok": True, "service": "finance-api", "version": "v1"}

@app.post("/v1/echo", response_model=EchoResponse)
def echo(payload: EchoRequest):
    return {"ok": True, "echo": payload}

@app.post("/v1/tvm/future-value", response_model=FutureValueResponse)
def calculate_future_value(payload: FutureValueRequest):
    """
    Calculate the future value of an investment using compound interest.
    
    Formula: FV = P * (1 + r/n)^(n*t)
    Where:
    - P = principal
    - r = annual_rate (as decimal, e.g., 0.07 for 7%)
    - n = compounds_per_year
    - t = years
    
    Example:
    - principal: 10000
    - annual_rate: 0.07 (7%)
    - years: 10
    - compounds_per_year: 12 (monthly)
    
    Returns the future value rounded to 2 decimal places.
    """
    principal = payload.principal
    annual_rate = payload.annual_rate
    years = payload.years
    compounds_per_year = payload.compounds_per_year
    
    # Calculate compound interest: FV = P * (1 + r/n)^(n*t)
    rate_per_period = annual_rate / compounds_per_year
    total_periods = compounds_per_year * years
    future_value = principal * (1 + rate_per_period) ** total_periods
    
    # Round to 2 decimal places
    future_value = round(future_value, 2)
    
    return {"ok": True, "future_value": future_value}
