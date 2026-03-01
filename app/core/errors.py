"""Exception handlers for unified error responses."""
from fastapi import Request, status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class NoSolutionError(ValueError):
    """Raised when a numerical solver cannot find a solution."""
    def __init__(self, message: str, details: list = None):
        super().__init__(message)
        self.details = details or []


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle FastAPI validation errors and return consistent error format."""
    details: list[str] = []
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
                "details": details,
            },
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTPException and wrap in the standard error envelope.

    This keeps status codes meaningful while ensuring the response shape is:
    {
        "ok": false,
        "error": { "code": "...", "message": "...", "details": [...] }
    }
    """
    # If the detail is already in our envelope format, return as-is.
    if isinstance(exc.detail, dict) and exc.detail.get("ok") is False and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)

    # Map common HTTP status codes to machine-readable error codes.
    status_code_to_error_code = {
        status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
        status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
        status.HTTP_403_FORBIDDEN: "FORBIDDEN",
        status.HTTP_404_NOT_FOUND: "NOT_FOUND",
        status.HTTP_408_REQUEST_TIMEOUT: "TIMEOUT",
        status.HTTP_422_UNPROCESSABLE_ENTITY: "VALIDATION_ERROR",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "INTERNAL_SERVER_ERROR",
    }

    error_code = status_code_to_error_code.get(exc.status_code, "HTTP_ERROR")

    # Derive human-readable message and details from the original detail.
    if isinstance(exc.detail, dict):
        message = (
            exc.detail.get("message")
            or exc.detail.get("detail")
            or str(exc.detail)
        )
        extra_details = exc.detail.get("details")
        if extra_details is None:
            # Put the whole dict into details if there is no dedicated list.
            extra_details = [exc.detail]
    else:
        message = str(exc.detail)
        extra_details = []

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "ok": False,
            "error": {
                "code": error_code,
                "message": message,
                "details": extra_details,
            },
        },
    )
