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
    """Echo request model for testing API connectivity."""
    message: str = Field(..., description="Message to echo back", examples=["Hello, World!", "Test message"])
    number: int | None = Field(None, description="Optional number to include in response", examples=[42, 100])

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Hello, World!",
                "number": 42
            }
        }

class EchoResponse(BaseModel):
    """Echo response model."""
    ok: bool = Field(..., description="Indicates if the request was successful", examples=[True])
    echo: EchoRequest = Field(..., description="Echoed request payload")

# Time Value of Money Models
class FutureValueRequest(BaseModel):
    """Request model for compound interest future value calculation.
    
    Calculates the future value of an investment using compound interest.
    Formula: FV = P * (1 + r/n)^(n*t)
    
    Note: annual_rate is a decimal (e.g., 0.07 for 7%, not 7).
    """
    principal: float = Field(
        ..., 
        ge=0, 
        description="Initial principal amount (must be >= 0)",
        examples=[10000, 5000, 25000]
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

@app.get("/v1/health", 
         summary="Health Check",
         description="Check if the API service is running and healthy.",
         response_description="Service health status",
         tags=["System"])
def health():
    """
    Health check endpoint.
    
    Returns the current status of the API service including:
    - Service name
    - API version
    
    Use this endpoint to verify the API is operational.
    """
    return {"ok": True, "service": "finance-api", "version": "v1"}

@app.post("/v1/echo", 
          response_model=EchoResponse,
          summary="Echo Endpoint",
          description="Echo back the request payload. Useful for testing API connectivity and request/response handling.",
          response_description="Echoed request payload",
          tags=["Testing"])
def echo(payload: EchoRequest):
    """
    Echo endpoint for testing.
    
    This endpoint accepts a request payload and returns it back unchanged.
    Useful for:
    - Testing API connectivity
    - Verifying request/response handling
    - Debugging CORS and authentication issues
    
    **Example Request:**
    ```json
    {
        "message": "Hello, World!",
        "number": 42
    }
    ```
    
    **Example Response:**
    ```json
    {
        "ok": true,
        "echo": {
            "message": "Hello, World!",
            "number": 42
        }
    }
    ```
    """
    return {"ok": True, "echo": payload}

@app.post("/v1/tvm/future-value", 
          response_model=FutureValueResponse,
          summary="Calculate Future Value",
          description="Calculate the future value of an investment using compound interest.",
          response_description="Calculated future value",
          tags=["Time Value of Money"])
def calculate_future_value(payload: FutureValueRequest):
    """
    Calculate the future value of an investment using compound interest.
    
    This endpoint calculates how much an investment will be worth after a specified
    number of years with compound interest.
    
    **Formula:** FV = P × (1 + r/n)^(n×t)
    
    Where:
    - **P** = principal (initial amount)
    - **r** = annual interest rate (as decimal, e.g., 0.07 for 7%)
    - **n** = number of compounding periods per year
    - **t** = number of years
    
    **Important Notes:**
    - The `annual_rate` must be provided as a decimal (0.07 for 7%, not 7)
    - Common compounding frequencies:
      - 1 = annually
      - 4 = quarterly
      - 12 = monthly
      - 365 = daily
    
    **Example Request:**
    ```json
    {
        "principal": 10000,
        "annual_rate": 0.07,
        "years": 10,
        "compounds_per_year": 12
    }
    ```
    
    This calculates: $10,000 invested at 7% APR, compounded monthly for 10 years.
    
    **Example Response:**
    ```json
    {
        "ok": true,
        "future_value": 19671.51
    }
    ```
    
    The result is rounded to 2 decimal places.
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
