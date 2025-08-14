from pydantic import BaseModel, Field, field_validator
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

_TWO_PLACES = Decimal("0.01")

def to_cents(amount: Decimal) -> int:
    q = amount.quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)
    return int((q * 100).to_integral_value(rounding=ROUND_HALF_UP))

def cents_to_str(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}{cents // 100}.{cents % 100:02d}"

class AmountIn(BaseModel):
    amount: str = Field(..., description="Amount in standard decimal notation, e.g. '100.00'.")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: str) -> str:
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
        return to_cents(Decimal(self.amount))

class BalanceOut(BaseModel):
    account_number: str
    balance: str = Field(..., description="Balance as a string with 2 decimal places.")
