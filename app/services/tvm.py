"""Time Value of Money calculation services (pure business logic)."""


def calculate_future_value(principal: float, annual_rate: float, years: float, compounds_per_year: int) -> float:
    """Calculate future value using compound interest.
    
    Formula: FV = P * (1 + r/n)^(n*t)
    
    Args:
        principal: Initial principal amount
        annual_rate: Annual interest rate as decimal
        years: Number of years
        compounds_per_year: Number of compounding periods per year
        
    Returns:
        Future value rounded to 2 decimal places
    """
    rate_per_period = annual_rate / compounds_per_year
    total_periods = compounds_per_year * years
    future_value = principal * (1 + rate_per_period) ** total_periods
    return round(future_value, 2)


def calculate_present_value(future_value: float, annual_rate: float, years: float, compounds_per_year: int) -> float:
    """Calculate present value from future value.
    
    Formula: PV = FV / (1 + r/n)^(n*t)
    
    Args:
        future_value: Future value amount
        annual_rate: Annual discount rate as decimal
        years: Number of years
        compounds_per_year: Number of compounding periods per year
        
    Returns:
        Present value rounded to 2 decimal places
    """
    if annual_rate == 0 or compounds_per_year == 0:
        return round(future_value, 2)
    
    rate_per_period = annual_rate / compounds_per_year
    total_periods = compounds_per_year * years
    present_value = future_value / (1 + rate_per_period) ** total_periods
    return round(present_value, 2)


def calculate_annuity_payment(present_value: float, annual_rate: float, years: float, payments_per_year: int) -> float:
    """Calculate level annuity payment.
    
    Formula: Pmt = PV × [r(1+r)^n] / [(1+r)^n - 1]
    
    Args:
        present_value: Present value of the annuity
        annual_rate: Annual interest rate as decimal
        years: Number of years
        payments_per_year: Number of payments per year
        
    Returns:
        Payment amount rounded to 2 decimal places
    """
    periodic_rate = annual_rate / payments_per_year
    total_payments = int(years * payments_per_year)

    if periodic_rate == 0:
        payment = present_value / total_payments
    else:
        payment = present_value * (
            periodic_rate * (1 + periodic_rate) ** total_payments
        ) / ((1 + periodic_rate) ** total_payments - 1)

    return round(payment, 2)
