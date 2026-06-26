"""FastAPI router for the runtime agent."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..aggregator_api.database import get_db, init_db
from .agent_core import RuntimeAgent
from .events import RuntimeEvent, EventType, CaptureMethod
from .action_queue import QueueStatus
from .operator_console import get_console_view

router = APIRouter(prefix="/api/runtime-agent", tags=["runtime-agent"])

# Global agent instance (in production, use dependency injection)
_agent: RuntimeAgent | None = None


def get_agent(db: Session = Depends(get_db)) -> RuntimeAgent:
    global _agent
    # Use shared agent from app.state if available
    from fastapi import Request
    try:
        from ..aggregator_api.main import app as main_app
        if hasattr(main_app.state, 'runtime_agent') and main_app.state.runtime_agent is not None:
            return main_app.state.runtime_agent
    except Exception:
        pass
    if _agent is None or _agent.tools.db != db:
        _agent = RuntimeAgent(db)
    return _agent


# ── Schemas ─────────────────────────────────────────────────────────────────

class EventRequest(BaseModel):
    event_type: str = "manual_operator_entry"
    source_type: str = "manual_operator_entry"
    source_name: str = ""
    source_group: str | None = None
    author_display_name: str = ""
    raw_text: str = ""
    capture_method: str = "manual_paste"
    operator: str = ""


class QueueActionRequest(BaseModel):
    operator: str = ""
    reason: str = ""
    edited_text: str | None = None


# ── Endpoints ───────────────────────────────────────────────────────────────

@router.post("/events")
def process_event(request: EventRequest, agent: RuntimeAgent = Depends(get_agent)):
    event = RuntimeEvent(
        event_type=EventType(request.event_type) if request.event_type in [e.value for e in EventType] else EventType.MANUAL_OPERATOR_ENTRY,
        source_type=request.source_type,
        source_name=request.source_name,
        source_group=request.source_group,
        author_display_name=request.author_display_name,
        raw_text=request.raw_text,
        capture_method=CaptureMethod(request.capture_method) if request.capture_method in [c.value for c in CaptureMethod] else CaptureMethod.MANUAL_PASTE,
        operator=request.operator,
    )
    result = agent.process_event(event)
    return result


@router.get("/queue")
def list_queue(status: str | None = None, agent: RuntimeAgent = Depends(get_agent)):
    qs = None
    if status:
        try:
            qs = QueueStatus(status)
        except ValueError:
            pass
    items = agent.queue.get_all(qs)
    return {"items": [i.to_dict() for i in items], "count": len(items)}


@router.get("/queue/{item_id}")
def get_queue_item(item_id: str, agent: RuntimeAgent = Depends(get_agent)):
    item = agent.queue.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Queue item not found")
    return item.to_dict()


@router.post("/queue/{item_id}/approve")
def approve_item(item_id: str, req: QueueActionRequest, agent: RuntimeAgent = Depends(get_agent)):
    item = agent.queue.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Queue item not found")
    item.approve(req.operator)
    agent.audit.record("queue_approved", f"Item: {item_id}", operator=req.operator, previous_state="pending", new_state="approved")
    return item.to_dict()


@router.post("/queue/{item_id}/reject")
def reject_item(item_id: str, req: QueueActionRequest, agent: RuntimeAgent = Depends(get_agent)):
    item = agent.queue.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Queue item not found")
    item.reject(req.reason, req.operator)
    agent.audit.record("queue_rejected", f"Item: {item_id}, Reason: {req.reason}", operator=req.operator, previous_state="pending", new_state="rejected")
    return item.to_dict()


@router.post("/queue/{item_id}/edit")
def edit_item(item_id: str, req: QueueActionRequest, agent: RuntimeAgent = Depends(get_agent)):
    item = agent.queue.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Queue item not found")
    if not req.edited_text:
        raise HTTPException(status_code=400, detail="edited_text is required")
    item.edit(req.edited_text, req.operator)
    agent.audit.record("queue_edited", f"Item: {item_id}", operator=req.operator, previous_state="pending", new_state="edited")
    return item.to_dict()


@router.post("/queue/{item_id}/mark-executed")
def mark_executed(item_id: str, req: QueueActionRequest, agent: RuntimeAgent = Depends(get_agent)):
    item = agent.queue.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Queue item not found")
    item.mark_executed(req.operator)
    agent.audit.record("queue_executed", f"Item: {item_id}", operator=req.operator, previous_state="approved", new_state="executed_manually")
    return item.to_dict()


@router.get("/status")
def agent_status(agent: RuntimeAgent = Depends(get_agent)):
    status = agent.get_status()
    status["console"] = get_console_view(agent.queue, agent.audit.count)
    return status


@router.post("/digest/run")
def run_digest(agent: RuntimeAgent = Depends(get_agent)):
    result = agent.run_daily_digest()
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("reason", "Digest run failed"))
    return result
