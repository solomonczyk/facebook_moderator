---
title: Dashboard
date: 2026-06-26
updated: 2026-06-26
---

# Dashboard — Sezonski rad Srbija

## Today's Tasks

- [ ] Sourcing: find 10–20 new vacancies
- [ ] Outreach: contact 3–5 groups/authors (max)
- [ ] Review queue: process pending reviews
- [ ] Moderation: process pending moderation cases
- [ ] Publishing: select 1–3 posts for today
- [ ] Daily report: fill and save

---

## Vacancy Queue

```dataview
TABLE
  date_added,
  location,
  job_type,
  employer_name,
  risk_level,
  status
FROM "vacancies"
WHERE status != "posted" AND status != "expired" AND status != "rejected" AND status != "filled"
SORT date_added DESC
```

## Worker Queue

```dataview
TABLE
  date_added,
  desired_job_type,
  location,
  status
FROM "workers"
WHERE status != "posted" AND status != "expired" AND status != "found_work" AND status != "rejected"
SORT date_added DESC
```

## Review Queue

```dataview
TABLE
  date_added,
  employer_name_optional,
  overall_rating,
  risk_level,
  status
FROM "reviews"
WHERE status != "posted" AND status != "rejected"
SORT date_added DESC
```

## Post Queue

```dataview
TABLE
  created_at,
  post_category,
  language,
  status
FROM "post-queue"
WHERE status != "posted"
SORT scheduled_for ASC
```

## Outreach Targets

```dataview
TABLE
  group_name,
  platform,
  language,
  status,
  last_contacted
FROM "outreach/target-groups"
WHERE status != "do_not_contact" AND status != "not_relevant"
SORT last_contacted ASC
```

---

## Pending Manual Publication

Posts ready to publish (operator must manually post to Facebook):

```dataview
TABLE
  created_at,
  post_category,
  language
FROM "post-queue/ready"
SORT created_at ASC
```

---

## Active Risks / Escalated Cases

```dataview
TABLE
  date_added,
  location,
  employer_name_optional,
  risk_level
FROM "reviews"
WHERE status = "escalated" OR status = "disputed"

---

## Moderation Queue

```dataview
TABLE
  date,
  post_type,
  verdict,
  risk_level,
  status
FROM "moderation/queue"
SORT date DESC
```

---

## Today's KPI

| Metric | Today |
|--------|-------|
| new_vacancies_found | |
| employers_contacted | |
| workers_added | |
| reviews_collected | |
| posts_published | |
| groups_contacted | |
| comments_received | |
| members_added | |
| suspicious_items_rejected | |

## Weekly KPI

| Metric | This Week | Last Week |
|--------|-----------|-----------|
| new_vacancies_found | | |
| employers_contacted | | |
| workers_added | | |
| reviews_collected | | |
| posts_published | | |
| groups_contacted | | |
| comments_received | | |
| members_added | | |
| suspicious_items_rejected | | |
