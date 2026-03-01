# Test Coverage Documentation

This document describes the test coverage for the financial-calculations-api project.

## Test Statistics

- **Total Test Files**: 11
- **Total Test Functions**: ~80+ test cases
- **Coverage Areas**: Unit tests, integration tests, error handling, edge cases

## Test Files

### Core Endpoint Tests

1. **`test_health.py`** (2 tests)
   - Health check endpoint
   - Response structure validation

2. **`test_info.py`** (2 tests)
   - Service info endpoint
   - Metadata structure validation

3. **`test_echo.py`** (5 tests)
   - Basic echo functionality
   - Optional fields
   - Validation errors
   - Response structure

### Time Value of Money Tests

4. **`test_future_value.py`** (9 tests)
   - Basic future value calculation
   - Different compounding frequencies
   - Validation (negative values, zero values, rate limits)
   - Accuracy checks
   - Missing fields

5. **`test_tvm.py`** (10 tests)
   - Present value calculations
   - Annuity payment calculations
   - Zero rate handling
   - Validation for both endpoints
   - Response structure

### Mortgage Tests

6. **`test_mortgage.py`** (18 tests)
   - Mortgage payment calculation
   - Amortization schedule generation
   - Mortgage summary
   - Mortgage with extra payments
   - Zero interest handling
   - Max months guard
   - Validation errors
   - Response structure validation

### Bond Tests

7. **`test_bond.py`** (9 tests)
   - Bond yield calculation
   - Bond price calculation
   - Premium/par/discount bonds
   - Validation errors
   - Response structure

### XIRR Tests

8. **`test_xirr.py`** (10 tests)
   - Basic XIRR calculation
   - XIRR explain endpoint
   - Solver type detection
   - Warnings detection
   - Validation (min/max cashflows)
   - Date validation

### Error Handling Tests

9. **`test_error_handling.py`** (9 tests)
   - NO_SOLUTION errors (bond yield, XIRR)
   - MAX_AMOUNT validation
   - Negative/zero value validation
   - Error response format consistency
   - Max months validation
   - Too many cashflows validation

### Integration Tests

10. **`test_integration.py`** (6 tests)
    - TVM round-trip (future value ↔ present value)
    - Bond price/yield round-trip
    - Mortgage summary consistency
    - Mortgage with extra payments consistency
    - All endpoints return `ok` field
    - XIRR explain metadata

### Edge Cases Tests

11. **`test_edge_cases.py`** (12 tests)
    - Very small/large principal amounts
    - Very high interest rates
    - Very long/short terms
    - Daily compounding
    - Zero coupon bonds
    - Minimal/maximal cashflows
    - Zero rate calculations

## Coverage by Endpoint

| Endpoint | Test File | Coverage |
|----------|-----------|----------|
| `GET /v1/health` | `test_health.py` | ✅ Full |
| `GET /v1/info` | `test_info.py` | ✅ Full |
| `POST /v1/echo` | `test_echo.py` | ✅ Full |
| `POST /v1/tvm/future-value` | `test_future_value.py`, `test_edge_cases.py` | ✅ Full |
| `POST /v1/tvm/present-value` | `test_tvm.py`, `test_integration.py`, `test_edge_cases.py` | ✅ Full |
| `POST /v1/tvm/annuity-payment` | `test_tvm.py`, `test_edge_cases.py` | ✅ Full |
| `POST /v1/mortgage/payment` | `test_mortgage.py`, `test_edge_cases.py` | ✅ Full |
| `POST /v1/mortgage/amortization-schedule` | `test_mortgage.py`, `test_error_handling.py` | ✅ Full |
| `POST /v1/mortgage/summary` | `test_mortgage.py`, `test_integration.py` | ✅ Full |
| `POST /v1/mortgage/with-extra-payments` | `test_mortgage.py`, `test_integration.py` | ✅ Full |
| `POST /v1/bond/yield` | `test_bond.py`, `test_error_handling.py`, `test_integration.py` | ✅ Full |
| `POST /v1/bond/price` | `test_bond.py`, `test_integration.py`, `test_edge_cases.py` | ✅ Full |
| `POST /v1/xirr` | `test_xirr.py`, `test_error_handling.py`, `test_edge_cases.py` | ✅ Full |
| `POST /v1/xirr/explain` | `test_xirr.py`, `test_integration.py` | ✅ Full |

## Test Categories

### 1. Unit Tests
- Test individual endpoints in isolation
- Validate request/response models
- Check calculation accuracy
- Verify response structure

### 2. Integration Tests
- Test round-trip operations (e.g., future value → present value)
- Verify consistency between related endpoints
- Check that all endpoints follow standard response format

### 3. Error Handling Tests
- Validation errors (422)
- Business logic errors (400, e.g., NO_SOLUTION)
- Error response format consistency
- Guard enforcement (max amounts, max cashflows, etc.)

### 4. Edge Cases Tests
- Boundary conditions (very small/large values)
- Zero values
- Maximum valid values
- Extreme scenarios (100-year terms, 99% rates, etc.)

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_health.py
```

### Run with coverage report
```bash
pytest --cov=app --cov-report=html
```

### Run specific test category
```bash
# Error handling tests
pytest tests/test_error_handling.py

# Integration tests
pytest tests/test_integration.py

# Edge cases
pytest tests/test_edge_cases.py
```

## Test Quality Metrics

- ✅ **All endpoints covered**: Every API endpoint has dedicated tests
- ✅ **Error cases covered**: Validation errors, business logic errors, guards
- ✅ **Edge cases covered**: Boundary conditions, extreme values, zero cases
- ✅ **Integration tests**: Round-trip operations and consistency checks
- ✅ **Response format**: All tests verify standard response structure
- ✅ **Accuracy tests**: Mathematical correctness verified where applicable

## Continuous Integration

Tests run automatically on:
- Every push to `main` branch
- Every pull request
- Via GitHub Actions workflow (`.github/workflows/test.yml`)

## Adding New Tests

When adding new endpoints or features:

1. **Add unit tests** in the appropriate domain test file
2. **Add error handling tests** in `test_error_handling.py` if applicable
3. **Add integration tests** in `test_integration.py` if the endpoint relates to others
4. **Add edge case tests** in `test_edge_cases.py` for boundary conditions

## Test Best Practices

- ✅ Use descriptive test names (`test_mortgage_payment_zero_interest`)
- ✅ Test both success and failure cases
- ✅ Verify response structure, not just status codes
- ✅ Use appropriate assertions (exact values vs. ranges)
- ✅ Test edge cases and boundary conditions
- ✅ Keep tests independent (no shared state)
- ✅ Use fixtures for common setup when appropriate
