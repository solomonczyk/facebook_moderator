# JSON Output Contract

The agent MUST return ONLY valid JSON. No markdown, no free text outside JSON.

```json
{
  "classification": "employer_job_post | worker_request | worker_group_available | review_experience | question | spam | suspicious | irrelevant | unclear",
  "confidence": 0.0,
  "risk_level": "low | medium | high",
  "recommended_action": "approve | approve_with_edits | reject | ask_missing_info | mark_spam | escalate",
  "digest_candidate": true,
  "public_post_allowed": true,
  "fields": {
    "job_type": "string | null",
    "location": "string | null",
    "workers_needed": "integer | null",
    "start_date": "string | null",
    "pay": "string | null",
    "payment_type": "string | null",
    "accommodation": "string | null",
    "food": "string | null",
    "transport": "string | null",
    "working_hours": "string | null",
    "contact": "string | null",
    "language": "string | null"
  },
  "missing_info": ["string"],
  "risk_flags": ["string"],
  "operator_summary": "Russian text, 1-2 sentences",
  "prepared_public_text": "Serbian text for Facebook",
  "prepared_reply_to_author": "Serbian reply text",
  "reason": "English, 1 sentence"
}
```

## Field Rules

- `classification`: ONE of the 9 allowed values
- `confidence`: 0.0–1.0
- `risk_level`: ONE of low/medium/high
- `recommended_action`: ONE of the 6 allowed values
- `digest_candidate`: true only for employer_job_post with contact+location+job_type
- `public_post_allowed`: false for spam, suspicious, high risk
- `fields`: all null if not found — never invent
- `missing_info`: list of Serbian labels for what's absent
- `risk_flags`: list of flags from the risk model
- `operator_summary`: Russian, short
- `prepared_public_text`: Serbian, safe, with disclaimer if needed
- `prepared_reply_to_author`: Serbian, polite, asking for missing info if needed
- `reason`: English, explain the decision

## Forbidden Words

NEVER use in prepared_public_text or prepared_reply_to_author:
- provereno
- sigurno
- garantovano
- najbolji poslodavac
- zagarantovano
