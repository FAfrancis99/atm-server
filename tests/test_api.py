"""Integration tests for the ATM API (FastAPI TestClient).

These tests exercise the public HTTP interface only, treating the server as
an external black box. They verify success paths and common error cases.

Notes:
- Data is stored in memory; each test run starts from the same defaults.
- Default demo accounts: 1001 → 1000.00, 1002 → 250.50
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health() -> None:
    """Health endpoint returns status and an account list."""
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert "status" in body
    assert body["status"] == "ok"
    assert isinstance(body.get("accounts", []), list)

def test_get_balance_existing() -> None:
    """Balance for existing account (1001) matches the default value."""
    r = client.get("/accounts/1001/balance")
    assert r.status_code == 200
    data = r.json()
    assert data["account_number"] == "1001"
    assert data["balance"] == "1000.00"

def test_deposit_and_withdraw() -> None:
    """Deposits increase and withdrawals decrease the balance accurately.

    Start at 250.50 for account 1002:
    - After +10.50 → 261.00
    - After -1.25 → 259.75
    """
    r = client.post("/accounts/1002/deposit", json={"amount": "10.50"})
    assert r.status_code == 200
    assert r.json()["balance"] == "261.00"  # 250.50 + 10.50

    r = client.post("/accounts/1002/withdraw", json={"amount": "1.25"})
    assert r.status_code == 200
    assert r.json()["balance"] == "259.75"

def test_insufficient_funds() -> None:
    """Overdraw attempts return 400 with a clear error message."""
    r = client.post("/accounts/1002/withdraw", json={"amount": "99999.99"})
    assert r.status_code == 400
    assert r.json()["detail"] == "insufficient funds"

def test_404_for_missing_account() -> None:
    """Operations on non-existent accounts return 404 Not Found."""
    r = client.get("/accounts/9999/balance")
    assert r.status_code == 404
    r = client.post("/accounts/9999/deposit", json={"amount": "1.00"})
    assert r.status_code == 404
