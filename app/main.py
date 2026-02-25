from fastapi import FastAPI, Request, status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import math
from datetime import datetime
from typing import List

# Optional scipy import for advanced calculations
try:
    from scipy.optimize import fsolve, root_scalar
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    fsolve = None
    root_scalar = None

app = FastAPI(
    title="Finance Calculations API",
    version="1.0.0",
    description="Stateless JSON API for financial calculations"
)

# CORS Middleware - Allow requests from GitHub Pages and localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Local FastAPI / Swagger
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        # Local static client (python -m http.server 3000)
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        # GitHub Pages
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

# Mortgage Models
class MortgagePaymentRequest(BaseModel):
    """Request model for mortgage payment calculation."""
    principal: float = Field(..., ge=0, description="Loan principal amount (must be >= 0)", examples=[300000, 500000])
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
    principal: float = Field(..., ge=0, description="Loan principal amount (must be >= 0)", examples=[300000, 500000])
    annual_rate: float = Field(..., ge=0, le=1, description="Annual interest rate as decimal", examples=[0.04, 0.05])
    years: float = Field(..., gt=0, description="Loan term in years (must be > 0)", examples=[15, 30])
    max_months: int = Field(600, ge=1, le=600, description="Maximum number of months to return (default: 600, max: 600)", examples=[360, 600])
    
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

# Bond Models
class BondYieldRequest(BaseModel):
    """Request model for bond yield calculation."""
    face_value: float = Field(..., gt=0, description="Face value of the bond (must be > 0)", examples=[1000, 10000])
    coupon_rate: float = Field(..., ge=0, le=1, description="Annual coupon rate as decimal (e.g., 0.05 for 5%)", examples=[0.05, 0.06])
    years_to_maturity: float = Field(..., gt=0, description="Years to maturity (must be > 0)", examples=[5, 10, 30])
    current_price: float = Field(..., gt=0, description="Current market price of the bond (must be > 0)", examples=[950, 1050])
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

# XIRR Models
class CashFlow(BaseModel):
    """Single cash flow entry."""
    amount: float = Field(..., description="Cash flow amount (negative for outflow, positive for inflow)")
    date: str = Field(..., description="Date in YYYY-MM-DD format", examples=["2024-01-01", "2024-12-31"])
    
    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError('date must be in YYYY-MM-DD format')
        return v

class XIRRRequest(BaseModel):
    """Request model for XIRR calculation."""
    cashflows: List[CashFlow] = Field(..., min_length=2, description="List of cash flows (must have at least 2)")
    max_cashflows: int = Field(1000, ge=2, le=1000, description="Maximum number of cash flows allowed (default: 1000, max: 1000)")
    initial_guess: float = Field(0.1, description="Initial guess for IRR (default: 0.1)", examples=[0.1, 0.05])
    
    @field_validator('cashflows')
    @classmethod
    def validate_cashflows(cls, v):
        if len(v) < 2:
            raise ValueError('cashflows must have at least 2 entries')
        if len(v) > 1000:
            raise ValueError('cashflows cannot exceed 1000 entries')
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

# Constants for guards
MAX_AMORTIZATION_MONTHS = 600
MAX_XIRR_CASHFLOWS = 1000
SOLVER_TIMEOUT_SECONDS = 5

@app.post("/v1/mortgage/payment", 
          response_model=MortgagePaymentResponse,
          summary="Calculate Mortgage Payment",
          description="Calculate the monthly payment for a fixed-rate mortgage.",
          response_description="Monthly payment amount",
          tags=["Mortgage"])
def calculate_mortgage_payment(payload: MortgagePaymentRequest):
    """
    Calculate the monthly payment for a fixed-rate mortgage.
    
    Uses the standard mortgage payment formula:
    M = P × [r(1+r)^n] / [(1+r)^n - 1]
    
    Where:
    - **M** = monthly payment
    - **P** = principal (loan amount)
    - **r** = monthly interest rate (annual_rate / 12)
    - **n** = total number of payments (years × 12)
    
    **Example Request:**
    ```json
    {
        "principal": 300000,
        "annual_rate": 0.04,
        "years": 30
    }
    ```
    
    **Example Response:**
    ```json
    {
        "ok": true,
        "monthly_payment": 1432.25
    }
    ```
    """
    principal = payload.principal
    annual_rate = payload.annual_rate
    years = payload.years
    
    # Calculate monthly payment
    monthly_rate = annual_rate / 12
    num_payments = years * 12
    
    if monthly_rate == 0:
        # No interest case
        monthly_payment = principal / num_payments
    else:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
    
    return {"ok": True, "monthly_payment": round(monthly_payment, 2)}

