---
type: employer
status: new
date_added: {{date}}
employer_name:
company_name:
location:
contact_public:
contact_private:
industry:
typical_jobs:
typical_seasons:
languages:
  - serbian
total_reviews: 0
average_rating:
verified_by_operator: false
risk_level: medium
notes:
---

# Employer — {{employer_name}} / {{company_name}}

## Profile

| Field | Value |
|-------|-------|
| **Employer Name** | `=this.employer_name` |
| **Company** | `=this.company_name` |
| **Location** | `=this.location` |
| **Industry** | `=this.industry` |
| **Typical Jobs** | `=this.typical_jobs` |
| **Seasons** | `=this.typical_seasons` |
| **Languages** | `=this.languages` |
| **Contact (Public)** | `=this.contact_public` |

## Reviews Summary

| Metric | Value |
|--------|-------|
| Total Reviews | `=this.total_reviews` |
| Average Rating | `=this.average_rating` |

```dataview
TABLE
  overall_rating,
  would_recommend,
  date_added
FROM "reviews"
WHERE employer_name_optional = this.employer_name
SORT date_added DESC
```

## Status

```yaml
Status: {{status}}
Verified: {{verified_by_operator}}
Risk Level: {{risk_level}}
```

## Notes

{{notes}}

## History

| Date | Action | By |
|------|--------|----|
| {{date}} | Created | operator |
