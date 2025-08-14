"""Pydantic models and money helpers for the ATM API."""

from pydantic import BaseModel, Field, field_validator
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Final
from .constants import (
    DESC_AMOUNT,
    DESC_BALANCE,
    ERR_AMOUNT_DECIMAL,
    ERR_AMOUNT_POSITIVE,
    ERR_AMOUNT_DECIMALS,
)

_TWO_PLACES: Final[Decimal] = Decimal("0.01")
# Named constants to avoid magic numbers
_CENTS_PER_UNIT: Final[int] = 100
_MAX_DECIMAL_PLACES: Final[int] = 2

def to_cents(amount: Decimal) -> int:
    """Convert a Decimal to integer cents with half-up rounding."""
    q = amount.quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)
    return int((q * _CENTS_PER_UNIT).to_integral_value(rounding=ROUND_HALF_UP))

def cents_to_str(cents: int) -> str:
    """Format integer cents as a two-decimal-place string."""
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    whole = cents // _CENTS_PER_UNIT
    frac = cents % _CENTS_PER_UNIT
    return f"{sign}{whole}.{frac:02d}"

class AmountIn(BaseModel):
    """Request body with a strictly positive amount up to 2 decimals."""
    amount: str = Field(..., description=DESC_AMOUNT)

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: str) -> str:
        """Ensure amount is a decimal string > 0 with <= 2 fractional digits."""
        try:
            dec = Decimal(v)
        except (InvalidOperation, TypeError):
            raise ValueError(ERR_AMOUNT_DECIMAL)
        if dec <= 0:
            raise ValueError(ERR_AMOUNT_POSITIVE)
        if abs(dec.as_tuple().exponent) > _MAX_DECIMAL_PLACES:
            raise ValueError(ERR_AMOUNT_DECIMALS)
        return v

    def amount_cents(self) -> int:
        """Return the amount as integer cents."""
        return to_cents(Decimal(self.amount))

class BalanceOut(BaseModel):
    """Response model with account number and formatted balance."""
    account_number: str
    balance: str = Field(..., description=DESC_BALANCE)
