"""Mortgage calculation services (pure business logic)."""
from typing import List
from datetime import date
from app.models.mortgage import AmortizationPayment


def calculate_mortgage_payment(principal: float, annual_rate: float, years: float) -> float:
    """Calculate monthly mortgage payment.
    
    Formula: M = P × [r(1+r)^n] / [(1+r)^n - 1]
    
    Args:
        principal: Loan principal amount
        annual_rate: Annual interest rate as decimal
        years: Loan term in years
        
    Returns:
        Monthly payment rounded to 2 decimal places
    """
    monthly_rate = annual_rate / 12
    num_payments = years * 12
    
    if monthly_rate == 0:
        monthly_payment = principal / num_payments
    else:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
    
    return round(monthly_payment, 2)


def generate_amortization_schedule(
    principal: float, 
    annual_rate: float, 
    years: float, 
    max_months: int
) -> tuple[float, int, List[AmortizationPayment]]:
    """Generate amortization schedule.
    
    Args:
        principal: Loan principal amount
        annual_rate: Annual interest rate as decimal
        years: Loan term in years
        max_months: Maximum number of months to return
        
    Returns:
        Tuple of (monthly_payment, total_payments, schedule)
    """
    monthly_rate = annual_rate / 12
    total_payments = int(years * 12)
    
    if monthly_rate == 0:
        monthly_payment = principal / total_payments
    else:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** total_payments) / ((1 + monthly_rate) ** total_payments - 1)
    
    # Generate schedule (limited by max_months)
    schedule = []
    balance = principal
    months_to_generate = min(total_payments, max_months)
    
    for month in range(1, months_to_generate + 1):
        interest_payment = balance * monthly_rate
        principal_payment = monthly_payment - interest_payment
        balance = balance - principal_payment
        
        if balance < 0.01:
            balance = 0
        
        schedule.append(AmortizationPayment(
            month=month,
            payment=round(monthly_payment, 2),
            principal_payment=round(principal_payment, 2),
            interest_payment=round(interest_payment, 2),
            remaining_balance=round(balance, 2)
        ))
    
    return (round(monthly_payment, 2), total_payments, schedule)


def calculate_mortgage_summary(principal: float, annual_rate: float, years: float) -> dict:
    """Calculate mortgage summary metrics.
    
    Args:
        principal: Loan principal amount
        annual_rate: Annual interest rate as decimal
        years: Loan term in years
        
    Returns:
        Dictionary with monthly_payment, total_paid, total_interest, payoff_months, payoff_date
    """
    monthly_rate = annual_rate / 12
    payoff_months = int(years * 12)

    if monthly_rate == 0:
        monthly_payment = principal / payoff_months
    else:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** payoff_months) / (
            (1 + monthly_rate) ** payoff_months - 1
        )

    total_paid = monthly_payment * payoff_months
    total_interest = total_paid - principal

    # Estimate payoff date
    today = date.today().replace(day=1)
    total_month_index = (today.year * 12 + (today.month - 1)) + (payoff_months - 1)
    payoff_year = total_month_index // 12
    payoff_month = total_month_index % 12 + 1
    payoff_date_str = f"{payoff_year:04d}-{payoff_month:02d}"

    return {
        "monthly_payment": round(monthly_payment, 2),
        "total_paid": round(total_paid, 2),
        "total_interest": round(total_interest, 2),
        "payoff_months": payoff_months,
        "payoff_date": payoff_date_str,
    }


def calculate_mortgage_with_extra_payments(
    principal: float, 
    annual_rate: float, 
    years: float, 
    extra_payment: float
) -> dict:
    """Calculate mortgage payoff with extra monthly payments.
    
    Args:
        principal: Loan principal amount
        annual_rate: Annual interest rate as decimal
        years: Loan term in years
        extra_payment: Extra payment amount per month
        
    Returns:
        Dictionary with all mortgage metrics including savings
    """
    monthly_rate = annual_rate / 12
    original_payoff_months = int(years * 12)

    # Calculate regular monthly payment
    if monthly_rate == 0:
        regular_monthly_payment = principal / original_payoff_months
    else:
        regular_monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** original_payoff_months) / (
            (1 + monthly_rate) ** original_payoff_months - 1
        )

    total_monthly_payment = regular_monthly_payment + extra_payment

    # Calculate original scenario (without extra payments)
    original_total_paid = regular_monthly_payment * original_payoff_months
    original_total_interest = original_total_paid - principal

    # Simulate payments with extra payments to find new payoff
    balance = principal
    new_payoff_months = 0
    new_total_paid = 0.0
    max_months = original_payoff_months * 2  # Safety limit

    while balance > 0.01 and new_payoff_months < max_months:
        new_payoff_months += 1
        interest_payment = balance * monthly_rate
        principal_payment = regular_monthly_payment - interest_payment
        extra_principal = extra_payment

        # Apply extra payment to principal
        total_principal_payment = principal_payment + extra_principal
        balance -= total_principal_payment
        new_total_paid += regular_monthly_payment + extra_payment

    if balance < 0:
        # Adjust for overpayment in last month
        new_total_paid += balance
        balance = 0

    new_total_interest = new_total_paid - principal
    months_saved = original_payoff_months - new_payoff_months
    interest_saved = original_total_interest - new_total_interest

    # Calculate new payoff date
    today = date.today().replace(day=1)
    total_month_index = (today.year * 12 + (today.month - 1)) + (new_payoff_months - 1)
    payoff_year = total_month_index // 12
    payoff_month = total_month_index % 12 + 1
    new_payoff_date = f"{payoff_year:04d}-{payoff_month:02d}"

    return {
        "regular_monthly_payment": round(regular_monthly_payment, 2),
        "total_monthly_payment": round(total_monthly_payment, 2),
        "original_payoff_months": original_payoff_months,
        "new_payoff_months": new_payoff_months,
        "months_saved": months_saved,
        "original_total_interest": round(original_total_interest, 2),
        "new_total_interest": round(new_total_interest, 2),
        "interest_saved": round(interest_saved, 2),
        "new_payoff_date": new_payoff_date,
    }
