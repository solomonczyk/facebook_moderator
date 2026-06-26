"""FastAPI router for runtime intake endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..aggregator_api.database import get_db
from .intake_models import (
    ManualPasteRequest, BrowserSelectionRequest, ClipboardRequest,
    VisibleGroupRequest, IntakeResponse,
)
from .event_mapper import (
    manual_paste_to_event, browser_selection_to_event,
    clipboard_to_event, visible_group_to_event,
)
from .intake_service import IntakeService
from .config import IntakeConfig

router = APIRouter(prefix="/api/runtime-intake", tags=["runtime-intake"])

_intake_service: IntakeService | None = None


def get_intake(db: Session = Depends(get_db)) -> IntakeService:
    global _intake_service
    # Use shared service from app.state if available
    try:
        from ..aggregator_api.main import app as main_app
        if hasattr(main_app.state, 'intake_service') and main_app.state.intake_service is not None:
            return main_app.state.intake_service
    except Exception:
        pass
    if _intake_service is None:
        _intake_service = IntakeService(db)
    return _intake_service


# ── Pydantic Schemas ────────────────────────────────────────────────────────

class ManualPasteSchema(BaseModel):
    source_type: str = "operator_pasted_text"
    source_name: str = "Facebook"
    source_group: str = ""
    source_url: str | None = None
    raw_text: str = ""
    operator: str = ""


class BrowserSelectionSchema(BaseModel):
    capture_method: str = "browser_extension_visible_selection"
    page_url: str = ""
    page_title: str = ""
    selected_text: str = ""
    source_group: str = ""
    captured_at: str | None = None
    operator: str = ""


class ClipboardSchema(BaseModel):
    capture_method: str = "clipboard_intake"
    raw_text: str = ""
    operator: str = ""


class VisibleGroupSchema(BaseModel):
    capture_method: str = "own_group_visible_intake"
    page_url: str = ""
    source_group: str = ""
    visible_text_blocks: list[str] = []
    operator: str = ""


# ── Endpoints ───────────────────────────────────────────────────────────────

@router.post("/manual-paste")
def manual_paste(req: ManualPasteSchema, intake: IntakeService = Depends(get_intake)):
    mapped = manual_paste_to_event(req)
    result = intake.process_event(mapped)
    return result.to_dict()


@router.post("/browser-selection")
def browser_selection(req: BrowserSelectionSchema, intake: IntakeService = Depends(get_intake)):
    mapped = browser_selection_to_event(req)
    result = intake.process_event(mapped)
    return result.to_dict()


@router.post("/clipboard")
def clipboard(req: ClipboardSchema, intake: IntakeService = Depends(get_intake)):
    mapped = clipboard_to_event(req)
    result = intake.process_event(mapped)
    return result.to_dict()


@router.post("/visible-group")
def visible_group(req: VisibleGroupSchema, intake: IntakeService = Depends(get_intake)):
    events = visible_group_to_event(req)
    results = intake.process_visible_group(events)
    return {"responses": [r.to_dict() for r in results], "count": len(results)}


@router.get("/status")
def intake_status(intake: IntakeService = Depends(get_intake)):
    return intake.get_status()
