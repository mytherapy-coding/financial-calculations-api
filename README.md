# financial-calculations-api

Stateless JSON API for financial calculations built with FastAPI.

> 📖 **Architecture Documentation**: See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed information about the project structure and design patterns.

## Quickstart

### Health Check
```bash
curl https://YOUR-RENDER-URL.onrender.com/v1/health
```

**Response:**
```json
{
  "ok": true,
  "service": "finance-api",
  "version": "v1"
}
```

### Echo Endpoint
```bash
curl -X POST https://YOUR-RENDER-URL.onrender.com/v1/echo \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, World!",
    "number": 42
  }'
```

**Response:**
```json
{
  "ok": true,
  "echo": {
    "message": "Hello, World!",
    "number": 42
  }
}
```

### Calculate Future Value (Compound Interest)
```bash
curl -X POST https://YOUR-RENDER-URL.onrender.com/v1/tvm/future-value \
  -H "Content-Type: application/json" \
  -d '{
    "principal": 10000,
    "annual_rate": 0.07,
    "years": 10,
    "compounds_per_year": 12
  }'
```

**Response:**
```json
{
  "ok": true,
  "future_value": 19671.51
}
```

**Note:** Replace `YOUR-RENDER-URL.onrender.com` with your actual Render deployment URL.

### Interactive API Documentation

Visit `/docs` in your browser for interactive Swagger UI documentation:
- Local: http://127.0.0.1:8000/docs
- Production: https://YOUR-RENDER-URL.onrender.com/docs

## Client Documentation

This section provides comprehensive documentation for developers using this API.

### Base URL

- **Production**: `https://YOUR-RENDER-URL.onrender.com`
- **Local Development**: `http://127.0.0.1:8000`

All endpoints are prefixed with `/v1/`.

### Authentication

This API does not require authentication. All endpoints are publicly accessible.

### Request Format

All requests should use:
- **Content-Type**: `application/json`
- **Method**: `POST` (for calculation endpoints) or `GET` (for info endpoints)

### Response Format

All successful responses follow this format:
```json
{
  "ok": true,
  "result_field": value
}
```

All error responses follow this format:
```json
{
  "ok": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": ["Additional error details"]
  }
}
```

### HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid input or business logic error (e.g., NO_SOLUTION)
- `408 Request Timeout`: Solver exceeded timeout (5 seconds)
- `422 Unprocessable Entity`: Validation error (invalid field types, missing required fields)
- `500 Internal Server Error`: Server error

### Rate Limits

Currently, there are no rate limits. However, please use the API responsibly.

### Error Handling

Always check the `ok` field in the response:

```javascript
const response = await fetch('https://api.example.com/v1/tvm/future-value', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    principal: 10000,
    annual_rate: 0.07,
    years: 10,
    compounds_per_year: 12
  })
});

const data = await response.json();

if (data.ok) {
  console.log('Future value:', data.future_value);
} else {
  console.error('Error:', data.error.message);
  console.error('Details:', data.error.details);
}
```

### Common Error Codes

- `VALIDATION_ERROR`: Request validation failed (missing fields, invalid types, out of range)
- `NO_SOLUTION`: Numerical solver could not find a solution (bond yield, XIRR)
- `SOLVER_TIMEOUT`: Calculation exceeded 5-second timeout
- `TOO_MANY_CASHFLOWS`: XIRR request exceeds 1000 cashflows limit
- `TOO_MANY_MONTHS`: Amortization schedule exceeds 600 months limit

### API Endpoints Reference

#### 1. Health Check
**GET** `/v1/health`

Check if the API is running.

**Response:**
```json
{
  "ok": true,
  "service": "finance-api",
  "version": "v1"
}
```

#### 2. Service Info
**GET** `/v1/info`

Get service metadata (version, environment, build timestamp).

**Response:**
```json
{
  "ok": true,
  "service": "finance-api",
  "version": "1.0.0",
  "environment": "production",
  "build_timestamp": "2024-01-01T00:00:00",
  "git_sha": "abc123"
}
```

#### 3. Echo
**POST** `/v1/echo`

Echo back the request payload (useful for testing).

**Request:**
```json
{
  "message": "Hello, World!",
  "number": 42
}
```

**Response:**
```json
{
  "ok": true,
  "echo": {
    "message": "Hello, World!",
    "number": 42
  }
}
```

#### 4. Future Value (Compound Interest)
**POST** `/v1/tvm/future-value`

