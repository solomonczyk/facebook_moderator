---
type: worker
status: new
date_added: {{date}}
source:
name_optional:
contact_public:
contact_private:
location:
desired_job_type:
experience:
available_from:
needs_accommodation: false
can_travel: false
alone_pair_group: alone
languages:
  - serbian
risk_level: low
posted_to_group: false
operator_approved: false
notes:
---

# Worker — {{name_optional}} ({{location}})

## Profile

| Field | Value |
|-------|-------|
| **Name** | `=this.name_optional` |
| **Location** | `=this.location` |
| **Desired Job** | `=this.desired_job_type` |
| **Experience** | `=this.experience` |
| **Available From** | `=this.available_from` |
| **Needs Accommodation** | `=this.needs_accommodation` |
| **Can Travel** | `=this.can_travel` |
| **Alone / Pair / Group** | `=this.alone_pair_group` |
| **Languages** | `=this.languages` |
| **Contact (Public)** | `=this.contact_public` |

## Source

- **Source:** `=this.source`

## Status

```yaml
Status: {{status}}
Risk Level: {{risk_level}}
Operator Approved: {{operator_approved}}
Posted to Group: {{posted_to_group}}
```

## Notes

{{notes}}

## History

| Date | Action | By |
|------|--------|----|
| {{date}} | Created | operator |
