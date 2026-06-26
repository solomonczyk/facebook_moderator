---
type: architecture
section: operator_approval
task: TASK-005A
date: 2026-06-26
---

# Operator Approval Workflow

## Principle

**The agent suggests. The operator decides.**

Every action that affects the group, publishes content, or contacts a person requires operator approval.

## Action Types and Approval Requirements

| Action | Approval Required? | Can Agent Auto-Execute? |
|--------|-------------------|------------------------|
| Create JobLead in DB | No | Yes (internal only) |
| Create WorkerProfile in DB | No | Yes (internal only) |
| Create EmployerProfile in DB | No | Yes (internal only) |
| Classify content | No | Yes |
| Generate draft reply | No | Yes |
| Generate draft post | No | Yes |
| Create action queue item | No | Yes |
| Publish reply to own group | **YES** | No |
| Publish post to own group | **YES** | No |
| Send message to employer | **YES** | No |
| Send message to worker | **YES** | No |
| Publish review | **YES** | No |
| Mark lead as verified | **YES** | No |
| Mark employer as verified | **YES** | No |
| Post to external group | **YES** | No (forbidden by default) |
| Ban/remove member | **YES** | No (operator only) |

## Queue Review Flow

1. Operator opens queue: `GET /api/runtime-agent/queue`
2. Operator reviews pending items
3. For each item:
   - **Approve**: `POST /queue/{id}/approve` → status: approved
   - **Edit + Approve**: `POST /queue/{id}/edit` with updated text → status: approved
   - **Reject**: `POST /queue/{id}/reject` → status: rejected
4. After manual execution: `POST /queue/{id}/mark-executed` → status: executed_manually

## Console View

The operator console shows:
- Pending replies (count)
- Pending digest drafts (count)
- New workers today (count)
- New employers today (count)
- High-risk leads (count)
- Needs clarification (count)
- Freshness alerts (leads older than 7 days still open)
