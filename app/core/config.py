"""Configuration and constants for the application."""
import os
from datetime import datetime, timezone

# CORS configuration
# Update ALLOWED_ORIGINS when adding new frontends (e.g. another GitHub Pages site).
ALLOWED_ORIGINS = [
    # Local FastAPI / Swagger
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    # Local static client (python -m http.server 3000)
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # GitHub Pages for this project
    "https://mytherapy-coding.github.io",
]

# Metadata for /v1/info endpoint
BUILD_TIMESTAMP = datetime.now(timezone.utc).isoformat()
GIT_SHA = os.getenv("GIT_SHA", "unknown")
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

# Constants for guards
MAX_AMORTIZATION_MONTHS = 600
MAX_XIRR_CASHFLOWS = 1000
MAX_AMOUNT = 1e12  # Maximum absolute monetary amount accepted by the API
SOLVER_TIMEOUT_SECONDS = 5

# Optional scipy import for advanced calculations
try:
    from scipy.optimize import fsolve, root_scalar
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    fsolve = None
    root_scalar = None
