# TASK 013 — Daily Digest Builder from Approved Queue Items

> Date: 2026-06-27
> Verdict: ACCEPTED

## Summary

Daily digest builder that collects approved low-risk queue items, formats a Serbian-language Facebook post with disclaimer, and submits the digest back to the operator approval queue with Telegram notification.

## Module

`backend/app/daily_digest/` — 2 files

| File | Purpose |
|------|---------|
| `builder.py` | Filter, format, queue integration, forbidden word check |
| `__main__.py` | CLI: `python -m app.daily_digest --dry-run --date YYYY-MM-DD` |

## Demo Results

| Metric | Value |
|--------|-------|
| Total source items | 6 |
| Included in digest | 2 |
| Excluded | 4 |
| Fallback used | No |
| Digest length | 804 chars |
| Forbidden words | 0 |
| Queue item created | Yes (operator_approval_required=true) |
| Telegram notification | Yes (test mode) |

## Exclusion Proof

| Item | Status | Risk | Why Excluded |
|------|--------|------|-------------|
| q_demo_003 | needs_info | medium | Not approved |
| q_demo_004 | needs_info | high | Not approved, high risk |
| q_demo_005 | needs_info | high | Not approved, high risk |
| q_demo_006 | spam | high | Spam, not approved |

## Fallback Mode

When 0 usable approved items: generates "Nema dovoljno proverenih oglasa..." with CTA.

## CLI

```bash
python -m app.daily_digest --dry-run
python -m app.daily_digest --date 2026-06-27
```
