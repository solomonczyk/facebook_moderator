---
type: post
status: draft
language: serbian
post_category:
target:
created_at: {{date}}
scheduled_for:
operator_approved: false
posted_to_facebook: false
facebook_post_url:
text:
notes:
---

# Post — {{post_category}}

## Meta

| Field | Value |
|-------|-------|
| **Status** | `=this.status` |
| **Category** | `=this.post_category` |
| **Language** | `=this.language` |
| **Target** | `=this.target` |
| **Created** | `=this.created_at` |
| **Scheduled** | `=this.scheduled_for` |

## Text

```
{{text}}
```

## Publication Gates

- [ ] Admin Copilot review completed
- [ ] Safe version created (if needed)
- [ ] `operator_approved: true`
- [ ] Posted to Facebook manually
- [ ] `facebook_post_url` added

## Facebook URL

`=this.facebook_post_url`

## Notes

{{notes}}
