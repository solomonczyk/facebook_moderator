---
type: audit
task: TASK-006C
section: telegram_callbacks
date: 2026-06-26
---

# Telegram Callback Tests — Runtime Analyst v1

## Button Actions

| Button | Callback Data | Queue Status After | Audit Entry |
|--------|--------------|-------------------|-------------|
| ✅ Approve | approve:{id} | approved | telegram_approve |
| ❌ Reject | reject:{id} | rejected | telegram_reject |
| ✅ Executed | mark_executed:{id} | executed_manually | telegram_executed |
| ❓ Needs Info | needs_info:{id} | needs_info | telegram_needs_info |
| 🚫 Spam | mark_spam:{id} | spam | telegram_spam |
| 📋 Duplicate | mark_duplicate:{id} | duplicate | telegram_marked_duplicate |
| 🔒 Closed | mark_closed:{id} | closed | telegram_closed |

## Queue Display

- /queue shows only PENDING items
- Processed items (approved, rejected, executed, closed, spam, duplicate, needs_info) are NOT shown in /queue
- Audit log records old_status -> new_status for every transition
