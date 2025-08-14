# Mini Project – ATM Server (FastAPI)

A minimal server‑side ATM system with in‑memory accounts and three operations:

- `GET /accounts/{account_number}/balance`
- `POST /accounts/{account_number}/deposit`
- `POST /accounts/{account_number}/withdraw`

> **Note**: This server stores data **in memory** (no database). Balances reset on restart.

## Quickstart (Local)

```
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open the interactive docs: http://127.0.0.1:8000/docs

### Preloaded demo accounts
Two accounts are preloaded by default:
- `1001` → `1000.00`
- `1002` → `250.50`

You can override the initial accounts with an environment variable:
```
export PRELOAD_ACCOUNTS='{"1001":"500.00","7777":"0.00"}'
uvicorn app.main:app --reload
```

## API Examples

```
# Health
curl http://localhost:8000/health

# Get balance
curl http://localhost:8000/accounts/1001/balance

# Deposit 10.50
curl -X POST http://localhost:8000/accounts/1002/deposit -H "Content-Type: application/json" -d '{"amount":"10.50"}'

# Withdraw 5
curl -X POST http://localhost:8000/accounts/1002/withdraw -H "Content-Type: application/json" -d '{"amount":"5.00"}'
```

Example response:
```
{
  "account_number": "1001",
  "balance": "995.00"
}
```

## Design Decisions

- **FastAPI + Pydantic v2** for concise, typed API and interactive Swagger docs.
- **Money as integer cents** to avoid floating‑point errors.
- **Validation**: positive amounts, max 2 decimal places.
- **Concurrency**: per‑account `Lock` guards deposit/withdraw.
- **No Auth / No DB**: per assignment; easy to extend later.

## Tests

```
pip install -r requirements.txt
pytest -q
```

## Deploy (choose one)

### Render (Docker)
1. Push this folder to GitHub.
2. In Render: New → Web Service → Build from Git repo.
3. Environment: Docker. Render sets `$PORT`; our command respects it.
4. (Optional) Set `PRELOAD_ACCOUNTS` env var.
5. Deploy. URL: `https://<service>.onrender.com`

### Railway (Docker)
1. Push to GitHub.
2. New Project → Deploy from Repo.
3. Detects Dockerfile. Set `PORT` if needed. Deploy.

### Heroku
1. `heroku create your-atm-server`
2. `git push heroku main`
3. `heroku open`

After deploying, your hosted URL becomes your submission link, e.g.:
`https://your-atm-server.onrender.com`

## Folder Layout

```
app/
  __init__.py
  main.py
  models.py
  storage.py
tests/
  test_api.py
Dockerfile
Procfile
requirements.txt
README.md
```

## Future Improvements

- Auth & per-account authorization
- Database persistence (PostgreSQL)
- Idempotency keys for POSTs
- Structured logging & metrics
- Rate limiting
