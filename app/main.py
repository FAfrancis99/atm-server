"""FastAPI app for a minimal ATM server.

Provides in-memory accounts with endpoints to get balance, deposit, and withdraw.
"""

from typing import Any, Dict

from fastapi import FastAPI, HTTPException, status
from .models import AmountIn, BalanceOut, cents_to_str
from .constants import (
    APP_TITLE,
    APP_VERSION,
    ENV_PRELOAD_ACCOUNTS,
    ROUTE_HEALTH,
    ROUTE_ACCOUNT_BALANCE,
    ROUTE_ACCOUNT_DEPOSIT,
    ROUTE_ACCOUNT_WITHDRAW,
    ROUTE_ROOT,
    KEY_STATUS,
    STATUS_OK,
    KEY_ACCOUNTS,
    KEY_MESSAGE,
    KEY_DOCS,
    KEY_SAMPLE_ACCOUNTS,
    ERR_ACCOUNT_NOT_FOUND,
    ERR_BALANCE_TYPE,
    ERR_PRELOAD_PARSE_FAILED,
)
from .storage import InMemoryStore
import os
import json
from decimal import Decimal, ROUND_HALF_UP

app = FastAPI(title=APP_TITLE, version=APP_VERSION)

# Named constants to avoid magic numbers
DEFAULT_ACCOUNTS: Dict[str, int] = {
    "1001": 100000,  # $1000.00
    "1002": 25050,   # $250.50
    "1003": 0,       # $0.00
    "1004": 50000,   # $500.00
    "1005": 12345,   # $123.45
    "1006": 999999,  # $9,999.99
}
DECIMAL_TWO_PLACES = Decimal("0.01")
CENTS_PER_UNIT = Decimal("100")

def _load_initial_accounts() -> Dict[str, int]:
    """Load initial accounts from PRELOAD_ACCOUNTS or return defaults.

    PRELOAD_ACCOUNTS example: {"1001":"1000.00","1002":"250.50"}
    Returns a mapping of account number to balance in cents.
    """
    env = os.getenv(ENV_PRELOAD_ACCOUNTS)
    if not env:
        # Return a copy to prevent accidental mutation of module constant
        return dict(DEFAULT_ACCOUNTS)
    try:
        raw = json.loads(env)
        out = {}
        for acc, val in raw.items():
            if isinstance(val, str):
                cents = int((Decimal(val).quantize(DECIMAL_TWO_PLACES, rounding=ROUND_HALF_UP) * CENTS_PER_UNIT).to_integral_value())
            elif isinstance(val, (int, float)):
                cents = int(Decimal(str(val)).quantize(DECIMAL_TWO_PLACES, rounding=ROUND_HALF_UP) * CENTS_PER_UNIT)
            else:
                raise ValueError(ERR_BALANCE_TYPE)
            out[str(acc)] = cents
        return out
    except Exception as e:
        raise RuntimeError(f"{ERR_PRELOAD_PARSE_FAILED}: {e}")

store = InMemoryStore(_load_initial_accounts())

@app.get(ROUTE_HEALTH)
def health() -> Dict[str, Any]:
    """Return service status and list of account numbers."""
    return {KEY_STATUS: STATUS_OK, KEY_ACCOUNTS: list(store.snapshot().keys())}

@app.get(ROUTE_ACCOUNT_BALANCE, response_model=BalanceOut)
def get_balance(account_number: str) -> BalanceOut:
    """Return the current balance for the given account.

    Raises 404 if the account is not found.
    """
    try:
        bal_cents = store.get_balance_cents(account_number)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERR_ACCOUNT_NOT_FOUND)
    return BalanceOut(account_number=account_number, balance=cents_to_str(bal_cents))

@app.post(ROUTE_ACCOUNT_DEPOSIT, response_model=BalanceOut)
def deposit(account_number: str, body: AmountIn) -> BalanceOut:
    """Deposit the provided amount into the account.

    Raises 404 if the account is not found.
    """
    try:
        new_bal = store.deposit(account_number, body.amount_cents())
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERR_ACCOUNT_NOT_FOUND)
    return BalanceOut(account_number=account_number, balance=cents_to_str(new_bal))

@app.post(ROUTE_ACCOUNT_WITHDRAW, response_model=BalanceOut)
def withdraw(account_number: str, body: AmountIn) -> BalanceOut:
    """Withdraw the provided amount from the account.

    Raises 404 if missing account or 400 for insufficient funds.
    """
    try:
        new_bal = store.withdraw(account_number, body.amount_cents())
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERR_ACCOUNT_NOT_FOUND)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return BalanceOut(account_number=account_number, balance=cents_to_str(new_bal))

@app.get(ROUTE_ROOT)
def root() -> Dict[str, Any]:
    """Root endpoint with service info and example accounts."""
    return {KEY_MESSAGE: APP_TITLE, KEY_DOCS: "/docs", KEY_SAMPLE_ACCOUNTS: store.snapshot()}
