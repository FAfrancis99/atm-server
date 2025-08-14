"""Thread-safe in-memory store for account balances (integer cents)."""

from __future__ import annotations
from threading import Lock
from typing import Dict
from .models import cents_to_str

class InMemoryStore:
    """Simple in-memory storage with per-account locks."""

    def __init__(self, initial_accounts: Dict[str, int] | None = None) -> None:
        self._balances: Dict[str, int] = dict(initial_accounts or {})
        self._locks: Dict[str, Lock] = {acc: Lock() for acc in self._balances}

    def _get_lock(self, account_number: str) -> Lock:
        """Return a lock for the account, creating it if necessary."""
        if account_number not in self._locks:
            self._locks[account_number] = Lock()
        return self._locks[account_number]

    def has_account(self, account_number: str) -> bool:
        """True if the account exists."""
        return account_number in self._balances

    def get_balance_cents(self, account_number: str) -> int:
        """Return balance in cents or raise KeyError if missing."""
        if account_number not in self._balances:
            raise KeyError("account not found")
        return self._balances[account_number]

    def deposit(self, account_number: str, amount_cents: int) -> int:
        """Add amount to balance atomically and return new balance.

        Raises KeyError if the account is missing.
        """
        if account_number not in self._balances:
            raise KeyError("account not found")
        lock = self._get_lock(account_number)
        with lock:
            self._balances[account_number] += amount_cents
            return self._balances[account_number]

    def withdraw(self, account_number: str, amount_cents: int) -> int:
        """Subtract amount from balance atomically and return new balance.

        Raises KeyError if missing account, ValueError for insufficient funds.
        """
        if account_number not in self._balances:
            raise KeyError("account not found")
        lock = self._get_lock(account_number)
        with lock:
            bal = self._balances[account_number]
            if amount_cents > bal:
                raise ValueError("insufficient funds")
            self._balances[account_number] = bal - amount_cents
            return self._balances[account_number]

    def create_account(self, account_number: str, opening_balance_cents: int = 0) -> None:
        """Create a new account or raise ValueError if it already exists."""
        if account_number in self._balances:
            raise ValueError("account already exists")
        self._balances[account_number] = opening_balance_cents
        self._locks[account_number] = Lock()

    def snapshot(self) -> Dict[str, str]:
        """Return a mapping of account to formatted balance string."""
        return {k: cents_to_str(v) for k, v in self._balances.items()}
