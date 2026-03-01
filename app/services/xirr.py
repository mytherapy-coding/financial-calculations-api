"""XIRR calculation services (pure business logic)."""
from datetime import datetime
from typing import List, Tuple, Dict
from app.core.config import SCIPY_AVAILABLE, fsolve, root_scalar
from app.core.errors import NoSolutionError
from app.models.xirr import CashFlow


def calculate_xirr(cashflows: List[CashFlow], initial_guess: float) -> float:
    """Calculate XIRR using numerical solver.
    
    Returns only the XIRR value.
    For more details, use `calculate_xirr_with_meta`.
    
    Args:
        cashflows: List of cash flows with dates
        initial_guess: Initial guess for IRR
        
    Returns:
        XIRR as decimal
        
    Raises:
        NoSolutionError: If no solution can be found
    """
    rate, _meta = calculate_xirr_with_meta(cashflows, initial_guess)
    return rate


def calculate_xirr_with_meta(cashflows: List[CashFlow], initial_guess: float) -> Tuple[float, Dict]:
    """Calculate XIRR and return (rate, meta) for explanation purposes.
    
    Args:
        cashflows: List of cash flows with dates
        initial_guess: Initial guess for IRR
        
    Returns:
        Tuple of (rate, meta_dict) where meta contains solver info and warnings
        
    Raises:
        NoSolutionError: If no solution can be found
    """
    # Parse dates and calculate days from first date
    dates = [datetime.strptime(cf.date, "%Y-%m-%d") for cf in cashflows]
    first_date = dates[0]
    days_from_first = [(d - first_date).days for d in dates]
    
    def npv(rate):
        """Calculate Net Present Value at given rate."""
        total = 0
        for i, cf in enumerate(cashflows):
            years = days_from_first[i] / 365.0
            total += cf.amount / ((1 + rate) ** years)
        return total
    
    meta = {
        "iterations": 0,
        "solver_type": "",
        "warnings": [],
    }

    # Detect potential multiple sign changes (multiple possible IRRs).
    signs = []
    test_rates = [-0.9, -0.5, 0.0, 0.1, 0.5, 1.0, 2.0]
    for r in test_rates:
        try:
            val = npv(r)
            signs.append(1 if val > 0 else -1 if val < 0 else 0)
        except Exception:
            continue
    non_zero_signs = [s for s in signs if s != 0]
    if len(non_zero_signs) >= 2 and any(
        non_zero_signs[i] != non_zero_signs[i - 1] for i in range(1, len(non_zero_signs))
    ):
        meta["warnings"].append(
            "Multiple sign changes in NPV over sample rates → multiple possible IRRs may exist."
        )

    # Default bracket for XIRR search
    low, high = -0.99, 10.0

    # Adjust bounds if initial guess suggests different range
    if 0 < initial_guess < 1:
        low, high = -0.5, 2.0

    # Check for sign change before attempting a root find.
    pv_low = npv(low)
    pv_high = npv(high)

    if abs(pv_low) < 1e-9:
        return low, meta
    if abs(pv_high) < 1e-9:
        return high, meta

    if pv_low * pv_high > 0:
        # No sign change within bracket → no solution in this range.
        raise NoSolutionError(
            "No XIRR solution in the searched range for the given cashflows.",
            details=[f"npv(low={low})={pv_low}", f"npv(high={high})={pv_high}"]
        )

    # Use scipy if available (more accurate)
    if SCIPY_AVAILABLE:
        try:
            result = root_scalar(npv, bracket=[low, high], method="brentq", x0=initial_guess)
            meta["solver_type"] = "scipy-brentq"
            return result.root, meta
        except ValueError:
            # Fallback to fsolve
            result = fsolve(npv, initial_guess)
            meta["solver_type"] = "scipy-fsolve"
            return float(result[0]), meta
    else:
        # Fallback: Simple bisection method (no scipy required)
        tolerance = 1e-6
        max_iterations = 100

        meta["solver_type"] = "bisection"

        for i in range(max_iterations):
            mid = (low + high) / 2
            npv_value = npv(mid)

            if abs(npv_value) < tolerance:
                meta["iterations"] = i + 1
                return mid, meta

            if npv_value > 0:
                low = mid
            else:
                high = mid

        # No convergence within max_iterations: treat as no solution
        raise NoSolutionError(
            "No XIRR solution found within iteration limit.",
            details=[]
        )
