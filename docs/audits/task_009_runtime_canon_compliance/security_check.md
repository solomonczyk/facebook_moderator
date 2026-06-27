# Security Check

> Date: 2026-06-27
> Method: Multi-pattern grep across entire repository

## Secrets Scan

```bash
grep -rE "sk-|api_key.*=|ANTHROPIC_API_KEY.*=.*sk-" backend/ docs/ --include="*.py" --include="*.md" --include="*.json"
```

**Result: NO SECRETS FOUND.**

All API key values are loaded from environment:
- `os.getenv("LLM_API_KEY")` / `os.getenv("ANTHROPIC_API_KEY")` — in `llm/config.py`, `services/llm_client.py`
- `os.getenv("TELEGRAM_BOT_TOKEN")` — in `telegram_bot/bot.py`, `analyst_agent/telegram_escalation.py`
- `os.getenv("TELEGRAM_OPERATOR_CHAT_ID")` — in `telegram_bot/bot.py`, `analyst_agent/telegram_escalation.py`

## .env Tracking

```bash
git ls-files .env
```

**Result: .env NOT TRACKED.** (Empty output = no tracked .env file)

No `.env.example` or `.env.template` files found either — environment variable names are documented in PROJECT_MEMORY.md only.

## Hardcoded Defaults (safe)

- `LLMConfig.provider = "deepseek"` — provider name only, not a secret
- `LLMConfig.base_url = "https://api.deepseek.com/anthropic"` — public URL
- `LLMConfig.model = "DeepSeek-V4-Pro"` — model identifier
- `DATABASE_URL = "sqlite:///./sezonski_rad_aggregator.db"` — local file path
- No hardcoded IP addresses, passwords, or tokens found

## Token Leakage Prevention

- `telegram_bot/bot.py` line 12: `logging.getLogger("httpx").setLevel(logging.WARNING)` — suppresses httpx URL logging to prevent token in journal (commit `df01890`)
- `telegram_escalation.py` validates token is not `"REPLACE_ME"` before use

## Dangerous Files

- `backend/app/account_worker/browser_session.py` — launches real Chrome browser, but gated by `WorkerConfig.can_start()` which rejects if any dangerous gate is True
- `backend/app/runtime_intake/clipboard_intake.py` — reads system clipboard (PowerShell/pbpaste/xclip), enabled by default (FINDING-007)
- No `eval()`, `exec()`, or `os.system()` calls in runtime code

## API Security

All API endpoints bind to `127.0.0.1`:
- Aggregator API: `127.0.0.1:8000`
- No authentication middleware (relies on localhost-only deployment)
- No rate limiting on API endpoints
- No CORS configuration

## Verdict

**PASS** — No committed secrets. `.env` not tracked. All sensitive values from environment. One note: clipboard intake defaults to enabled (low severity, see FINDING-007).
