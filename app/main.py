from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
