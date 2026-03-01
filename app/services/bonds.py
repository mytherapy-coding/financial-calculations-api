"""Bond calculation services (pure business logic)."""
from app.core.config import SCIPY_AVAILABLE, fsolve, root_scalar
from app.core.errors import NoSolutionError


def bond_price_at_yield(
    face_value: float,
    coupon_rate: float,
    years_to_maturity: float,
    yield_to_maturity: float,
    payments_per_year: int
) -> float:
    """Calculate bond price at a given yield.
    
    Args:
        face_value: Face value of the bond
        coupon_rate: Annual coupon rate as decimal
        years_to_maturity: Years to maturity
        yield_to_maturity: Yield to maturity as decimal
        payments_per_year: Number of coupon payments per year
        
    Returns:
        Bond price
    """
    coupon_payment = (face_value * coupon_rate) / payments_per_year
    total_payments = int(years_to_maturity * payments_per_year)

    pv_coupons = 0.0
    for i in range(1, total_payments + 1):
        pv_coupons += coupon_payment / ((1 + yield_to_maturity / payments_per_year) ** i)
    pv_face = face_value / ((1 + yield_to_maturity / payments_per_year) ** total_payments)
    return pv_coupons + pv_face


def calculate_bond_yield(
    face_value: float,
    coupon_rate: float,
    years_to_maturity: float,
    current_price: float,
    payments_per_year: int
) -> float:
    """Calculate bond yield to maturity using numerical solver.
    
    Args:
        face_value: Face value of the bond
        coupon_rate: Annual coupon rate as decimal
        years_to_maturity: Years to maturity
        current_price: Current market price
        payments_per_year: Number of coupon payments per year
        
    Returns:
        Yield to maturity as decimal
        
    Raises:
        NoSolutionError: If no solution can be found in the search range
    """
    coupon_payment = (face_value * coupon_rate) / payments_per_year
    total_payments = int(years_to_maturity * payments_per_year)

    def bond_present_value(yield_rate: float) -> float:
        """Present value minus current price (root at PV - price = 0)."""
        return bond_price_at_yield(face_value, coupon_rate, years_to_maturity, yield_rate, payments_per_year) - current_price
    
    # Common bracket for yield search
    low, high = 0.0, 1.0

    # Check for sign change before attempting a root find.
    pv_low = bond_present_value(low)
    pv_high = bond_present_value(high)

    if abs(pv_low) < 1e-9:
        return low
    if abs(pv_high) < 1e-9:
        return high

    # If there is no sign change, there is no solution in [low, high].
    if pv_low * pv_high > 0:
        raise NoSolutionError(
            "No bond yield solution in [0, 1] for the given inputs.",
            details=[f"pv(low=0.0)={pv_low}", f"pv(high=1.0)={pv_high}"]
        )

    # Use scipy if available (more accurate)
    if SCIPY_AVAILABLE:
        try:
            result = root_scalar(bond_present_value, bracket=[low, high], method="brentq")
            return result.root
        except ValueError:
            # Fallback to fsolve
            result = fsolve(bond_present_value, 0.05)
            return float(result[0])
    else:
        # Fallback: Simple bisection method (no scipy required)
        tolerance = 1e-6
        max_iterations = 100
        
        for _ in range(max_iterations):
            mid = (low + high) / 2
            pv = bond_present_value(mid)
            
            if abs(pv) < tolerance:
                return mid
            
            if pv > 0:
                low = mid
            else:
                high = mid
        
        # Return best guess if convergence not reached
        return (low + high) / 2
