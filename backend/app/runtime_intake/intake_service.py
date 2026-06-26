"""Intake service: processes incoming content and routes to runtime agent."""

from sqlalchemy.orm import Session

from ..runtime_agent.agent_core import RuntimeAgent
from ..runtime_agent.events import RuntimeEvent
from .config import IntakeConfig
from .intake_models import IntakeResponse


class IntakeService:
    def __init__(self, db: Session, config: IntakeConfig | None = None):
        self.config = config or IntakeConfig()
        self._agent: RuntimeAgent | None = None
        self._db = db

    @property
    def agent(self) -> RuntimeAgent:
        if self._agent is None:
            self._agent = RuntimeAgent(self._db)
        return self._agent

    def process_event(self, event: RuntimeEvent) -> IntakeResponse:
        if not self.config.manual_paste_enabled:
            return IntakeResponse(False, errors=["Manual paste intake is disabled"])

        result = self.agent.process_event(event)
        if not result.get("success"):
            return IntakeResponse(False, errors=result.get("errors", ["Processing failed"]))

        return IntakeResponse(
            success=True,
            event_id=result.get("event_id"),
            classification=result.get("classification", ""),
            queue_item_id=result.get("queue_item_id"),
            suggested_reply=result.get("suggested_reply", ""),
            action=result.get("action", "operator_review"),
        )

    def process_visible_group(self, events: list[RuntimeEvent]) -> list[IntakeResponse]:
        if not self.config.own_group_visible_intake_enabled:
            return [IntakeResponse(False, errors=["Own group visible intake is disabled"])]
        return [self.process_event(e) for e in events]

    def get_status(self) -> dict:
        return {
            "config": self.config.to_dict(),
            "agent_status": self.agent.get_status(),
        }
