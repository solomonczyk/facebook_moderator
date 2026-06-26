---
type: architecture
task: TASK-005B
version: 0.1.0
date: 2026-06-26
status: draft
production_accepted: false
---

# Local Facebook Runtime Intake — MVP

## Goal

Connect the TASK 005A runtime agent to real incoming Facebook content via local intake adapters. Reduce manual operator work.

## Intake Modes

| Mode | Description | Default |
|------|-------------|---------|
| A — Manual Paste | Operator pastes text into API | ✅ Enabled |
| B — Clipboard Intake | Local watcher processes copied FB text | ✅ Enabled |
| C — Browser Selected Text | Extension captures user-selected text | ✅ Enabled |
| D — Own Group Visible | Reads visible viewport of own FB group | ❌ Disabled |

## Architecture

```
[Facebook Tab] → [Browser Extension] → [Clipboard / Selection]
       ↓                                        ↓
[Manual Paste] → [Intake API] → [Event Mapper] → [Runtime Agent]
                                                    ↓
                                            [Action Queue]
                                                    ↓
                                            [Operator Console]
```

## Dangerous Gates (all disabled by default)

```yaml
manual_paste_enabled: true
clipboard_intake_enabled: true
selected_text_extension_enabled: true
own_group_visible_intake_enabled: false
external_group_visible_intake_enabled: false
facebook_account_worker_enabled: false
auto_reply_enabled: false
auto_post_enabled: false
auto_comment_enabled: false
auto_message_enabled: false
```
