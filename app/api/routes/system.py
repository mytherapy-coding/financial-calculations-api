"""System routes (health, echo, info)."""
from fastapi import APIRouter
from app.models.common import EchoRequest, EchoResponse
from app.core.config import BUILD_TIMESTAMP, GIT_SHA, ENVIRONMENT

router = APIRouter()


@router.get(
    "/v1/health",
    summary="Health Check",
    description="Check if the API is running and healthy.",
    response_description="Health status",
    tags=["System"],
)
def health():
    """
    Health check endpoint.
    
    Returns basic service information to confirm the API is running.
    """
    return {"ok": True, "service": "finance-api", "version": "v1"}


@router.get(
    "/v1/info",
    summary="Service Information",
    description="Get service metadata including version, environment, build timestamp, and git SHA.",
    response_description="Service metadata",
    tags=["System"],
)
def info():
    """
    Service information endpoint.
    
    Returns metadata useful for debugging:
    - version: API version
    - environment: deployment environment
    - build_timestamp: when the service was built
    - git_sha: git commit SHA (if available)
    """
    return {
        "ok": True,
        "service": "finance-api",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "build_timestamp": BUILD_TIMESTAMP,
        "git_sha": GIT_SHA,
    }


@router.post(
    "/v1/echo",
    response_model=EchoResponse,
    summary="Echo Request",
    description="Echo back the request payload. Useful for testing API connectivity and JSON parsing.",
    response_description="Echoed request payload",
    tags=["System"],
)
def echo(payload: EchoRequest):
    """
    Echo endpoint for testing.
    
    Returns the same payload that was sent, useful for:
    - Testing API connectivity
    - Verifying JSON parsing
    - Debugging request/response flow
    """
    return {"ok": True, "echo": payload}