Calculate the future value of an investment using compound interest.

**Request:**
```json
{
  "principal": 10000,
  "annual_rate": 0.07,
  "years": 10,
  "compounds_per_year": 12
}
```

**Fields:**
- `principal` (float, required): Initial investment amount (≥ 0, ≤ 1e12)
- `annual_rate` (float, required): Annual interest rate as decimal (0.07 = 7%, range: 0-1)
- `years` (float, required): Number of years (> 0)
- `compounds_per_year` (int, required): Compounding frequency (1=annual, 12=monthly, 365=daily)

**Response:**
```json
{
  "ok": true,
  "future_value": 19671.51
}
```

#### 5. Present Value
**POST** `/v1/tvm/present-value`

Calculate the present value of a future amount.

**Request:**
```json
{
  "future_value": 10000,
  "annual_rate": 0.07,
  "years": 10,
  "compounds_per_year": 12
}
```

**Response:**
```json
{
  "ok": true,
  "present_value": 5083.49
}
```

#### 6. Annuity Payment
**POST** `/v1/tvm/annuity-payment`

Calculate the level payment amount for a fixed-term annuity.

**Request:**
```json
{
  "present_value": 10000,
  "annual_rate": 0.05,
  "years": 5,
  "payments_per_year": 12
}
```

**Response:**
```json
{
  "ok": true,
  "payment": 188.71
}
```

#### 7. Mortgage Payment
**POST** `/v1/mortgage/payment`

Calculate monthly payment for a fixed-rate mortgage.

**Request:**
```json
{
  "principal": 300000,
  "annual_rate": 0.04,
  "years": 30
}
```

**Response:**
```json
{
  "ok": true,
  "monthly_payment": 1432.25
}
```

#### 8. Amortization Schedule
**POST** `/v1/mortgage/amortization-schedule`

Generate detailed amortization schedule (limited to 600 months).

**Request:**
```json
{
  "principal": 300000,
  "annual_rate": 0.04,
  "years": 30,
  "max_months": 360
}
```

**Response:**
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

#### 9. Mortgage Summary
**POST** `/v1/mortgage/summary`

Get key mortgage metrics (payment, total paid, interest, payoff date).

**Request:**
```json
{
  "principal": 300000,
  "annual_rate": 0.04,
  "years": 30
}
```

**Response:**
```json
{
  "ok": true,
  "monthly_payment": 1432.25,
  "total_paid": 515610.0,
  "total_interest": 215610.0,
  "payoff_months": 360,
  "payoff_date": "2054-01"
}
```

#### 10. Mortgage with Extra Payments
**POST** `/v1/mortgage/with-extra-payments`

Calculate mortgage impact of making extra principal payments.

**Request:**
```json
{
  "principal": 300000,
  "annual_rate": 0.04,
  "years": 30,
  "extra_monthly_payment": 200
}
```

**Response:**
```json
{
  "ok": true,
  "regular_monthly_payment": 1432.25,
  "total_monthly_payment": 1632.25,
  "original_payoff_months": 360,
  "new_payoff_months": 280,
  "months_saved": 80,
  "original_total_interest": 215610.0,
  "new_total_interest": 165432.0,
  "interest_saved": 50178.0,
  "new_payoff_date": "2046-05"
}
```

#### 11. Bond Yield to Maturity
**POST** `/v1/bond/yield`

Calculate yield to maturity for a bond.

**Request:**
```json
{
  "face_value": 1000,
  "coupon_rate": 0.05,
  "years_to_maturity": 10,
  "current_price": 950,
  "payments_per_year": 2
}
```

**Response:**
```json
{
  "ok": true,
  "yield_to_maturity": 0.055
}
```

#### 12. Bond Price from Yield
**POST** `/v1/bond/price`

Calculate bond price given yield to maturity.

**Request:**
```json
{
  "face_value": 1000,
  "coupon_rate": 0.05,
  "years_to_maturity": 10,
  "yield_to_maturity": 0.055,
  "payments_per_year": 2
}
```

**Response:**
```json
{
  "ok": true,
  "price": 980.50
}
```

#### 13. XIRR (Extended Internal Rate of Return)
**POST** `/v1/xirr`

Calculate XIRR for irregular cash flows with dates.

