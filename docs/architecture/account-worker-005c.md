---
type: architecture
task: TASK-005C
version: 0.1.0
date: 2026-06-26
status: prototype
production_accepted: false
---

# Account Worker — Own Group Watcher

## Role

First autonomous runtime worker for the operator's own Facebook group.
Reads visible content, sends to runtime agent, creates action queue items.
Never posts, comments, or messages.

## Architecture

```
[Visible Browser] → [Content Extractor] → [Seen Store] → [Event Sender]
       ↓                                               ↓
[Rate Limiter]                              [Runtime Agent API]
       ↓                                               ↓
[Emergency Stop]                              [Action Queue]
```

## Rules

- Visible browser only — operator logs in manually
- Own group only — external groups rejected
- Read-only — no Facebook submission
- Draft-only — operator must approve all actions
- Rate-limited — max 3 runs/hour, 20 items/run, 2 scrolls/run
- Emergency stop — in-memory flag, operator can trigger anytime

## Gates (all must pass for worker to start)

```yaml
own_group_worker_enabled: true
own_group_url_configured: true
auto_post_enabled: false
auto_comment_enabled: false
auto_message_enabled: false
captcha_bypass_enabled: false
stealth_browser_enabled: false
fake_account_enabled: false
```
