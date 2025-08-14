from fastapi import FastAPI, HTTPException
from .models import AmountIn, BalanceOut, cents_to_str
from .storage import InMemoryStore
import os, json
from decimal import Decimal, ROUND_HALF_UP

app = FastAPI(title="Mini ATM Server", version="1.0.0")

def _load_initial_accounts():
    env = os.getenv("PRELOAD_ACCOUNTS")
    if not env:
        return {"1001": 100000, "1002": 25050}
    try:
        raw = json.loads(env)
        out = {}
        for acc, val in raw.items():
            if isinstance(val, str):
                cents = int((Decimal(val).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) * 100).to_integral_value())
            elif isinstance(val, (int, float)):
                cents = int(Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) * 100)
            else:
                raise ValueError("balance must be string or number")
            out[str(acc)] = cents
        return out
    except Exception as e:
        raise RuntimeError(f"Failed to parse PRELOAD_ACCOUNTS: {e}")

store = InMemoryStore(_load_initial_accounts())

@app.get("/health")
def health():
    return {"status": "ok", "accounts": list(store.snapshot().keys())}

@app.get("/accounts/{account_number}/balance", response_model=BalanceOut)
def get_balance(account_number: str):
    try:
        bal_cents = store.get_balance_cents(account_number)
    except KeyError:
        raise HTTPException(status_code=404, detail="account not found")
    return BalanceOut(account_number=account_number, balance=cents_to_str(bal_cents))

@app.post("/accounts/{account_number}/deposit", response_model=BalanceOut)
def deposit(account_number: str, body: AmountIn):
    try:
        new_bal = store.deposit(account_number, body.amount_cents())
    except KeyError:
        raise HTTPException(status_code=404, detail="account not found")
    return BalanceOut(account_number=account_number, balance=cents_to_str(new_bal))

@app.post("/accounts/{account_number}/withdraw", response_model=BalanceOut)
def withdraw(account_number: str, body: AmountIn):
    try:
        new_bal = store.withdraw(account_number, body.amount_cents())
    except KeyError:
        raise HTTPException(status_code=404, detail="account not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return BalanceOut(account_number=account_number, balance=cents_to_str(new_bal))

@app.get("/")
def root():
    return {
        "message": "Mini ATM Server",
        "docs": "/docs",
        "sample_accounts": store.snapshot()
    }
