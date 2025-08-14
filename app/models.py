"""Pydantic models and money helpers for the ATM API."""

from pydantic import BaseModel, Field, field_validator
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Final

_TWO_PLACES: Final[Decimal] = Decimal("0.01")

def to_cents(amount: Decimal) -> int:
    """Convert a Decimal to integer cents with half-up rounding."""
    q = amount.quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)
    return int((q * 100).to_integral_value(rounding=ROUND_HALF_UP))

def cents_to_str(cents: int) -> str:
    """Format integer cents as a two-decimal-place string."""
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}{cents // 100}.{cents % 100:02d}"

class AmountIn(BaseModel):
    """Request body with a strictly positive amount up to 2 decimals."""
    amount: str = Field(..., description="Amount in standard decimal notation, e.g. '100.00'.")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: str) -> str:
        """Ensure amount is a decimal string > 0 with <= 2 fractional digits."""
        try:
            dec = Decimal(v)
        except (InvalidOperation, TypeError):
            raise ValueError("amount must be a decimal number (e.g., '12.34')")
        if dec <= 0:
            raise ValueError("amount must be positive")
        if abs(dec.as_tuple().exponent) > 2:
            raise ValueError("amount must have at most 2 decimal places")
        return v

    def amount_cents(self) -> int:
        """Return the amount as integer cents."""
        return to_cents(Decimal(self.amount))

class BalanceOut(BaseModel):
    """Response model with account number and formatted balance."""
    account_number: str
    balance: str = Field(..., description="Balance as a string with 2 decimal places.")
