"""Runtime agent core: orchestrates event processing pipeline."""

from sqlalchemy.orm import Session

from .config import RuntimeConfig
from .events import RuntimeEvent, validate_event
from .brain import classify, ContentClass
from .tools import AgentTools
from .action_queue import ActionQueue, QueueItem, ActionType, QueueStatus
from .policy import PolicyEngine
from .audit_log import AuditLog
from .memory import AgentMemory
from .scheduler import TaskScheduler


class RuntimeAgent:
    def __init__(self, db: Session):
        self.config = RuntimeConfig()
        self.tools = AgentTools(db)
        self.queue = ActionQueue()
        self.policy = PolicyEngine(self.config)
        self.audit = AuditLog()
        self.memory = AgentMemory()
        self.scheduler = TaskScheduler()

    def process_event(self, event: RuntimeEvent) -> dict:
        """Main event processing pipeline."""
        # 1. Validate
        errors = validate_event(event)
        if errors:
            self.audit.record("event_rejected", f"Validation: {', '.join(errors)}", event.event_id)
            return {"success": False, "errors": errors}

        self.audit.record("event_received", f"Type: {event.event_type.value}", event.event_id)

        # 2. Classify
        classification = classify(event.raw_text, event.source_group or "")
        self.audit.record(
            "content_classified",
            f"Class: {classification.classification.value}, confidence: {classification.confidence}",
            event.event_id,
        )

        # 3. Store in memory
        self.memory.remember(event.event_id, {
            "raw_text": event.raw_text[:200],
            "classification": classification.classification.value,
            "source": event.source_name,
        })

        # 4. Execute record actions
        for action in classification.record_actions:
            allowed, reason = self.policy.validate_action(action)
            if not allowed:
                self.audit.record("action_blocked", reason, event.event_id)
                continue

            if action == "create_job_lead":
                self.tools.create_job_lead({
                    "source_type": event.source_type,
                    "source_name": event.source_name,
                    "source_group": event.source_group,
                    "raw_text": event.raw_text,
                    "location": classification.extracted_entities.get("locations", [None])[0] if classification.extracted_entities.get("locations") else None,
                    "job_type": "sezonski rad",
                    "contact_phone": _extract_phone(event.raw_text),
                    "accommodation": classification.extracted_entities.get("accommodation"),
                    "food": classification.extracted_entities.get("food"),
                })
                self.audit.record("job_lead_created", "", event.event_id)

            if action == "create_worker_profile":
                self.tools.create_worker_profile(classification.extracted_entities)
                self.audit.record("worker_profile_created", "", event.event_id)

            if action == "create_employer_profile":
                self.tools.create_employer_profile(classification.extracted_entities)
                self.audit.record("employer_profile_created", "", event.event_id)

        # 5. Create action queue item
        if classification.recommended_action != "none":
            queue_item = QueueItem(
                action_type=self._map_action(classification.recommended_action),
                event_id=event.event_id,
                suggested_text=classification.suggested_reply or classification.suggested_public_post,
                operator_approval_required=classification.operator_approval_required,
            )
            self.queue.add(queue_item)
            self.audit.record(
                "queue_item_created",
                f"Action: {queue_item.action_type.value}, ID: {queue_item.item_id}",
                event.event_id,
            )

        # 6. Return processing result
        return {
            "success": True,
            "event_id": event.event_id,
            "classification": classification.classification.value,
            "confidence": classification.confidence,
            "risk_level": classification.risk_level,
            "record_actions": classification.record_actions,
            "suggested_reply": classification.suggested_reply[:200] if classification.suggested_reply else "",
            "operator_approval_required": classification.operator_approval_required,
            "queue_item_id": queue_item.item_id if classification.recommended_action != "none" else None,
        }

    def run_daily_digest(self) -> dict:
        if not self.scheduler.should_run_digest():
            return {"success": False, "reason": "Digest already run today"}
        digest_text = self.tools.generate_digest()
        item = QueueItem(
            action_type=ActionType.CREATE_DIGEST_POST,
            suggested_text=digest_text,
            operator_approval_required=True,
        )
        self.queue.add(item)
        self.scheduler.mark_digest_run()
        self.audit.record("digest_draft_created", f"Queue ID: {item.item_id}")
        return {"success": True, "queue_item_id": item.item_id, "digest_preview": digest_text[:300]}

    def get_status(self) -> dict:
        return {
            "config": self.config.to_dict(),
            "queue_summary": self.queue.get_summary(),
            "audit_entries": self.audit.count,
            "memory_items": len(self.memory.recent()),
        }

    @staticmethod
    def _map_action(action: str) -> ActionType:
        mapping = {
            "ask_for_missing_info": ActionType.ASK_FOR_MISSING_INFO,
            "create_job_lead": ActionType.SAVE_EMPLOYER_LEAD,
            "operator_review": ActionType.REQUEST_OPERATOR_REVIEW,
            "moderate_review": ActionType.REVIEW_MODERATION_NEEDED,
            "reject": ActionType.REQUEST_OPERATOR_REVIEW,
        }
        return mapping.get(action, ActionType.REQUEST_OPERATOR_REVIEW)


def _extract_phone(text: str) -> str | None:
    import re
    match = re.search(r'0\d{1,2}[\s/-]?\d{2,4}[\s/-]?\d{2,4}[\s/-]?\d{2,4}', text)
    return match.group(0) if match else None
