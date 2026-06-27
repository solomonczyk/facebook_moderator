# TASK 016 — Real Daily Workflow Pilot

> Date: 2026-06-27
> Verdict: ACCEPTED WITH BLOCKERS

## Summary

Daily workflow pilot runner built and tested in dry-run mode. Full 7-step pipeline works end-to-end. Real Telegram activation blocked pending operator token configuration (same blocker as TASK 015).

## Pilot Results (dry-run)

| Step | Result |
|------|--------|
| 1. Setup check | No token configured |
| 2. Public intake | 5 groups, 5 candidates |
| 3. Classify + queue | 5/5 items |
| 4. Telegram notifications | 5 test payloads |
| 5. Operator actions | 2 approved, 1 needs_info, 1 escalate, 1 spam |
| 6. Digest builder | 2 items included, 666 chars |
| 7. Final digest | saved to artifacts/ |

## Real Activation Steps (for operator)

```bash
# 1. Configure
export TELEGRAM_BOT_TOKEN="your-bot-token"
export TELEGRAM_OPERATOR_CHAT_ID="your-chat-id"
export TELEGRAM_TEST_MODE=false

# 2. Verify
python -m app.telegram_setup_check

# 3. Run real pilot
python -m app.daily_pilot --real
```

## Commands

| Command | Mode | Purpose |
|---------|------|---------|
| `python -m app.daily_pilot` | Dry-run | Full workflow test |
| `python -m app.daily_pilot --real` | Real | Live Telegram + queue |

## Blockers

- TELEGRAM_BOT_TOKEN not configured
- TELEGRAM_OPERATOR_CHAT_ID not configured
- Real callback verification pending operator button press