**Request:**
```json
{
  "cashflows": [
    {"amount": -10000, "date": "2024-01-01"},
    {"amount": 2000, "date": "2024-06-30"},
    {"amount": 3000, "date": "2024-12-31"},
    {"amount": 5000, "date": "2025-12-31"}
  ],
  "initial_guess": 0.1
}
```

**Response:**
```json
{
  "ok": true,
  "xirr": 0.15
}
```

#### 14. XIRR Explain
**POST** `/v1/xirr/explain`

Calculate XIRR with detailed solver metadata.

**Request:** Same as `/v1/xirr`

**Response:**
```json
{
  "ok": true,
  "xirr": 0.15,
  "iterations": 25,
  "solver_type": "scipy-brentq",
  "warnings": []
}
```

### Code Examples

#### JavaScript/TypeScript

```javascript
const API_BASE = 'https://YOUR-RENDER-URL.onrender.com';

async function calculateFutureValue(principal, rate, years) {
  const response = await fetch(`${API_BASE}/v1/tvm/future-value`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      principal,
      annual_rate: rate,
      years,
      compounds_per_year: 12
    })
  });
  
  const data = await response.json();
  
  if (!data.ok) {
    throw new Error(data.error.message);
  }
  
  return data.future_value;
}

// Usage
calculateFutureValue(10000, 0.07, 10)
  .then(fv => console.log('Future value:', fv))
  .catch(err => console.error('Error:', err));
```

#### Python

```python
import requests

API_BASE = 'https://YOUR-RENDER-URL.onrender.com'

def calculate_future_value(principal, rate, years):
    response = requests.post(
        f'{API_BASE}/v1/tvm/future-value',
        json={
            'principal': principal,
            'annual_rate': rate,
            'years': years,
            'compounds_per_year': 12
        }
    )
    
    data = response.json()
    
    if not data['ok']:
        raise Exception(data['error']['message'])
    
    return data['future_value']

# Usage
try:
    fv = calculate_future_value(10000, 0.07, 10)
    print(f'Future value: {fv}')
except Exception as e:
    print(f'Error: {e}')
```

#### cURL

```bash
curl -X POST https://YOUR-RENDER-URL.onrender.com/v1/tvm/future-value \
  -H "Content-Type: application/json" \
  -d '{
    "principal": 10000,
    "annual_rate": 0.07,
    "years": 10,
    "compounds_per_year": 12
  }'
```

### Important Notes

1. **Rate Format**: All rates are decimals (0.07 = 7%, not 7)
2. **Amount Limits**: Maximum amount is 1e12 (1 trillion)
3. **Date Format**: Use `YYYY-MM-DD` format for dates
4. **Precision**: Results are rounded to 2-6 decimal places depending on the endpoint
5. **Timeouts**: Solver endpoints (bond yield, XIRR) have a 5-second timeout
6. **CORS**: API supports CORS for web applications

### Best Practices

1. **Always check `ok` field** before using results
2. **Handle errors gracefully** - display user-friendly messages
3. **Validate inputs client-side** before sending requests
4. **Cache results** when appropriate to reduce API calls
5. **Use appropriate precision** - don't display more decimals than meaningful
6. **Respect rate limits** (if implemented in the future)

## Setup

### 1. Create virtual environment
```bash
python -m venv .venv
```

### 2. Activate virtual environment
```bash
# macOS/Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## Run Locally

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The server will start at `http://127.0.0.1:8000`

## API Endpoints

### Health Check
- **GET** `/v1/health`
- **Description:** Check if the API service is running and healthy
- **Response:** `{"ok": true, "service": "finance-api", "version": "v1"}`

### Echo
- **POST** `/v1/echo`
- **Description:** Echo back the request payload. Useful for testing API connectivity.
- **Request body:**
  ```json
  {
    "message": "string",
    "number": 123  // optional
  }
  ```
- **Response:** `{"ok": true, "echo": {...}}`

### Future Value (Compound Interest)
- **POST** `/v1/tvm/future-value`
- **Description:** Calculate the future value of an investment using compound interest.
- **Formula:** FV = P × (1 + r/n)^(n×t)
- **Request body:**
  ```json
  {
    "principal": 10000,
    "annual_rate": 0.07,  // 7% as decimal (not 7)
    "years": 10,
    "compounds_per_year": 12  // monthly
  }
  ```
- **Response:** `{"ok": true, "future_value": 19671.51}`
- **Note:** `annual_rate` must be a decimal (0.07 for 7%, not 7)

## Testing

The project has **comprehensive test coverage** with **91+ test functions** across 11 test files:

