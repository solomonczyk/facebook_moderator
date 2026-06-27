# TASK 015 — Real Telegram Operator Chat Enablement

> Date: 2026-06-27
> Verdict: ACCEPTED WITH BLOCKERS

## Summary

Built safe Telegram real-send infrastructure. All guards in place. Real activation requires operator to configure `TELEGRAM_BOT_TOKEN` and `TELEGRAM_OPERATOR_CHAT_ID`.

## New Commands

| Command | Purpose |
|---------|---------|
| `python -m app.telegram_setup_check` | Check env vars (masks tokens) |
| `python -m app.telegram_send_test --real` | Send one test message to operator |
| `python -m app.telegram_queue_test --real` | Send queue notification with buttons |

## Setup Check Result

| Field | Value |
|-------|-------|
| Bot token | [NOT SET] |
| Operator chat | [NOT SET] |
| Test mode | true |
| Can real send | false |

## Safety Guards

| Guard | Status |
|-------|--------|
| TEST_MODE=true blocks real send | ✅ |
| --real flag required for real send | ✅ |
| Operator chat ID allowlist | ✅ |
| Token masked in all artifacts | ✅ |
| .env not tracked | ✅ |
| No Facebook actions | ✅ |
| production_accepted=false | ✅ |

## Blockers (for real activation)

1. Operator must set `TELEGRAM_BOT_TOKEN` in `.env`
2. Operator must set `TELEGRAM_OPERATOR_CHAT_ID` in `.env`
3. Operator must set `TELEGRAM_TEST_MODE=false`
4. Operator runs `python -m app.telegram_send_test --real` to verify
5. Operator runs `python -m app.telegram_queue_test --real` to test buttons

## Operator Activation Steps

```bash
# 1. Configure env (NEVER commit .env)
export TELEGRAM_BOT_TOKEN="123456:ABC..."
export TELEGRAM_OPERATOR_CHAT_ID="123456789"
export TELEGRAM_TEST_MODE=false

# 2. Verify setup (token masked)
python -m app.telegram_setup_check

# 3. Send test message
python -m app.telegram_send_test --real

# 4. Send queue notification
python -m app.telegram_queue_test --real

# 5. Press Approve button in Telegram
# 6. Verify queue status changed
curl http://127.0.0.1:8000/api/runtime-agent/queue
```
