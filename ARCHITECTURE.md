# Architecture Documentation

This document describes the modular architecture of the financial-calculations-api project.

## Overview

The project follows a **layered architecture** pattern with clear separation between:
- **API Layer** (routes): HTTP request/response handling
- **Service Layer**: Pure business logic
- **Model Layer**: Data validation and serialization
- **Core Layer**: Configuration and cross-cutting concerns

## Directory Structure

```
app/
├── main.py              # FastAPI app entry point (34 lines)
├── core/                # Core configuration and error handling
│   ├── config.py        # Constants, CORS, metadata, scipy imports
│   └── errors.py        # Exception handlers and custom exceptions
├── models/              # Pydantic request/response models
│   ├── common.py        # Common models (ErrorDetail, ErrorResponse, Echo)
│   ├── tvm.py           # Time Value of Money models
│   ├── mortgage.py      # Mortgage calculation models
│   ├── bonds.py         # Bond calculation models
│   └── xirr.py          # XIRR calculation models
├── services/            # Pure business logic (no FastAPI dependencies)
│   ├── tvm.py           # TVM calculation services
│   ├── mortgage.py      # Mortgage calculation services
│   ├── bonds.py         # Bond calculation services
│   └── xirr.py          # XIRR calculation services
└── api/
    └── routes/           # FastAPI route handlers
        ├── system.py     # Health, echo, info endpoints
        ├── tvm.py        # TVM endpoints
        ├── mortgage.py   # Mortgage endpoints
        ├── bonds.py      # Bond endpoints
        └── xirr.py       # XIRR endpoints
```

## Layer Responsibilities

### 1. Core Layer (`app/core/`)

**Purpose**: Shared configuration and cross-cutting concerns.

#### `config.py`
- Application constants (MAX_AMOUNT, MAX_AMORTIZATION_MONTHS, etc.)
- CORS configuration (ALLOWED_ORIGINS)
- Build metadata (BUILD_TIMESTAMP, GIT_SHA, ENVIRONMENT)
- Optional scipy imports with fallback

#### `errors.py`
- Exception handlers for unified error responses
- Custom exceptions (NoSolutionError)
- Error response formatting

### 2. Model Layer (`app/models/`)

**Purpose**: Data validation and serialization using Pydantic.

**Rules**:
- Models contain **only** Pydantic `BaseModel` classes
- No business logic
- No FastAPI dependencies
- Field validation and examples for Swagger documentation

**Example**:
```python
class FutureValueRequest(BaseModel):
    principal: float = Field(..., ge=0, le=MAX_AMOUNT)
    annual_rate: float = Field(..., ge=0, le=1)
    years: float = Field(..., gt=0)
    compounds_per_year: int = Field(..., gt=0)
```

### 3. Service Layer (`app/services/`)

**Purpose**: Pure business logic calculations.

**Rules**:
- **No FastAPI dependencies** (no `HTTPException`, no `Request`, etc.)
- **No HTTP concerns** (status codes, headers, etc.)
- Functions take primitive types or model instances
- Functions return primitive types or dictionaries
- Raise custom exceptions (e.g., `NoSolutionError`) for business logic errors
- Easily testable without FastAPI

**Example**:
```python
def calculate_future_value(
    principal: float,
    annual_rate: float,
    years: float,
    compounds_per_year: int
) -> float:
    """Calculate future value using compound interest."""
    rate_per_period = annual_rate / compounds_per_year
    total_periods = compounds_per_year * years
    future_value = principal * (1 + rate_per_period) ** total_periods
    return round(future_value, 2)
```

### 4. API Layer (`app/api/routes/`)

**Purpose**: HTTP request/response handling.

**Rules**:
- FastAPI route decorators (`@router.post`, `@router.get`)
- Request/response models from `app/models/`
- Call service functions from `app/services/`
- Handle HTTP exceptions and convert service exceptions to HTTP responses
- Return properly formatted responses

**Example**:
```python
@router.post("/v1/tvm/future-value", response_model=FutureValueResponse)
def calculate_future_value(payload: FutureValueRequest):
    """Calculate the future value of an investment."""
    future_value = calc_fv(
        payload.principal,
        payload.annual_rate,
        payload.years,
        payload.compounds_per_year,
    )
    return {"ok": True, "future_value": future_value}
```

## Request Flow

```
1. HTTP Request
   ↓
2. FastAPI Router (app/api/routes/*)
   - Validates request using Pydantic models
   - Extracts parameters
   ↓
3. Service Layer (app/services/*)
   - Performs business logic calculations
   - May raise custom exceptions
   ↓
4. Router (app/api/routes/*)
   - Handles exceptions
   - Formats response
   ↓
5. HTTP Response
```

## Error Handling

### Service Layer Errors

Services raise custom exceptions:
- `NoSolutionError`: When a numerical solver cannot find a solution

### Route Layer Error Handling

Routes catch service exceptions and convert them to HTTP responses:

```python
try:
    result = calculate_bond_yield(...)
except NoSolutionError as e:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "ok": False,
            "error": {
                "code": "NO_SOLUTION",
                "message": str(e),
                "details": e.details,
            },
        },
    )
```

### Global Exception Handlers

`app/core/errors.py` provides global exception handlers:
- `validation_exception_handler`: Handles Pydantic validation errors
- `http_exception_handler`: Formats HTTPException responses consistently

## Adding New Features

### Adding a New Endpoint

1. **Add models** in `app/models/<domain>.py`:
   ```python
   class NewRequest(BaseModel):
       field: float = Field(...)
   
   class NewResponse(BaseModel):
       ok: bool
       result: float
   ```

2. **Add service function** in `app/services/<domain>.py`:
   ```python
   def calculate_new(field: float) -> float:
       """Pure calculation logic."""
       return field * 2
   ```

3. **Add route** in `app/api/routes/<domain>.py`:
   ```python
   @router.post("/v1/domain/new", response_model=NewResponse)
   def new_endpoint(payload: NewRequest):
       result = calculate_new(payload.field)
       return {"ok": True, "result": result}
   ```

4. **Register router** in `app/main.py` (if new domain):
   ```python
   from app.api.routes import new_domain
   app.include_router(new_domain.router)
   ```

## Testing Strategy

### Service Layer Tests

Services can be tested independently:

```python
def test_calculate_future_value():
    result = calculate_future_value(10000, 0.07, 10, 12)
    assert abs(result - 19671.51) < 0.01
```

### Route Layer Tests

Routes are tested using FastAPI's `TestClient`:

```python
def test_future_value_endpoint():
    response = client.post("/v1/tvm/future-value", json={
        "principal": 10000,
        "annual_rate": 0.07,
        "years": 10,
        "compounds_per_year": 12
    })
    assert response.status_code == 200
    assert response.json()["ok"] is True
```

## Benefits of This Architecture

1. **Separation of Concerns**: Each layer has a single, well-defined responsibility
2. **Testability**: Services can be tested without FastAPI, routes can be tested with TestClient
3. **Reusability**: Service functions can be reused in different contexts (CLI, background jobs, etc.)
4. **Maintainability**: Changes are isolated to specific layers
5. **Scalability**: Easy to add new endpoints and domains
6. **Type Safety**: Pydantic models provide runtime validation and type hints

## Migration from Monolithic Structure

The project was refactored from a single `app/main.py` file (1721 lines) to this modular structure:

- **Before**: All code in `app/main.py` (models, services, routes, config)
- **After**: Organized into 4 layers across 20+ files
- **Result**: `app/main.py` reduced to 34 lines (only app initialization)

This refactoring improves:
- Code organization
- Developer experience
- Testability
- Maintainability
