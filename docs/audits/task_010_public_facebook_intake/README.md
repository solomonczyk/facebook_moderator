# TASK 010 — Controlled Public Facebook Intake

> Date: 2026-06-27
> Verdict: ACCEPTED

## Summary

Built a safe public Facebook intake pipeline that discovers seasonal work groups, captures screenshots of public pages (no login), extracts text, deduplicates, and feeds into the TASK 009 intake queue. All findings require operator approval. Nothing is auto-published.

## Module

`backend/app/facebook_public_intake/` — 7 files, ~550 lines

| File | Purpose |
|------|---------|
| `config.py` | Safety gates, rate limits, HARD_FORBIDDEN list |
| `discovery.py` | Curated seed list of 7 known public groups + 8 search terms |
| `screenshotter.py` | Selenium-based capture, incognito, no cookies, no login |
| `ocr_extractor.py` | Text extraction (DOM + pytesseract fallback), post splitting |
| `deduplicator.py` | SHA256 + text prefix dedup, seen-set tracking |
| `pipeline.py` | Full orchestrator: discovery → screenshot → extract → dedup → intake |
| `__main__.py` | CLI: `python -m app.facebook_public_intake --dry-run` |

## Demo Results

| Metric | Value |
|--------|-------|
| Seed groups | 7 |
| Search terms | 8 |
| Simulated candidates extracted | 7 |
| Duplicates detected & skipped | 1 |
| New candidates sent to intake | 6 |
| Correctly classified | 6/6 |
| High risk escalated | Yes (all 3) |
| Operator approval required | ALWAYS |

## Safety Proof

| Check | Status |
|-------|--------|
| No Facebook login | ✅ |
| No cookies/session | ✅ |
| No Facebook publish | ✅ |
| No Facebook comment | ✅ |
| No Facebook message | ✅ |
| Incognito browser mode | ✅ |
| Dry-run by default | ✅ |
| Rate limited (5 groups, 3 screenshots each) | ✅ |
| All candidates → operator approval queue | ✅ |
| High risk → escalated, never published | ✅ |
| `production_accepted` = false | ✅ |

## CLI Usage

```bash
# Dry run (default, safe)
python -m app.facebook_public_intake --dry-run --max-groups 5

# Real run (requires Chrome + Selenium)
python -m app.facebook_public_intake --no-dry-run --max-groups 3 --screenshots-per-group 2
```

## Next

TASK 011 — Telegram Operator Approval Flow
