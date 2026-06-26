"""FastAPI router for the Runtime Manager Agent."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel


router = APIRouter(prefix="/api/manager", tags=["manager"])


class AnalyzeRequest(BaseModel):
    source_type: str = "manual_text"
    source_label: str = ""
    raw_text: str = ""
    author_hint: str | None = None
    operator_note: str | None = None


def _get_manager(request: Request):
    if hasattr(request.app.state, 'runtime_manager'):
        return request.app.state.runtime_manager
    raise HTTPException(status_code=503, detail="Runtime manager not initialized")


@router.post("/analyze")
def analyze(request: Request, req: AnalyzeRequest):
    manager = _get_manager(request)
    decision = manager.analyze(req.model_dump())
    return {
        "success": True,
        "llm_used": manager.llm_available,
        "decision": decision.to_queue_dict(),
    }


@router.get("/status")
def manager_status(request: Request):
    try:
        manager = _get_manager(request)
        return manager.get_status()
    except HTTPException:
        return {"llm_available": False, "error": "Manager not initialized"}
