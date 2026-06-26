"""Operator console view models."""

from .action_queue import ActionQueue, QueueStatus


def get_console_view(queue: ActionQueue, audit_count: int) -> dict:
    pending = queue.get_all(QueueStatus.PENDING)
    return {
        "pending_replies": len([i for i in pending if "reply" in i.action_type.value]),
        "pending_digest_drafts": len([i for i in pending if "digest" in i.action_type.value]),
        "pending_posts": len([i for i in pending if "publish" in i.action_type.value]),
        "pending_reviews": len([i for i in pending if "moderation" in i.action_type.value or "review" in i.action_type.value]),
        "total_pending": len(pending),
        "audit_log_entries": audit_count,
        "recent_pending": [
            {
                "item_id": i.item_id,
                "type": i.action_type.value,
                "preview": i.suggested_text[:100] if i.suggested_text else "",
                "created": i.created_at,
            }
            for i in pending[:10]
        ],
    }