- ✅ **All endpoints covered**: Every API endpoint has dedicated tests
- ✅ **Error handling**: Validation errors, business logic errors, guards
- ✅ **Edge cases**: Boundary conditions, extreme values, zero cases
- ✅ **Integration tests**: Round-trip operations and consistency checks
- ✅ **Response format**: All tests verify standard response structure

See [TEST_COVERAGE.md](TEST_COVERAGE.md) for detailed coverage documentation.

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_health.py
```

### Interactive API Documentation (Swagger UI)
Open in your browser: http://127.0.0.1:8000/docs

### Manual Testing Examples

**Health Check:**
```bash
curl http://127.0.0.1:8000/v1/health
```

**Echo Endpoint:**
```bash
curl -X POST http://127.0.0.1:8000/v1/echo \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "number": 42}'
```

## Deploy to Render

### Prerequisites
- GitHub repository (this project should be pushed to GitHub)
- Render account (sign up at https://render.com/)

### Deployment Steps

1. **Push to GitHub** (if not already done)
   ```bash
   git push origin main
   ```

2. **Create Render Web Service**
   - Go to https://dashboard.render.com/
   - Click "New +" → "Web Service"
   - Connect your GitHub account and select the repository
   - Configure the service:
     - **Name**: `finance-api` (or your preferred name)
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - **Plan**: Free tier is available

3. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your app
   - Wait for deployment to complete (usually 2-3 minutes)

4. **Verify Deployment**
   - Health check: `https://<your-service>.onrender.com/v1/health`
   - API docs: `https://<your-service>.onrender.com/docs`

### Troubleshooting

