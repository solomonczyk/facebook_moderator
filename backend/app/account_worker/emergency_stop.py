"""Emergency stop: in-memory flag to immediately halt the worker."""

from datetime import datetime


class EmergencyStop:
    def __init__(self):
        self._stopped: bool = False
        self._stopped_at: str | None = None
        self._reason: str = ""

    @property
    def is_stopped(self) -> bool:
        return self._stopped

    def trigger(self, reason: str = "Operator requested emergency stop") -> None:
        self._stopped = True
        self._stopped_at = datetime.utcnow().isoformat()
        self._reason = reason

    def reset(self) -> None:
        self._stopped = False
        self._stopped_at = None
        self._reason = ""

    def check(self) -> None:
        """Check if emergency stop was triggered. Raises if so."""
        if self._stopped:
            raise WorkerEmergencyStopped(self._reason or "Emergency stop active")

    def to_dict(self) -> dict:
        return {
            "emergency_stopped": self._stopped,
            "stopped_at": self._stopped_at,
            "reason": self._reason,
        }


class WorkerEmergencyStopped(Exception):
    pass
