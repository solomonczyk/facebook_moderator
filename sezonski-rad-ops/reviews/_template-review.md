---
type: review
status: new
date_added: {{date}}
source:
reviewer_language: serbian
location:
employer_name_optional:
job_type:
work_period:
promised_conditions:
actual_conditions:
pay_received:
pay_on_time:
accommodation_rating:
food_rating:
treatment_rating:
work_conditions_rating:
overall_rating:
would_recommend:
contains_personal_data: false
contains_insults: false
legal_risk: medium
risk_level: medium
safe_version_created: false
operator_approved: false
posted_to_group: false
facebook_post_url:
safe_version_text:
notes:
---

# Review — {{employer_name_optional}} ({{location}})

## Review Summary

| Field | Value |
|-------|-------|
| **Reviewer Language** | `=this.reviewer_language` |
| **Location** | `=this.location` |
| **Employer** | `=this.employer_name_optional` |
| **Job Type** | `=this.job_type` |
| **Work Period** | `=this.work_period` |

## Conditions

| Field | Promised | Actual |
|-------|----------|--------|
| **Pay** | | `=this.pay_received` |
| **On Time** | | `=this.pay_on_time` |
| **Accommodation** | | ⭐ `=this.accommodation_rating` |
| **Food** | | ⭐ `=this.food_rating` |
| **Treatment** | | ⭐ `=this.treatment_rating` |
| **Work Conditions** | | ⭐ `=this.work_conditions_rating` |

## Ratings

| Dimension | Rating (1–5) |
|-----------|-------------|
| Accommodation | `=this.accommodation_rating` |
| Food | `=this.food_rating` |
| Treatment | `=this.treatment_rating` |
| Work Conditions | `=this.work_conditions_rating` |
| **Overall** | **`=this.overall_rating`** |

**Would Recommend:** `=this.would_recommend`

## Safety Check

- [ ] Contains personal data: `=this.contains_personal_data`
- [ ] Contains insults: `=this.contains_insults`
- [ ] Legal risk: `=this.legal_risk`
- [ ] Safe version created: `=this.safe_version_created`

## Status

```yaml
Status: {{status}}
Risk Level: {{risk_level}}
Safe Version: {{safe_version_created}}
Operator Approved: {{operator_approved}}
Posted to Group: {{posted_to_group}}
Facebook URL: {{facebook_post_url}}
```

## Safe Version

`=this.safe_version_text`

## Original Text

## Notes

{{notes}}

## History

| Date | Action | By |
|------|--------|----|
| {{date}} | Created | operator |
