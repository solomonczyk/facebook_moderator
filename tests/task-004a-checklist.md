---
type: test_checklist
task: TASK-004A
date: 2026-06-26
---

# Test Checklist — Task 004A Aggregator Architecture

## Architecture Documentation

- [x] 1. seasonal-work-aggregator-004a.md — main architecture doc
- [x] 2. data-model-004a.md — JobLead, EmployerProfile, WorkerProfile, Review schemas
- [x] 3. source-ingestion-004a.md — source-agnostic intake design
- [x] 4. facebook-capture-risk-model-004a.md — capture disabled by default, risk gates
- [x] 5. trust-rating-review-model-004a.md — rating categories, safe wording, right of reply
- [x] 6. moderation-policy-004a.md — queue states, escalation triggers
- [x] 7. mvp-roadmap-004a.md — 4 layers with timeline

## Data Models

- [x] 8. JobLead model: 40+ fields, all required types
- [x] 9. EmployerProfile model: all required fields
- [x] 10. WorkerProfile model: all required fields
- [x] 11. Review model: 9 rating categories + metadata
- [x] 12. Classification enum: 11 values
- [x] 13. Source type enum: 9 values
- [x] 14. Risk flag enum: 12 values

## Backend Code (Python)

- [x] 15. models.py — all dataclasses + enums
- [x] 16. schemas.py — intake + review validation
- [x] 17. lead_normalizer.py — phone/pay/location extraction + missing_info
- [x] 18. duplicate_detector.py — phone, URL, text similarity, location+job matching
- [x] 19. freshness_scorer.py — 5 statuses with operator override
- [x] 20. risk_scorer.py — 12 flags, keyword detection
- [x] 21. digest_builder.py — formatting, sorting, disclaimer, forbidden words
- [x] 22. moderation_queue.py — approve/reject/escalate with history

## Tests (Python)

- [x] 23. test_aggregator_models.py — 6 tests
- [x] 24. test_lead_normalizer.py — 7 tests
- [x] 25. test_duplicate_detector.py — 5 tests
- [x] 26. test_freshness_scorer.py — 7 tests
- [x] 27. test_risk_scorer.py — 7 tests
- [x] 28. test_digest_builder.py — 6 tests

## Dangerous Actions — All Disabled

- [x] 29. No Facebook cookie scraping
- [x] 30. No headless Facebook bot
- [x] 31. No captcha bypass
- [x] 32. No auto-posting
- [x] 33. No auto-commenting
- [x] 34. No fake vacancies
- [x] 35. No fake reviews
- [x] 36. Facebook capture disabled by default

## Delivery

- [x] 37. Proof JSON valid
- [x] 38. Checklist complete
- [x] 39. Git commit done
- [x] 40. Working tree clean

## Summary

| Category | Checks | Passed |
|----------|--------|--------|
| Architecture docs | 7 | 7 |
| Data models | 7 | 7 |
| Backend code | 8 | 8 |
| Tests | 6 | 6 |
| Dangerous actions | 8 | 8 |
| Delivery | 4 | 4 |
| **Total** | **40** | **40** |
