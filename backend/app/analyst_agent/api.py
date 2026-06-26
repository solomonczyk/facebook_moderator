"""FastAPI router for the analyst agent."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/analyst", tags=["analyst"])


class AnalystRunRequest(BaseModel):
    max_items: int = 10


class QueueItemRequest(BaseModel):
    item_id: str = ""
    action_type: str = ""
    suggested_text: str = ""
    event_id: str | None = None


def _get_analyst(request: Request):
    """Get shared analyst agent from app state."""
    if hasattr(request.app.state, 'analyst_agent'):
        return request.app.state.analyst_agent
    raise HTTPException(status_code=503, detail="Analyst agent not initialized")


@router.get("/status")
def status(request: Request):
    try:
        analyst = _get_analyst(request)
        return analyst.get_status()
    except HTTPException:
        return {"analyst_enabled": False, "error": "Not initialized"}


@router.post("/process-queue")
def process_queue(request: Request, req: AnalystRunRequest | None = None):
    analyst = _get_analyst(request)
    if not analyst.enabled:
        raise HTTPException(status_code=400, detail="Analyst is disabled")
    result = analyst.process_pending_queue()
    return result


@router.post("/analyze-item")
def analyze_item(request: Request, item: QueueItemRequest):
    analyst = _get_analyst(request)
    if not analyst.enabled:
        raise HTTPException(status_code=400, detail="Analyst is disabled")
    result = analyst.process_queue_item(item.model_dump())
    return result


@router.post("/kill-switch")
def kill_switch(request: Request):
    analyst = _get_analyst(request)
    analyst.config.analyst_enabled = False
    analyst.config.autonomous_mode_enabled = False
    return {"success": True, "message": "Analyst kill switch activated. Autonomous mode disabled."}


@router.get("/audit")
def audit_log(request: Request):
    analyst = _get_analyst(request)
    entries = analyst.audit.recent(30)
    return {
        "entries": [
            {
                "timestamp": e.timestamp,
                "decision_id": e.decision_id,
                "action": e.action,
                "risk_level": e.risk_level,
                "confidence": e.confidence,
                "executed": e.executed,
                "escalated": e.escalated,
            }
            for e in entries
        ],
        "summary": analyst.audit.get_summary(),
    }
