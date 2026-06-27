"""Telegram operator API — test dispatch, webhook, status."""

import os
import json
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/telegram", tags=["telegram"])


class TestDispatchRequest(BaseModel):
    item_id: str = ""


class NotificationTestResult(BaseModel):
    item_id: str
    notification_sent: bool
    test_mode: bool
    payload_saved: bool
    payload_path: str = ""


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/test-dispatch/{item_id}")
async def test_dispatch_item(item_id: str, request: Request):
    """Test-dispatch a specific queue item notification (test mode only)."""
    agent = getattr(request.app.state, "runtime_agent", None)
    if not agent:
        raise HTTPException(status_code=503, detail="Runtime agent not initialized")

    item = agent.queue.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Queue item not found: {item_id}")

    from .notifier import send_notification, is_test_mode

    item_dict = item.to_dict()
    # Enrich with classification/risk if available from audit log
    # For now, use what's on the queue item
    sent = send_notification(item_dict)

    return {
        "item_id": item_id,
        "notification_sent": sent,
        "test_mode": is_test_mode(),
        "action_type": item_dict.get("action_type"),
        "status": item_dict.get("status"),
    }


@router.get("/status")
async def telegram_status(request: Request):
    """Get Telegram integration status."""
    from .notifier import is_test_mode, is_available, get_test_payloads

    agent = getattr(request.app.state, "runtime_agent", None)
    queue_pending = agent.queue.get_pending_count() if agent else 0

    test_mode = is_test_mode()
    available = is_available()

    return {
        "telegram_available": available,
        "test_mode": test_mode,
        "bot_token_configured": bool(os.getenv("TELEGRAM_BOT_TOKEN", "")),
        "operator_chat_id_configured": bool(os.getenv("TELEGRAM_OPERATOR_CHAT_ID", "")),
        "queue_pending": queue_pending,
        "test_payloads_count": len(get_test_payloads()) if test_mode else 0,
        "production_accepted": False,
        "last_check": datetime.utcnow().isoformat(),
    }
