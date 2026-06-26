---
type: architecture
task: TASK-005A
version: 0.1.0
date: 2026-06-26
status: draft
production_accepted: false
---

# Runtime Agent — Sezonski Rad Srbija

## Role

The runtime agent is a standalone business agent that operates continuously. It processes incoming market/group data, classifies content, creates structured records, generates replies and posts, manages action queues, and prepares operator-approved actions.

It is NOT a VS Code build helper. It is a Telegram bot-style business assistant for the seasonal work aggregator.

## Architecture

```
[Events] → [Brain/Classifier] → [Tool Layer] → [Action Queue] → [Operator Console]
                ↓                    ↓                ↓
           [Audit Log]         [DB Storage]    [Operator Approve/Reject/Edit]
```

## Component Map

| Component | File | Purpose |
|-----------|------|---------|
| Agent Core | agent_core.py | Event loop, orchestration |
| Config | config.py | Gates, settings, runtime flags |
| Events | events.py | Event schema, validation |
| Brain | brain.py | Content classification |
| Tools | tools.py | Database + export operations |
| Action Queue | action_queue.py | Pending/approved/executed actions |
| Policy | policy.py | Gate enforcement, safety rules |
| Memory | memory.py | Short-term context for conversations |
| Scheduler | scheduler.py | Timed tasks (digest, freshness check) |
| API | api.py | FastAPI router for runtime endpoints |
| Operator Console | operator_console.py | Console view models |
| Audit Log | audit_log.py | Immutable event processing log |

## Event Flow

1. Event arrives via API (`POST /api/runtime-agent/events`)
2. Agent core validates event
3. Brain classifies content
4. Policy checks gates
5. Tools create/update DB records
6. Action queue items are generated
7. Audit log records everything
8. Operator reviews queue, approves/rejects/edits

## Modes

### Mode 1 — Safe Draft (default, active)

- Operator pastes text manually
- Agent classifies, creates records, generates drafts
- Operator manually publishes everything
- No Facebook access at all

### Mode 2 — Assisted Own-Group (designed, disabled)

- Agent monitors operator-visible own-group content
- Drafts action queue items
- Operator approves each
- No auto-submit

### Mode 3 — Account Browser Worker (risk-managed, disabled)

- Agent uses logged-in browser session (operator's device)
- Reads visible content only
- May prepare own-group replies
- No external posting, no messaging
- Full audit, operator can kill

All modes above Mode 1 are disabled by default.
