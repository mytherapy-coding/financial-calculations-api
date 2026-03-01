"""Bond calculation routes."""
from fastapi import APIRouter, status, HTTPException
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from app.models.bonds import (
    BondYieldRequest,
    BondYieldResponse,
    BondPriceRequest,
    BondPriceResponse,
)
from app.services.bonds import (
    calculate_bond_yield,
    bond_price_at_yield,
)
from app.core.config import SOLVER_TIMEOUT_SECONDS
from app.core.errors import NoSolutionError

router = APIRouter()


@router.post(
    "/v1/bond/yield",
    response_model=BondYieldResponse,
    summary="Calculate Bond Yield to Maturity",
    description="Calculate the yield to maturity for a bond using numerical solver.",
    response_description="Yield to maturity",
    tags=["Bonds"],
)
def calculate_bond_yield_endpoint(payload: BondYieldRequest):
    """
    Calculate the yield to maturity (YTM) for a bond.
    
    Uses numerical methods to solve for the yield that equates the present value
    of all future cash flows to the current bond price.
    
    **Guards:**
    - 5 second timeout for solver
    """
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                calculate_bond_yield,
                payload.face_value,
                payload.coupon_rate,
                payload.years_to_maturity,
                payload.current_price,
                payload.payments_per_year,
            )
            yield_result = future.result(timeout=SOLVER_TIMEOUT_SECONDS)

        return {"ok": True, "yield_to_maturity": round(yield_result, 6)}
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
                    "message": f"Failed to calculate bond yield: {str(e)}",
                    "details": [],
                },
            },
        )


@router.post(
    "/v1/bond/price",
    response_model=BondPriceResponse,
    summary="Calculate Bond Price from Yield",
    description="Calculate the bond price given yield to maturity and coupon information.",
    response_description="Bond price",
    tags=["Bonds"],
)
def calculate_bond_price_endpoint(payload: BondPriceRequest):
    """
    Calculate the price of a bond from its yield to maturity.

    Uses the standard bond pricing formula:
    - Present value of all coupon payments
    - Present value of the face value at maturity
    """
    price = bond_price_at_yield(
        payload.face_value,
        payload.coupon_rate,
        payload.years_to_maturity,
        payload.yield_to_maturity,
        payload.payments_per_year,
    )

    return {"ok": True, "price": round(price, 4)}
