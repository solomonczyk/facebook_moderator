"""FastAPI router for the account worker."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..aggregator_api.database import get_db
from .worker_service import WorkerService

router = APIRouter(prefix="/api/account-worker", tags=["account-worker"])

_worker_service: WorkerService | None = None


def get_worker(db: Session = Depends(get_db)) -> WorkerService:
    global _worker_service
    if _worker_service is None:
        _worker_service = WorkerService(db)
    return _worker_service


class EmergencyStopRequest(BaseModel):
    reason: str = "Operator requested emergency stop"


@router.get("/status")
def status(worker: WorkerService = Depends(get_worker)):
    return worker.get_status()


@router.post("/start")
def start(worker: WorkerService = Depends(get_worker)):
    ok, msg = worker.start()
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}


@router.post("/stop")
def stop(worker: WorkerService = Depends(get_worker)):
    worker.stop()
    return {"success": True, "message": "Worker stopped"}


@router.post("/pause")
def pause(worker: WorkerService = Depends(get_worker)):
    worker.pause()
    return {"success": True, "message": "Worker paused"}


@router.post("/resume")
def resume(worker: WorkerService = Depends(get_worker)):
    worker.resume()
    return {"success": True, "message": "Worker resumed"}


@router.post("/emergency-stop")
def emergency_stop(req: EmergencyStopRequest, worker: WorkerService = Depends(get_worker)):
    worker.emergency_stop(req.reason)
    return {"success": True, "message": "Emergency stop triggered"}


@router.post("/run-once")
def run_once(dry_run: bool = False, worker: WorkerService = Depends(get_worker)):
    result = worker.watcher.run_once(dry_run=dry_run)
    return {
        "run_id": result.run_id,
        "items_seen": result.items_seen,
        "items_new": result.items_new,
        "items_sent": result.items_sent,
        "errors": result.errors,
        "dry_run": dry_run,
        "state": result.state.value,
    }
