"""XIRR calculation routes."""
from fastapi import APIRouter, status, HTTPException
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from app.models.xirr import (
    XIRRRequest,
    XIRRResponse,
    XIRRExplainResponse,
)
from app.services.xirr import (
    calculate_xirr,
    calculate_xirr_with_meta,
)
from app.core.config import MAX_XIRR_CASHFLOWS, SOLVER_TIMEOUT_SECONDS
from app.core.errors import NoSolutionError

router = APIRouter()


@router.post(
    "/v1/xirr",
    response_model=XIRRResponse,
    summary="Calculate XIRR",
    description="Calculate Extended Internal Rate of Return for irregular cash flows with dates.",
    response_description="XIRR value",
    tags=["Time Value of Money"],
)
def calculate_xirr_endpoint(payload: XIRRRequest):
    """
    Calculate the Extended Internal Rate of Return (XIRR) for irregular cash flows.
    
    XIRR is used when cash flows occur at irregular intervals. It calculates
    the annualized return rate that makes the Net Present Value (NPV) equal to zero.
    
    **Guards:**
    - Maximum 1000 cash flows
    - 5 second timeout for solver
    """
    # Guard: Check cashflow count
    if len(payload.cashflows) > MAX_XIRR_CASHFLOWS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "ok": False,
                "error": {
                    "code": "TOO_MANY_CASHFLOWS",
                    "message": f"Maximum {MAX_XIRR_CASHFLOWS} cash flows allowed",
                    "details": [f"Received {len(payload.cashflows)} cash flows"],
                },
            },
        )

    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                calculate_xirr,
                payload.cashflows,
                payload.initial_guess,
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
                    "details": [],
                },
            },
        )
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "ok": False,
                "error": {
                    "code": "SOLVER_ERROR",
                    "message": f"Failed to calculate XIRR: {str(e)}",
                    "details": [],
                },
            },
        )


@router.post(
    "/v1/xirr/explain",
    response_model=XIRRExplainResponse,
    summary="Calculate XIRR with explanation",
    description=(
        "Calculate XIRR and return additional metadata such as solver type, "
        "iteration count, and numerical warnings."
    ),
    response_description="XIRR explanation",
    tags=["Time Value of Money"],
)
def explain_xirr_endpoint(payload: XIRRRequest):
    """
    XIRR explanation endpoint.

    Returns:
    - `xirr`: computed rate
    - `iterations`: number of iterations used (for the bisection fallback)
    - `solver_type`: which solver was used (`scipy-brentq`, `scipy-fsolve`, or `bisection`)
    - `warnings`: list of numerical warnings, e.g. potential multiple IRRs
    """
    if len(payload.cashflows) > MAX_XIRR_CASHFLOWS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "ok": False,
                "error": {
                    "code": "TOO_MANY_CASHFLOWS",
                    "message": f"Maximum {MAX_XIRR_CASHFLOWS} cash flows allowed",
                    "details": [f"Received {len(payload.cashflows)} cash flows"],
                },
            },
        )

    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                calculate_xirr_with_meta,
                payload.cashflows,
                payload.initial_guess,
            )
            rate, meta = future.result(timeout=SOLVER_TIMEOUT_SECONDS)

        return {
            "ok": True,
            "xirr": round(rate, 6),
            "iterations": int(meta.get("iterations") or 0),
            "solver_type": meta.get("solver_type") or "",
            "warnings": meta.get("warnings") or [],
        }
    except FutureTimeoutError:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail={
                "ok": False,
                "error": {
                    "code": "SOLVER_TIMEOUT",
                    "message": f"Solver exceeded timeout of {SOLVER_TIMEOUT_SECONDS} seconds",
                    "details": [],
                },
            },
        )
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "ok": False,
                "error": {
                    "code": "SOLVER_ERROR",
                    "message": f"Failed to calculate XIRR: {str(e)}",
                    "details": [],
                },
            },
        )
