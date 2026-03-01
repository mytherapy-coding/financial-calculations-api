"""Common request/response models."""
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Error detail model."""
    code: str
    message: str
    details: list = []


class ErrorResponse(BaseModel):
    """Standard error response model."""
    ok: bool = False
    error: ErrorDetail


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
