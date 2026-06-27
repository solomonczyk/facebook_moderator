# TASK 016C — Real Telegram Pilot Confirmation

> Date: 2026-06-27
> Verdict: ACCEPTED WITH BLOCKERS
> Blocker: Operator must run `--real` commands on server (has .env with tokens)

## Infrastructure Status: READY

All three utilities verified locally in dry-run/test mode.

## Operator: Run These 3 Commands on Server

```bash
cd /path/to/facebook_moderator

# 1. Verify .env loaded, tokens detected (masked)
PYTHONPATH=backend python -m app.telegram_setup_check

# 2. Send one test message to your Telegram
PYTHONPATH=backend python -m app.telegram_send_test --real

# 3. Send queue notification with buttons
PYTHONPATH=backend python -m app.telegram_queue_test --real
```

## Operator: After Running, Confirm

| Check | Expected |
|-------|----------|
| setup_check shows .env FOUND | ☐ |
| setup_check shows token masked (not exposed) | ☐ |
| Test message received in Telegram | ☐ |
| Queue notification received with buttons | ☐ |
| Pressed one button (e.g., Approve) | ☐ |
| Queue status changed after button press | ☐ |

## Expected Output (sanitized)

```
.env file:      FOUND (/path/to/.env)
Bot token:      1234****wxyz
Operator chat:  12****89
Test mode:      False
Can real send:  True
```

## Safety

- No Facebook actions
- No public group sends
- production_accepted=false
- .env NOT tracked
- Tokens never printed
