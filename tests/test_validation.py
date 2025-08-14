"""Validation tests for amount inputs and error responses."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_invalid_amounts_return_422() -> None:
    # Too many decimals
    r = client.post("/accounts/1001/deposit", json={"amount": "1.234"})
    assert r.status_code == 422

    # Negative
    r = client.post("/accounts/1001/deposit", json={"amount": "-5.00"})
    assert r.status_code == 422

    # Zero
    r = client.post("/accounts/1001/deposit", json={"amount": "0.00"})
    assert r.status_code == 422

    # Non-numeric
    r = client.post("/accounts/1001/deposit", json={"amount": "abc"})
    assert r.status_code == 422


def test_missing_amount_field_returns_422() -> None:
    r = client.post("/accounts/1001/deposit", json={})
    assert r.status_code == 422
