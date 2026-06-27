# Operator Daily Workflow — Sezonski Rad Srbija

> Version: 1.0 | Date: 2026-06-27

## Quick Reference

| Step | Command | What happens |
|------|---------|-------------|
| 1. Daily | `/today` | Посмотреть сводку в Telegram |
| 2. Bundle | `/postpack` | Готовый пакет текстов для FB |
| 3. Publish | **Manually** copy text to Facebook group | Вы публикуете, не бот |
| 4. Status | `/done <id>` | Отметить опубликованным (опционально) |

## What the Agent Does Independently

- Discovers public Facebook groups about seasonal work
- Extracts text from public posts (screenshots in real mode)
- Classifies content: job_offer, worker_search, warning, spam, etc.
- Extracts fields: location, pay, contact, accommodation, job type
- Assesses risk: low / medium / high
- Creates queue items needing your approval
- Builds daily digest from approved items
- Sends Telegram notifications (test mode by default)

## What You Must Do Manually

- **Approve or reject** each queue item (via Telegram or API)
- **Edit** suggested text if needed
- **Copy approved digest** to Facebook group manually
- **Decide** on escalated/high-risk items
- **Enable real Telegram mode** when ready (`TELEGRAM_TEST_MODE=false`)
- **Enable production** only when fully satisfied (`production_accepted=true`)

## Daily Commands (Quick Start)

```bash
# 1. Run public intake (dry-run = safe, no browser)
cd facebook_moderator
PYTHONPATH=backend python -m app.facebook_public_intake --dry-run --max-groups 5

# 2. View queue (via API)
curl http://127.0.0.1:8000/api/runtime-agent/queue

# 3. Build digest from approved items
PYTHONPATH=backend python -m app.daily_digest --date $(date +%Y-%m-%d)

# 4. Run full E2E demo
PYTHONPATH=backend python -m app.facebook_public_intake.e2e_demo --dry-run

# 5. Final smoke test
PYTHONPATH=backend python -m app.final_smoke --dry-run
```

## Telegram Commands

| Command | What it does |
|---------|-------------|
| `/start` | Show welcome message |
| `/status` | Runtime health, safety gates, queue count |
| `/queue` | Show pending items with approve/reject buttons |
| `/digest` | Generate daily digest draft |
| `/addlead <text>` | Manually submit a lead for analysis |
| `/help` | Show available commands |

## Telegram Buttons

| Button | Meaning | Queue Status After |
|--------|---------|--------------------|
| Approve | Content is safe, ready for manual FB publish | approved |
| Reject | Content violates rules | rejected |
| Edit | Change suggested text | edited (reply with new text) |
| Request Info | Missing information, ask author | needs_info |
| Escalate | Needs deeper operator review | needs_info |
| Spam | Mark as spam | spam |

## Safety Notes

- **Agent NEVER publishes to Facebook.** You must manually copy/paste.
- **High-risk items are NEVER auto-approved.** They go to escalation.
- **Spam is NEVER included in digest.** It is marked and excluded.
- **Digest is a DRAFT until you approve it.** Always review before posting.
- **`production_accepted` is FALSE.** Production mode requires your explicit command.
- **Telegram is in TEST MODE by default.** No real messages sent until you configure it.

## Digest Posting Checklist

Before posting the digest to Facebook:
- [ ] Review each included item — is contact/location/pay accurate?
- [ ] Check that no forbidden words appear (provereno, sigurno, garantovano)
- [ ] Verify disclaimer is present
- [ ] Confirm only approved items are included
- [ ] Copy text manually to Facebook group
- [ ] Do NOT mark as "provereno" or "garantovano"

## Environment Variables (for reference)

```
TELEGRAM_BOT_TOKEN=...        # Bot token from @BotFather
TELEGRAM_OPERATOR_CHAT_ID=... # Your Telegram chat ID
TELEGRAM_TEST_MODE=true       # false = real send to operator
LLM_PROVIDER=deepseek         # LLM provider
LLM_API_KEY=...               # API key
```

## Files You May Need

- Brain system prompt: `backend/brain/PROMPTS/SystemPrompt.md`
- Project memory: `docs/project/PROJECT_MEMORY.md`
- Project rules: `docs/project/PROJECT_CANON/`
- Audit proofs: `docs/audits/`
- Screenshots: `artifacts/screenshots/`
- Test payloads: `artifacts/test_telegram_payloads/`
