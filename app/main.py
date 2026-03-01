"""Main FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import ALLOWED_ORIGINS
from app.core.errors import validation_exception_handler, http_exception_handler
from app.api.routes import system, tvm, mortgage, bonds, xirr

app = FastAPI(
    title="Finance Calculations API",
    version="1.0.0",
    description="Stateless JSON API for financial calculations"
)

# CORS Middleware - allow only known frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
from fastapi import HTTPException

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

# Include routers
app.include_router(system.router)
app.include_router(tvm.router)
app.include_router(mortgage.router)
app.include_router(bonds.router)
app.include_router(xirr.router)
