"""Structured intake API — employer offer and worker search endpoints."""

import logging
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

logger = logging.getLogger("sezonski.structured_api")

router = APIRouter(prefix="/api/intake", tags=["structured-intake"])


# ── Request Schemas ──────────────────────────────────────────────────────────

class EmployerOfferRequest(BaseModel):
    employer_name: str = ""
    work_location: str = ""
    job_type: str = ""
    workers_needed: str = ""
    start_date: str = ""
    pay_amount: str = ""
    pay_type: str = ""
    working_hours_or_norm: str = ""
    housing_provided: str = ""
    food_provided: str = ""
    payment_frequency: str = ""
    contact: str = ""
    # Optional
    transport: str = ""
    experience_required: str = ""
    gender_or_age_constraints: str = ""
    additional_info: str = ""
    source_url: str = ""
    source_group: str = ""
    language: str = "sr"


class WorkerSearchRequest(BaseModel):
    worker_name: str = ""
    current_location: str = ""
    people_count: str = ""
    desired_job_type: str = ""
    available_from: str = ""
    housing_needed: str = ""
    food_needed: str = ""
    contact: str = ""
    # Optional
    experience: str = ""
    languages: str = ""
    has_transport: str = ""
    preferred_location: str = ""
    additional_info: str = ""
    source_url: str = ""
    source_group: str = ""
    language: str = "sr"


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/employer-offer")
async def intake_employer_offer(req: EmployerOfferRequest, request: Request):
    """Accept structured employer offer → validate → queue → notify."""
    from .structured_intake import EmployerOfferIntake, process_employer_offer

    offer = EmployerOfferIntake(
        employer_name=req.employer_name,
        work_location=req.work_location,
        job_type=req.job_type,
        workers_needed=req.workers_needed,
        start_date=req.start_date,
        pay_amount=req.pay_amount,
        pay_type=req.pay_type,
        working_hours_or_norm=req.working_hours_or_norm,
        housing_provided=req.housing_provided,
        food_provided=req.food_provided,
        payment_frequency=req.payment_frequency,
        contact=req.contact,
        transport=req.transport,
        experience_required=req.experience_required,
        gender_or_age_constraints=req.gender_or_age_constraints,
        additional_info=req.additional_info,
        source_url=req.source_url,
        source_group=req.source_group,
        language=req.language,
    )

    result = process_employer_offer(offer)

    # Add to runtime agent queue if available
    _add_to_runtime_queue(request, result)

    # Send Telegram notification
    _notify_telegram(result)

    return {
        "lead_id": result["lead_id"],
        "item_id": result["item_id"],
        "status": result["status"],
        "action_type": result["action_type"],
        "classification": result["classification"],
        "risk_level": result["risk_level"],
        "completeness": offer.completeness(),
        "missing_fields": result["missing_info"],
        "operator_approval_required": True,
    }


@router.post("/worker-search")
async def intake_worker_search(req: WorkerSearchRequest, request: Request):
    """Accept structured worker search → validate → queue → notify."""
    from .structured_intake import WorkerSearchIntake, process_worker_search

    worker = WorkerSearchIntake(
        worker_name=req.worker_name,
        current_location=req.current_location,
        people_count=req.people_count,
        desired_job_type=req.desired_job_type,
        available_from=req.available_from,
        housing_needed=req.housing_needed,
        food_needed=req.food_needed,
        contact=req.contact,
        experience=req.experience,
        languages=req.languages,
        has_transport=req.has_transport,
        preferred_location=req.preferred_location,
        additional_info=req.additional_info,
        source_url=req.source_url,
        source_group=req.source_group,
        language=req.language,
    )

    result = process_worker_search(worker)

    _add_to_runtime_queue(request, result)
    _notify_telegram(result)

    return {
        "lead_id": result["lead_id"],
        "item_id": result["item_id"],
        "status": result["status"],
        "action_type": result["action_type"],
        "classification": result["classification"],
        "risk_level": result["risk_level"],
        "completeness": worker.completeness(),
        "missing_fields": result["missing_info"],
        "operator_approval_required": True,
    }


# ── Helpers ──────────────────────────────────────────────────────────────────

def _add_to_runtime_queue(request: Request, result: dict):
    """Add item to runtime agent queue if available."""
    try:
        agent = getattr(request.app.state, "runtime_agent", None)
        if agent:
            from ..runtime_agent.action_queue import QueueItem, ActionType

            atype_map = {
                "publish_own_group_post": ActionType.PUBLISH_OWN_GROUP_POST,
                "ask_for_missing_info": ActionType.ASK_FOR_MISSING_INFO,
                "request_operator_review": ActionType.REQUEST_OPERATOR_REVIEW,
            }
            item = QueueItem(
                item_id=result["item_id"],
                action_type=atype_map.get(result["action_type"], ActionType.REQUEST_OPERATOR_REVIEW),
                suggested_text=result.get("suggested_text", ""),
                reason=result.get("reason", ""),
                operator_approval_required=True,
            )
            agent.queue.add(item)
            logger.info(f"Added to runtime queue: {result['item_id']}")
    except Exception as e:
        logger.warning(f"Could not add to runtime queue: {e}")


def _notify_telegram(result: dict):
    """Send Telegram notification for the intake result."""
    try:
        from ..telegram_bot.notifier import send_notification
        send_notification(result)
    except Exception as e:
        logger.warning(f"Telegram notification failed: {e}")
