---
type: operator_guide
task: TASK-005C
date: 2026-06-26
---

# How to Run — Account Worker

## Prerequisites

- Backend running on localhost:8000
- Chrome/Firefox installed
- Operator logged into Facebook manually in visible browser

## Start

```bash
# Configure group URL
export OWN_FACEBOOK_GROUP_URL="https://www.facebook.com/groups/992369183697618"

# Start worker
curl -X POST http://localhost:8000/api/account-worker/start
```

## Monitor

```bash
curl http://localhost:8000/api/account-worker/status
```

## Stop / Pause

```bash
curl -X POST http://localhost:8000/api/account-worker/stop
curl -X POST http://localhost:8000/api/account-worker/pause
```

## Emergency

```bash
curl -X POST http://localhost:8000/api/account-worker/emergency-stop
```

## What to expect

- Worker opens own group in visible browser tab
- Reads visible posts/comments
- Sends new content to runtime agent
- Runtime agent classifies → creates queue items
- Operator reviews queue, approves/rejects
- Operator manually posts any approved content

No auto-posting. No auto-commenting. No auto-messaging.
