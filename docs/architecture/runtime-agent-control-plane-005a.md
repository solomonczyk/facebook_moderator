---
type: architecture
section: control_plane
task: TASK-005A
date: 2026-06-26
---

# Runtime Agent — Control Plane

## Dangerous Gates

All gates are **disabled by default**. No gate may be enabled without explicit operator confirmation.

```yaml
facebook_account_worker_enabled: false
facebook_external_group_capture_enabled: false
facebook_own_group_capture_enabled: false
facebook_auto_reply_enabled: false
facebook_auto_post_enabled: false
facebook_auto_comment_enabled: false
facebook_auto_message_enabled: false
captcha_bypass_enabled: false
stealth_browser_enabled: false
fake_account_enabled: false
review_auto_publish_enabled: false
production_accepted: false
```

## Hard Forbidden (permanent)

```text
captcha_bypass
stealth_evasion
fake_accounts
credential_extraction
cookie_export
private_member_data_collection
fake_vacancies
fake_reviews
```

## Operator Approval Workflow

Every action goes through:

```
[Suggested by Agent] → [Queue: pending] → [Operator reviews]
                                              ↓
                              ┌───────────────┼───────────────┐
                              ↓               ↓               ↓
                          [Approve]       [Edit + Approve]  [Reject]
                              ↓               ↓               ↓
                      [Mark Executed]  [Mark Executed]   [Cancelled]
```

Default: `operator_approval_required: true` for all actions.

## Action Queue States

```
pending → approved → executed_manually
pending → edited → approved → executed_manually
pending → rejected → cancelled
pending → failed → cancelled
```

## Audit Requirements

Every event, classification, tool call, and queue state change must be logged:

```yaml
audit_entry:
  timestamp:
  event_id:
  action:
  agent_version:
  operator:
  details:
  previous_state:
  new_state:
```

Audit log is append-only. No deletions.