@app.post("/v1/mortgage/amortization-schedule", 
          response_model=AmortizationScheduleResponse,
          summary="Generate Amortization Schedule",
          description="Generate an amortization schedule for a mortgage. Limited to max_months (default: 600).",
          response_description="Amortization schedule",
          tags=["Mortgage"])
def generate_amortization_schedule(payload: AmortizationScheduleRequest):
    """
    Generate an amortization schedule for a fixed-rate mortgage.
    
    Returns a detailed payment schedule showing principal and interest breakdown
    for each payment period.
    
    **Guards:**
    - Maximum 600 months (50 years) to prevent excessive output
    
    **Example Request:**
    ```json
    {
        "principal": 300000,
        "annual_rate": 0.04,
        "years": 30,
        "max_months": 360
    }
    ```
    
    **Example Response:**
    ```json
    {
        "ok": true,
        "monthly_payment": 1432.25,
        "total_payments": 360,
        "schedule": [
            {
                "month": 1,
                "payment": 1432.25,
                "principal_payment": 432.25,
                "interest_payment": 1000.00,
                "remaining_balance": 299567.75
            },
            ...
        ]
    }
    ```
    """
    principal = payload.principal
    annual_rate = payload.annual_rate
    years = payload.years
    max_months = payload.max_months
    
    # Calculate monthly payment
    monthly_rate = annual_rate / 12
    total_payments = int(years * 12)
    
    if monthly_rate == 0:
        monthly_payment = principal / total_payments
    else:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** total_payments) / ((1 + monthly_rate) ** total_payments - 1)
    
    # Generate schedule (limited by max_months)
    schedule = []
    balance = principal
    months_to_generate = min(total_payments, max_months)
    
    for month in range(1, months_to_generate + 1):
        interest_payment = balance * monthly_rate
        principal_payment = monthly_payment - interest_payment
        balance = balance - principal_payment
        
        # Handle final payment adjustment
        if month == months_to_generate and months_to_generate < total_payments:
            # Don't adjust, just show remaining
            pass
        elif balance < 0.01:
            balance = 0
        
        schedule.append(AmortizationPayment(
            month=month,
            payment=round(monthly_payment, 2),
            principal_payment=round(principal_payment, 2),
            interest_payment=round(interest_payment, 2),
            remaining_balance=round(balance, 2)
        ))
    
    return {
        "ok": True,
        "monthly_payment": round(monthly_payment, 2),
        "total_payments": total_payments,
        "schedule": schedule
    }

def _calculate_bond_yield(face_value, coupon_rate, years_to_maturity, current_price, payments_per_year):
    """Calculate bond yield to maturity using numerical solver."""
    coupon_payment = (face_value * coupon_rate) / payments_per_year
    total_payments = int(years_to_maturity * payments_per_year)
    
    def bond_present_value(yield_rate):
        """Calculate present value of bond at given yield."""
        pv_coupons = 0
        for i in range(1, total_payments + 1):
            pv_coupons += coupon_payment / ((1 + yield_rate / payments_per_year) ** i)
        pv_face = face_value / ((1 + yield_rate / payments_per_year) ** total_payments)
        return pv_coupons + pv_face - current_price
    
    # Use scipy if available (more accurate)
    if SCIPY_AVAILABLE:
        try:
            result = root_scalar(bond_present_value, bracket=[0.0, 1.0], method='brentq')
            return result.root
        except ValueError:
            # Fallback to fsolve
            result = fsolve(bond_present_value, 0.05)
            return float(result[0])
    else:
        # Fallback: Simple bisection method (no scipy required)
        low, high = 0.0, 1.0
        tolerance = 1e-6
        max_iterations = 100
        
        for _ in range(max_iterations):
            mid = (low + high) / 2
            pv = bond_present_value(mid)
            
            if abs(pv) < tolerance:
                return mid
            
            if pv > 0:
                low = mid
            else:
                high = mid
        
        # Return best guess if convergence not reached
        return (low + high) / 2

@app.post("/v1/bond/yield", 
          response_model=BondYieldResponse,
          summary="Calculate Bond Yield to Maturity",
          description="Calculate the yield to maturity for a bond using numerical solver.",
          response_description="Yield to maturity",
          tags=["Bonds"])
