from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert "status" in r.json()

def test_get_balance_existing():
    r = client.get("/accounts/1001/balance")
    assert r.status_code == 200
    assert r.json()["balance"] == "1000.00"

def test_deposit_and_withdraw():
    r = client.post("/accounts/1002/deposit", json={"amount": "10.50"})
    assert r.status_code == 200
    assert r.json()["balance"] == "261.00"  # 250.50 + 10.50

    r = client.post("/accounts/1002/withdraw", json={"amount": "1.25"})
    assert r.status_code == 200
    assert r.json()["balance"] == "259.75"

def test_insufficient_funds():
    r = client.post("/accounts/1002/withdraw", json={"amount": "99999.99"})
    assert r.status_code == 400
    assert r.json()["detail"] == "insufficient funds"

def test_404_for_missing_account():
    r = client.get("/accounts/9999/balance")
    assert r.status_code == 404
    r = client.post("/accounts/9999/deposit", json={"amount": "1.00"})
    assert r.status_code == 404