- **Service crashes**: Check Render logs in the dashboard
- **404 errors**: Verify start command points to `app.main:app`
- **Port errors**: Must use `$PORT` environment variable (don't hardcode port 8000)
- **Build fails**: Check that `requirements.txt` is correct and all dependencies are listed

### Using render.yaml (Optional)

The project includes a `render.yaml` file for automatic configuration. When creating a new service, Render will detect and use this file automatically.

## Web Client

A simple web client is included in the `docs/` directory that can call the API from a browser.

### Setup Client

1. **Configure API URL** in `docs/app.js`:
   ```javascript
   // DEFAULT_PRODUCTION_URL is set to your Render deployment by default:
   const DEFAULT_API_BASE = "https://YOUR-RENDER-URL.onrender.com";
   ```

2. **Test locally**:
- Open `docs/index.html` in your browser, or serve it via:
  ```bash
  cd docs
  python -m http.server 3000
  # Then open http://localhost:3000
  ```
   - Click "Check Health" or "Send Echo" buttons
   - Make sure your Render API is deployed and CORS is configured

### Deploy to GitHub Pages

1. **Push client files to GitHub** (already in the repo)

2. **Enable GitHub Pages**:
   - Go to your repository on GitHub
   - Settings → Pages
   - Source: Select "Deploy from a branch"
   - Branch: `main`
   - Folder: `/docs`
   - Click "Save"

3. **Update CORS in Backend**:
   - The backend already includes CORS middleware
   - Make sure your GitHub Pages URL is in the `ALLOWED_ORIGINS` list in `app/core/config.py`
   - Example: `"https://mytherapy-coding.github.io"`

4. **Verify Deployment**:
   - Your client will be available at: `https://<username>.github.io/<repo-name>/`
   - Or if using a custom domain: `https://yourdomain.com`

### Overriding API base (for local dev or forks)

The client supports overriding the API base via a query parameter and remembers it in `localStorage`:

```text
https://<username>.github.io/<repo-name>/?api=http://127.0.0.1:8000
```

This is useful when:
- You run the API locally (FastAPI on `http://127.0.0.1:8000`)
- You fork the repo and deploy your own backend

Implementation outline in `docs/app.js`:

```javascript
const DEFAULT_API_BASE = "https://YOUR-RENDER-URL.onrender.com";

function resolveApiBase() {
  const params = new URLSearchParams(window.location.search);

  // 1) Query param ?api=
  const apiFromQuery = params.get("api");
  if (apiFromQuery) {
    localStorage.setItem("api_base", apiFromQuery);
    return apiFromQuery;
  }

  // 2) localStorage fallback
  const apiFromStorage = localStorage.getItem("api_base");
  if (apiFromStorage) {
    return apiFromStorage;
  }

  // 3) Default production URL
  return DEFAULT_API_BASE;
}

const API_BASE = resolveApiBase();
```

### Client Features

- **Health Check**: Tests the `/v1/health` endpoint
- **Echo**: Sends a POST request to `/v1/echo` with sample data
- **JSON Display**: Shows formatted JSON responses

### CORS Configuration

The backend includes CORS middleware with a **strict allowlist** of frontends that are allowed to call the API.

By default, the following origins are allowed:
- Local development:
  - `http://localhost:8000`
  - `http://127.0.0.1:8000`
  - `http://localhost:3000`
  - `http://127.0.0.1:3000`
- GitHub Pages for this project:
  - `https://mytherapy-coding.github.io`

If you add another frontend (for example, a different GitHub Pages site or a custom domain), update `ALLOWED_ORIGINS` in `app/core/config.py`:

```python
ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # Add your GitHub Pages or custom domains here:
    "https://YOURNAME.github.io",
]
```

> Note: `allow_origins` does **not** support wildcards like `"https://*.github.io"` in the way you might expect.  
> If you really want to allow any `username.github.io` (but not other domains), you can use `allow_origin_regex`, for example:
>
> ```python
> app.add_middleware(
>     CORSMiddleware,
>     allow_origin_regex=r"https://[a-zA-Z0-9-]+\.github\.io",
>     allow_methods=["*"],
>     allow_headers=["*"],
> )
> ```
>
> For most cases, a strict `ALLOWED_ORIGINS` list is safer and easier to reason about.

## Project Structure

```
financial-calculations-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── core/                # Core configuration and error handling
│   │   ├── config.py        # Constants, CORS, metadata
│   │   └── errors.py        # Exception handlers
│   ├── models/              # Pydantic request/response models
│   │   ├── common.py        # Common models (Error, Echo)
│   │   ├── tvm.py           # Time Value of Money models
│   │   ├── mortgage.py      # Mortgage calculation models
│   │   ├── bonds.py         # Bond calculation models
│   │   └── xirr.py          # XIRR calculation models
│   ├── services/            # Pure business logic (no FastAPI dependencies)
│   │   ├── tvm.py           # TVM calculation services
│   │   ├── mortgage.py      # Mortgage calculation services
│   │   ├── bonds.py         # Bond calculation services
│   │   └── xirr.py          # XIRR calculation services
│   └── api/
│       └── routes/           # FastAPI route handlers
│           ├── system.py    # Health, echo, info endpoints
│           ├── tvm.py        # TVM endpoints
│           ├── mortgage.py   # Mortgage endpoints
│           ├── bonds.py      # Bond endpoints
│           └── xirr.py       # XIRR endpoints
├── docs/                    # Web client (served by GitHub Pages)
│   ├── index.html
│   ├── app.js
│   └── style.css
├── tests/                   # Pytest test suite (91+ tests)
│   ├── test_health.py       # Health check tests
│   ├── test_echo.py         # Echo endpoint tests
│   ├── test_info.py         # Info endpoint tests
│   ├── test_future_value.py # Future value tests
│   ├── test_tvm.py          # TVM (present value, annuity) tests
│   ├── test_mortgage.py     # Mortgage calculation tests
│   ├── test_bond.py         # Bond calculation tests
│   ├── test_xirr.py         # XIRR calculation tests
│   ├── test_error_handling.py # Error handling and validation tests
│   ├── test_integration.py  # Integration and round-trip tests
│   └── test_edge_cases.py   # Edge cases and boundary tests
├── .github/workflows/       # CI workflow
├── CONCEPTS.md
├── DEPLOY.md
├── LICENSE
├── PHASE1_CHECKLIST.md
├── README.md
├── render.yaml
└── requirements.txt
```

### Architecture

The project follows a **modular architecture** with clear separation of concerns:

- **`app/main.py`**: FastAPI application initialization, middleware, exception handlers, and router registration (34 lines)
- **`app/core/`**: Shared configuration and error handling
- **`app/models/`**: Pydantic models for request/response validation
- **`app/services/`**: Pure business logic functions (no FastAPI dependencies, easily testable)
- **`app/api/routes/`**: FastAPI route handlers that call services and return HTTP responses

This architecture provides:
- **Separation of concerns**: Routes → Services → Models
- **Testability**: Services can be tested independently without FastAPI
- **Scalability**: Easy to add new endpoints and domains
- **Maintainability**: Changes are isolated to specific modules
