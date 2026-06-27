# Operator Launch Guide — Sezonski rad Srbija

> Date: 2026-06-27 | production_accepted: false

## 1. First Launch — Check

```bash
cd /opt/facebook_moderator && git pull
PYTHONPATH=backend python3 -m app.telegram_setup_check
```

Expected: `.env FOUND`, token masked, test_mode=false, can_real_send=true.

## 2. Pin the Post in Facebook Group

Copy-paste from [facebook_group_pinned_post_sr.md](../project/facebook_group_pinned_post_sr.md) into the Facebook group as a pinned announcement.

Do this **manually** in Facebook. The agent does NOT post.

## 3. Reply to Comments

Use templates from [facebook_comment_templates_sr.md](../project/facebook_comment_templates_sr.md):
- Employer missing info → "Hvala na objavi. Da bismo je objavili..."
- Worker missing info → "Hvala. Da bismo objavu pripremili..."
- Spam → "Ova objava je uklonjena jer krši pravila grupe."

## 4. Submit Structured Intake

### Employer Offer

```bash
curl -X POST http://127.0.0.1:8000/api/intake/employer-offer \
  -H "Content-Type: application/json" \
  -d '{
    "employer_name":"Gazdinstvo Petrović",
    "work_location":"Arilje",
    "job_type":"berba malina",
    "workers_needed":"10",
    "start_date":"1. jul",
    "pay_amount":"5000",
    "pay_type":"dnevnica",
    "working_hours_or_norm":"8 sati",
    "housing_provided":"da",
    "food_provided":"da",
    "payment_frequency":"dnevno",
    "contact":"064-123-4567"
  }'
```

### Worker Search

```bash
curl -X POST http://127.0.0.1:8000/api/intake/worker-search \
  -H "Content-Type: application/json" \
  -d '{
    "worker_name":"Marko Radnik",
    "current_location":"Ivanjica",
    "people_count":"3",
    "desired_job_type":"berba malina",
    "available_from":"odmah",
    "housing_needed":"da",
    "food_needed":"da",
    "contact":"065-111-222",
    "experience":"3 godine",
    "has_transport":"da"
  }'
```

## 5. Review in Telegram

Open Telegram, send these commands to the bot:

| Command | Shows |
|---------|-------|
| `/drafts` | Pending items ready for manual FB publish |
| `/spam` | Items in spam quarantine |
| `/queue` | All pending queue items with approve/reject buttons |
| `/status` | Runtime health and safety gates |
| `/forms` | Structured intake API reference |
| `/digest` | Generate daily digest draft |

## 6. Approve or Reject

For each item with buttons:
- **Approve** → item ready for manual FB publish
- **Reject** → item removed from publish queue
- **Edit** → reply with new text, then approve
- **Escalate** → flag for deeper review

## 7. Publish to Facebook

After approving in Telegram:
1. Check `/drafts` — approved items are listed
2. Copy the `suggested_text` from the queue
3. **Manually** paste into Facebook group as a new post
4. After posting, mark as published:

```bash
# Via API (if server running):
curl -X POST http://127.0.0.1:8000/api/runtime-agent/queue/{item_id}/mark-executed \
  -H "Content-Type: application/json" -d '{"operator":"you"}'
```

## 8. Build Daily Digest

```bash
cd /opt/facebook_moderator
PYTHONPATH=backend python3 -m app.daily_digest --date $(date +%Y-%m-%d)
```

The digest goes to Telegram as a queue item. Review, approve, then **manually** copy to Facebook.

## 9. Daily Workflow

```bash
# One command — full pipeline
cd /opt/facebook_moderator
PYTHONPATH=backend python3 -m app.daily_pilot --real
```

## 10. Safety Rules

- ❌ Agent NEVER publishes to Facebook
- ❌ Agent NEVER deletes posts or bans users
- ❌ Agent NEVER logs into Facebook
- ✅ All publishing is manual copy-paste by operator
- ✅ High-risk items always escalated
- ✅ Spam always quarantined
- ✅ Digest always requires operator approval before posting
