"""Centralized string constants to avoid magic strings across the app."""

# App metadata
APP_TITLE = "Mini ATM Server"
APP_VERSION = "1.0.0"

# Environment variables
ENV_PRELOAD_ACCOUNTS = "PRELOAD_ACCOUNTS"

# Routes
ROUTE_ROOT = "/"
ROUTE_HEALTH = "/health"
ROUTE_ACCOUNT_BALANCE = "/accounts/{account_number}/balance"
ROUTE_ACCOUNT_DEPOSIT = "/accounts/{account_number}/deposit"
ROUTE_ACCOUNT_WITHDRAW = "/accounts/{account_number}/withdraw"

# JSON keys and common values
KEY_STATUS = "status"
STATUS_OK = "ok"
KEY_ACCOUNTS = "accounts"
KEY_MESSAGE = "message"
KEY_DOCS = "docs"
KEY_SAMPLE_ACCOUNTS = "sample_accounts"

# Error / info messages
ERR_ACCOUNT_NOT_FOUND = "account not found"
ERR_INSUFFICIENT_FUNDS = "insufficient funds"
ERR_ACCOUNT_EXISTS = "account already exists"
ERR_BALANCE_TYPE = "balance must be string or number"
ERR_PRELOAD_PARSE_FAILED = "Failed to parse PRELOAD_ACCOUNTS"

# Model field descriptions and validation messages
DESC_AMOUNT = "Amount in standard decimal notation, e.g. '100.00'."
ERR_AMOUNT_DECIMAL = "amount must be a decimal number (e.g., '12.34')"
ERR_AMOUNT_POSITIVE = "amount must be positive"
ERR_AMOUNT_DECIMALS = "amount must have at most 2 decimal places"
DESC_BALANCE = "Balance as a string with 2 decimal places."
