"""Basic concurrency test to ensure per-account operations remain consistent.

Note: This is a lightweight smoke test for thread-safety, not a full stress test.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_parallel_deposits_single_account() -> None:
    # Use account 1003 (starts at 0.00)
    amounts = ["1.00"] * 20  # total 20.00

    def deposit_once() -> None:
        r = client.post("/accounts/1003/deposit", json={"amount": "1.00"})
        assert r.status_code == 200

    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = [ex.submit(deposit_once) for _ in amounts]
        for f in as_completed(futures):
            f.result()

    # Final balance should be exactly 20.00
    r = client.get("/accounts/1003/balance")
    assert r.status_code == 200
    assert r.json()["balance"] == "20.00"