def calculate_bond_yield(payload: BondYieldRequest):
    """
    Calculate the yield to maturity (YTM) for a bond.
    
    Uses numerical methods to solve for the yield that equates the present value
    of all future cash flows to the current bond price.
    
    **Guards:**
    - 5 second timeout for solver
    
    **Example Request:**
    ```json
    {
        "face_value": 1000,
        "coupon_rate": 0.05,
        "years_to_maturity": 10,
        "current_price": 950,
        "payments_per_year": 2
    }
    ```
    
    **Example Response:**
    ```json
    {
        "ok": true,
        "yield_to_maturity": 0.055
    }
    ```
    """
    # Note: Bond yield now works without scipy (uses bisection method as fallback)
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                _calculate_bond_yield,
                payload.face_value,
                payload.coupon_rate,
                payload.years_to_maturity,
                payload.current_price,
                payload.payments_per_year
            )
            yield_result = future.result(timeout=SOLVER_TIMEOUT_SECONDS)
            
        return {"ok": True, "yield_to_maturity": round(yield_result, 6)}
    except FutureTimeoutError:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail={
                "ok": False,
                "error": {
                    "code": "SOLVER_TIMEOUT",
                    "message": f"Solver exceeded timeout of {SOLVER_TIMEOUT_SECONDS} seconds",
                    "details": []
                }
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "ok": False,
                "error": {
                    "code": "SOLVER_ERROR",
                    "message": f"Failed to calculate bond yield: {str(e)}",
                    "details": []
                }
            }
        )

def _calculate_xirr(cashflows, initial_guess):
    """Calculate XIRR using numerical solver."""
    # Parse dates and calculate days from first date
    dates = [datetime.strptime(cf.date, "%Y-%m-%d") for cf in cashflows]
    first_date = dates[0]
    days_from_first = [(d - first_date).days for d in dates]
    
    def npv(rate):
        """Calculate Net Present Value at given rate."""
        total = 0
        for i, cf in enumerate(cashflows):
            years = days_from_first[i] / 365.0
            total += cf.amount / ((1 + rate) ** years)
        return total
    
    # Use scipy if available (more accurate)
    if SCIPY_AVAILABLE:
        try:
            result = root_scalar(npv, bracket=[-0.99, 10.0], method='brentq', x0=initial_guess)
            return result.root
        except ValueError:
            # Fallback to fsolve
            result = fsolve(npv, initial_guess)
            return float(result[0])
    else:
        # Fallback: Simple bisection method (no scipy required)
        low, high = -0.99, 10.0
        tolerance = 1e-6
        max_iterations = 100
        
        # Adjust bounds if initial guess suggests different range
        if initial_guess > 0 and initial_guess < 1:
            low, high = -0.5, 2.0
        
        for _ in range(max_iterations):
            mid = (low + high) / 2
            npv_value = npv(mid)
            
            if abs(npv_value) < tolerance:
                return mid
            
            if npv_value > 0:
                low = mid
            else:
                high = mid
        
        # Return best guess if convergence not reached
        return (low + high) / 2

@app.post("/v1/xirr", 
          response_model=XIRRResponse,
          summary="Calculate XIRR",
          description="Calculate Extended Internal Rate of Return for irregular cash flows with dates.",
          response_description="XIRR value",
          tags=["Time Value of Money"])
def calculate_xirr(payload: XIRRRequest):
    """
    Calculate the Extended Internal Rate of Return (XIRR) for irregular cash flows.
    
    XIRR is used when cash flows occur at irregular intervals. It calculates
    the annualized return rate that makes the Net Present Value (NPV) equal to zero.
    
    **Guards:**
    - Maximum 1000 cash flows
    - 5 second timeout for solver
    
    **Example Request:**
    ```json
    {
        "cashflows": [
            {"amount": -10000, "date": "2024-01-01"},
            {"amount": 2000, "date": "2024-06-30"},
            {"amount": 3000, "date": "2024-12-31"},
            {"amount": 5000, "date": "2025-12-31"}
        ],
        "max_cashflows": 1000,
        "initial_guess": 0.1
    }
    ```
    
    **Example Response:**
    ```json
    {
        "ok": true,
        "xirr": 0.15
    }
    ```
    """
    # Note: XIRR now works without scipy (uses bisection method as fallback)
    # Guard: Check cashflow count
    if len(payload.cashflows) > MAX_XIRR_CASHFLOWS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "ok": False,
                "error": {
                    "code": "TOO_MANY_CASHFLOWS",
                    "message": f"Maximum {MAX_XIRR_CASHFLOWS} cash flows allowed",
                    "details": [f"Received {len(payload.cashflows)} cash flows"]
                }
            }
        )
    
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                _calculate_xirr,
                payload.cashflows,
                payload.initial_guess
            )
            xirr_result = future.result(timeout=SOLVER_TIMEOUT_SECONDS)
            
        return {"ok": True, "xirr": round(xirr_result, 6)}
    except FutureTimeoutError:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail={
                "ok": False,
                "error": {
                    "code": "SOLVER_TIMEOUT",
                    "message": f"Solver exceeded timeout of {SOLVER_TIMEOUT_SECONDS} seconds",
                    "details": []
                }
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "ok": False,
                "error": {
                    "code": "SOLVER_ERROR",
                    "message": f"Failed to calculate XIRR: {str(e)}",
                    "details": []
                }
            }
        )
