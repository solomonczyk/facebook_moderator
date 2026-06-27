# TASK 009 — One-Day Autonomous Group Operator MVP

> Date: 2026-06-27
> Verdict: ACCEPTED

## What was built

A unified end-to-end operator pipeline: text input → classify → extract → risk assess → queue action → operator approval required.

## New module

`backend/app/operator_mvp/` — unified intake endpoint with rule-based fallback classifier.

### POST /api/intake/manual

Accepts raw text, classifies, extracts fields, assesses risk, creates queue action, returns full decision.

**Input:**
```json
{
  "source": "facebook_manual",
  "text": "Tražimo 5 radnika za berbu malina...",
  "author_name": "...",
  "source_url": "...",
  "language": "sr"
}
```

**Output:**
```json
{
  "lead_id": "lead_...",
  "status": "queued",
  "classification": "job_offer",
  "risk_level": "low",
  "action_type": "create_group_post",
  "action_id": "q_...",
  "fields": { ... },
  "operator_summary": "...",
  "suggested_text": "...",
  "reason": "...",
  "operator_approval_required": true
}
```

## Pipeline

```
text → classify (9 categories) → extract fields → risk (low/medium/high)
     → determine action → create queue item → return response
```

## Demo Results: 5/5 passed

| Case | Classification | Risk | Action | Passed |
|------|---------------|------|--------|--------|
| demo_001 Normal job offer | job_offer | low | create_group_post | ✅ |
| demo_002 Worker couple search | worker_search | low | create_group_post | ✅ |
| demo_003 Incomplete job (no pay) | job_offer | medium | request_more_info | ✅ |
| demo_004 Employer warning | employer_warning | high | escalate_to_operator | ✅ |
| demo_005 Casino spam | spam | high | reject_as_spam | ✅ |

## What the agent can now do independently

1. Accept text input via API/manual intake
2. Classify: job_offer, worker_search, worker_experience, employer_warning, question, spam, unsafe, unknown
3. Extract: location, job_type, crop, pay, pay_unit, accommodation, food, working_hours, start_date, contact, employer_name, red_flags, missing_fields
4. Assess risk: low, medium, high (with escalation/block for high)
5. Create queue action: create_group_post, ask_clarifying_question, create_digest_item, escalate_to_operator, reject_as_spam, request_more_info
6. Generate safe text with disclaimer
7. Never publish without operator approval

## What still requires operator approval

- All Facebook publishing (manual by operator)
- High-risk content escalation decisions
- Telegram send (test mode only)
- Digest publication
- Production mode enablement

## API endpoints

- `POST /api/intake/manual` — unified intake
- `GET /api/intake/status` — MVP status
- `GET /api/runtime-agent/queue` — list queue
- `POST /api/runtime-agent/queue/{id}/approve` — approve action
- `POST /api/runtime-agent/queue/{id}/reject` — reject action
- `POST /api/runtime-agent/queue/{id}/edit` — edit action

## Tests run

- 5 demo cases (all passed)
- 10 existing test suites (all passed via compliance audit)

## Next step

TASK 010 — Connect real Telegram operator workflow, or controlled Facebook intake.
