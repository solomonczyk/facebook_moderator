# TASK 016B — Server .env Real Telegram Activation Fix

> Date: 2026-06-27
> Verdict: ACCEPTED

## Problem

Server has `.env` with real tokens, but runtime showed `TELEGRAM_BOT_TOKEN: [NOT SET]` because no `python-dotenv` loader was called before `os.getenv()`.

## Fix

Created shared `backend/app/env_loader.py`:
- Searches for `.env` in: project root, `backend/`, parent directories
- Loads via `python-dotenv` if found
- Returns sanitized diagnostics (tokens always masked)
- Idempotent — safe to call multiple times

Updated 5 files to use shared loader:
- `telegram_setup_check.py`
- `telegram_send_test.py`
- `telegram_queue_test.py`
- `daily_pilot.py`
- `telegram_bot/notifier.py`

## Verification

| Check | Result |
|-------|--------|
| .env file search | Works (found in project root) |
| Token detection | Present, masked |
| Chat ID detection | Present, masked |
| Token never exposed | Confirmed |
| Real send gated by --real | Confirmed |

## How It Works

```python
from app.env_loader import load_env
load_env()  # Searches for .env, loads into os.environ

# Or with explicit path:
load_env(env_file="/path/to/.env")
```

## Server Activation

On the VPS, after deploying this fix:
```bash
python -m app.telegram_setup_check
# Should show: .env file: FOUND, token present, chat ID present
python -m app.telegram_send_test --real
# Should send 1 message to operator
```
