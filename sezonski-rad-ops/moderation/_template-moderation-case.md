---
type: moderation_case
status: new
date: {{date}}
post_type:
language: serbian
verdict:
risk_level: medium
source_text:
safe_version:
operator_decision:
operator_approved: false
escalated: false
resolved: false
notes:
---

# Moderation Case — {{date}}

## Post Info

| Field | Value |
|-------|-------|
| **Date** | `=this.date` |
| **Post Type** | `=this.post_type` |
| **Language** | `=this.language` |
| **Verdict** | `=this.verdict` |
| **Risk Level** | `=this.risk_level` |

## Original Text

```
{{source_text}}
```

## Admin Copilot Analysis

```
{{copilot_output}}
```

## Safe Version

```
{{safe_version}}
```

## Decision

```yaml
Verdict: {{verdict}}
Operator Decision: {{operator_decision}}
Approved: {{operator_approved}}
Escalated: {{escalated}}
Resolved: {{resolved}}
```

## Notes

{{notes}}

## History

| Date | Action | By |
|------|--------|----|
| {{date}} | Created | operator |
