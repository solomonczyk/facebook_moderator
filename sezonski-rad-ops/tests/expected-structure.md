---
type: expected_structure
task: sezonski_rad_ops_001
date: 2026-06-26
---

# Expected Vault Structure

## Directory Tree

```
sezonski-rad-ops/
├── 00-dashboard.md
├── 01-daily-workflow.md
├── 02-rules.md
├── 03-risk-policy.md
├── 04-content-plan.md
├── README.md
│
├── vacancies/
│   ├── _template-vacancy.md
│   └── samples/
│       └── 2026-06-23-berry-picking-valjevo.md
│
├── workers/
│   ├── _template-worker.md
│   └── samples/
│       └── 2026-06-24-marko-subotica.md
│
├── reviews/
│   ├── _template-review.md
│   └── samples/
│       └── 2026-06-25-hladnjaca-smederevo.md
│
├── employers/
│   ├── _template-employer.md
│   └── samples/
│       └── vocarstvo-jovic.md
│
├── outreach/
│   ├── _template-target.md
│   ├── _template-outreach-log.md
│   ├── target-groups/
│   │   └── sezonski-poslovi-hrvatska.md
│   └── daily-logs/
│       └── 2026-06-26.md
│
├── moderation/
│   ├── _template-moderation-case.md
│   ├── queue/
│   └── resolved/
│
├── post-queue/
│   ├── _template-post.md
│   ├── ready/
│   ├── posted/
│   └── rejected/
│
├── templates/
│   ├── serbian/    (10 files)
│   ├── russian/    (10 files)
│   ├── ukrainian/  (10 files)
│   ├── hungarian/  (10 files)
│   └── romanian/   (10 files)
│
├── reports/
│   ├── _template-daily-report.md
│   └── _template-weekly-report.md
│
├── proof/
│   ├── proof.json
│   └── validation-report.md
│
└── tests/
    ├── test-cases.md
    └── expected-structure.md
```

## File Count

| Category | Expected Count |
|----------|---------------|
| Root files | 6 |
| Entity templates | 8 |
| Sample records | 4 |
| Outreach targets | 1 |
| Outreach logs | 1 |
| Multilingual templates | 50 |
| Report templates | 2 |
| Proof files | 2 |
| Test files | 2 |
| **Total** | **76** |

## Required YAML Fields by Entity

### Vacancy (22 fields)
type, status, source, source_url, facebook_post_url, date_added, last_checked, location, job_type, employer_name, contact_public, contact_private, start_date, workers_needed, pay_amount, pay_type, pay_frequency, working_hours, accommodation, food, transport, registered_work, languages, risk_level, verified_by_operator, posted_to_group, operator_approved, notes

### Worker (17 fields)
type, status, date_added, source, name_optional, contact_public, contact_private, location, desired_job_type, experience, available_from, needs_accommodation, can_travel, alone_pair_group, languages, risk_level, posted_to_group, operator_approved, notes

### Review (23 fields)
type, status, date_added, source, reviewer_language, location, employer_name_optional, job_type, work_period, promised_conditions, actual_conditions, pay_received, pay_on_time, accommodation_rating, food_rating, treatment_rating, work_conditions_rating, overall_rating, would_recommend, contains_personal_data, contains_insults, legal_risk, risk_level, safe_version_created, operator_approved, posted_to_group, facebook_post_url, safe_version_text, notes

### Outreach Target (16 fields)
type, status, platform, group_name, group_url, language, topic, location, member_count, posting_allowed, last_contacted, message_variant, operator_posted, operator_approved, result, risk_level, notes

### Post Queue (12 fields)
type, status, language, post_category, target, created_at, scheduled_for, operator_approved, posted_to_facebook, facebook_post_url, text, notes
