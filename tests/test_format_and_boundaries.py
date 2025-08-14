"""Formatting and boundary condition tests for balances and amounts."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_balance_formatting_two_decimals() -> None:
    r = client.get("/accounts/1001/balance")
    assert r.status_code == 200
    bal = r.json()["balance"]
    assert "." in bal and len(bal.split(".")[1]) == 2


def test_large_deposit_with_rounding() -> None:
    # Start from a clean known account (1003 starts at 0.00 by default)
    r = client.post("/accounts/1003/deposit", json={"amount": "123456.789"})
    # Too many decimals -> validation 422
    assert r.status_code == 422

    r = client.post("/accounts/1003/deposit", json={"amount": "123456.78"})
    assert r.status_code == 200
    assert r.json()["balance"].endswith(".78")


def test_withdraw_exact_balance_to_zero() -> None:
    # Account 1004 starts with 500.00; withdraw exactly 500.00
    r = client.post("/accounts/1004/withdraw", json={"amount": "500.00"})
    assert r.status_code == 200
    assert r.json()["balance"] == "0.00"
