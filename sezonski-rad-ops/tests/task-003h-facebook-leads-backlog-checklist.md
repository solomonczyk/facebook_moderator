---
type: test_checklist
task: TASK-003H
date: 2026-06-26
---

# Test Checklist — Task 003H Facebook Leads Backlog

## Structural Checks

- [x] 1. Backlog file exists: `reports/live-market-feed/backlog/2026-06-26-facebook-leads-backlog.md`
- [x] 2. Tomorrow live market feed exists: `reports/live-market-feed/2026-06-27-live-market-feed.md`
- [x] 3. At least 5 Facebook leads extracted: 9 total (7 vacancies + 2 workers)
- [x] 4. At least 3 tomorrow digest candidates: 4 confirmed candidates
- [x] 5. Vacancy records created: 5 files in `vacancies/facebook/`
- [x] 6. Worker records created: 2 files in `workers/`

## Content Checks

- [x] 7. Duplicate Velibor lead flagged for operator decision (not silently excluded)
- [x] 8. Worker leads NOT included in vacancy digest (separated in both backlog and feed)
- [x] 9. Needs-manual-review leads clearly marked (FB-006 Ovcina, FB-007 Trnava, W-002)
- [x] 10. Disclaimer exists in Draft Digest Input
- [x] 11. No "provereno" / "sigurno" / "garantovano" in lead descriptions
- [x] 12. No invented conditions — all missing_info explicitly stated
- [x] 13. All contacts from operator-provided screenshots (not auto-scraped)
- [x] 14. ocr_confidence marked for leads with unclear text
- [x] 15. needs_operator_confirmation flagged where applicable

## Source Integrity

- [x] 16. Facebook automation: false (confirmed in all frontmatter)
- [x] 17. Source marked as operator_provided_facebook_screenshot
- [x] 18. Source group: Malinari Srbija
- [x] 19. Today's digest NOT repeated (only tomorrow's feed prepared)

## Proof & Delivery

- [x] 20. Proof JSON valid
- [x] 21. Git commit done
- [x] 22. Files not pushed (operator controls push)

## Summary

| Check | Result |
|-------|--------|
| Total checks | 22 |
| Passed | 22 |
| Failed | 0 |
| Pending operator action | 3 (FB-006 contact, FB-007 phone, Velibor decision) |
