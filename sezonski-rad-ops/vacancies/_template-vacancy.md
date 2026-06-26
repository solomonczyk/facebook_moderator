---
type: vacancy
status: new
source: unknown
source_url:
facebook_post_url:
date_added: {{date}}
last_checked: {{date}}
location:
job_type:
employer_name:
contact_public:
contact_private:
start_date:
workers_needed:
pay_amount:
pay_type:
pay_frequency:
working_hours:
accommodation:
food:
transport:
registered_work:
languages:
  - serbian
risk_level: medium
verified_by_operator: false
posted_to_group: false
operator_approved: false
notes:
---

# {{employer_name}} — {{job_type}} ({{location}})

## Vacancy Details

| Field | Value |
|-------|-------|
| **Location** | `=this.location` |
| **Job Type** | `=this.job_type` |
| **Employer** | `=this.employer_name` |
| **Start Date** | `=this.start_date` |
| **Workers Needed** | `=this.workers_needed` |
| **Pay** | `=this.pay_amount` `=this.pay_type` / `=this.pay_frequency` |
| **Working Hours** | `=this.working_hours` |
| **Accommodation** | `=this.accommodation` |
| **Food** | `=this.food` |
| **Transport** | `=this.transport` |
| **Registered Work** | `=this.registered_work` |
| **Contact** | `=this.contact_public` |
| **Languages** | `=this.languages` |

## Source

- **Source:** `=this.source`
- **URL:** `=this.source_url`

## Status

```yaml
Status: {{status}}
Risk Level: {{risk_level}}
Verified: {{verified_by_operator}}
Operator Approved: {{operator_approved}}
Posted to Group: {{posted_to_group}}
Facebook URL: {{facebook_post_url}}
```

## Required Fields Check

- [ ] Mesto rada / grad
- [ ] Vrsta posla
- [ ] Kada posao počinje
- [ ] Koliko radnika je potrebno
- [ ] Plata
- [ ] Način isplate
- [ ] Radno vreme
- [ ] Smeštaj: da/ne
- [ ] Hrana: da/ne
- [ ] Prevoz: da/ne / po dogovoru
- [ ] Kontakt telefon / Viber / WhatsApp
- [ ] Da li je radnik prijavljen

## Notes

{{notes}}

## History

| Date | Action | By |
|------|--------|----|
| {{date}} | Created | operator |
