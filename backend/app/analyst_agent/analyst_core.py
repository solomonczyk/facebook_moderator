"""Analyst core: orchestrates brain -> policy -> execute pipeline."""

import uuid
import logging
from datetime import datetime

from .config import AnalystConfig
from .policy import PolicyEngine
from .brain import analyze_queue_item, AnalystDecision
from .risk_scorer import assess_risk
from .audit import AnalystAudit

logger = logging.getLogger("sezonski.analyst")


class AnalystAgent:
    def __init__(self, config: AnalystConfig | None = None, runtime_agent=None):
        self.config = config or AnalystConfig()
        self.policy = PolicyEngine()
        self.audit = AnalystAudit()
        self.runtime_agent = runtime_agent
        self._decision_count: int = 0

    @property
    def enabled(self) -> bool:
        return self.config.analyst_enabled

    def process_queue_item(self, queue_item: dict) -> dict:
        """Full pipeline: analyze -> policy check -> execute or escalate."""
        decision_id = f"dec_{uuid.uuid4().hex[:12]}"
        item_id = queue_item.get("item_id", "unknown")
        item_text = queue_item.get("suggested_text", "")

        # 1. Sanitize untrusted content
        sanitized = self.policy.sanitize_content(item_text)

        # Create sanitized copy for analysis
        safe_item = {**queue_item, "suggested_text": sanitized}

        # 2. Analyze
        decision = analyze_queue_item(safe_item)

        # 3. Risk assessment
        risk = assess_risk(
            decision.action,
            decision.extracted_entities,
            raw_text=sanitized,
            item_flags=decision.flags,
        )
        decision.risk_level = risk.risk_level

        # 4. Policy validation
        policy_result = self.policy.validate(
            decision.action,
            risk_level=decision.risk_level,
            confidence=decision.confidence,
            autonomous_mode=self.config.autonomous_mode_enabled,
        )

        # 5. Execute or escalate
        executed = False
        escalated = False
        execution_result = ""

        if policy_result.allowed and self.config.autonomous_mode_enabled:
            executed = True
            execution_result = self._execute_action(decision, queue_item)
        elif policy_result.requires_operator:
            escalated = True
            execution_result = f"Escalated: {policy_result.reason}"
        else:
            execution_result = f"Blocked: {policy_result.blocked_reason}"

        # 6. Audit
        self.audit.record(
            decision_id=decision_id,
            queue_item_id=item_id,
            action=decision.action,
            risk_level=decision.risk_level,
            confidence=decision.confidence,
            policy_allowed=policy_result.allowed,
            executed=executed,
            escalated=escalated,
            reasoning=decision.reasoning,
        )
        self._decision_count += 1

        return {
            "decision_id": decision_id,
            "queue_item_id": item_id,
            "action": decision.action,
            "confidence": decision.confidence,
            "risk_level": decision.risk_level,
            "policy_allowed": policy_result.allowed,
            "executed": executed,
            "escalated": escalated,
            "reasoning": decision.reasoning,
            "suggested_reply": decision.suggested_reply,
            "flags": decision.flags,
            "requires_operator": policy_result.requires_operator,
            "execution_result": execution_result,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def process_pending_queue(self) -> dict:
        """Process all pending queue items. Returns summary."""
        if not self.runtime_agent:
            return {"processed": 0, "error": "No runtime agent available"}

        ok, reason = self.config.can_operate()
        if not ok:
            return {"processed": 0, "error": reason}

        pending = self.runtime_agent.queue.get_all()
        results = []
        for item in pending[:self.config.max_autonomous_decisions_per_hour]:
            result = self.process_queue_item(item.to_dict())
            results.append(result)

        return {
            "processed": len(results),
            "executed": len([r for r in results if r["executed"]]),
            "escalated": len([r for r in results if r["escalated"]]),
            "blocked": len([r for r in results if not r["policy_allowed"]]),
            "results": results,
        }

    def _execute_action(self, decision: AnalystDecision, queue_item: dict) -> str:
        """Execute an allowed action on the runtime agent."""
        item_id = queue_item.get("item_id", "")
        agent = self.runtime_agent

        if not agent:
            return "No runtime agent"

        action = decision.action

        if action == "save_worker_lead":
            return f"Worker lead saved: {decision.extracted_entities}"

        elif action == "save_job_lead":
            return f"Job lead saved"

        elif action == "mark_spam_candidate":
            item = agent.queue.get(item_id)
            if item:
                item.reject("Spam detected by analyst")
                agent.audit.record("analyst_spam", f"Item: {item_id}")
            return "Marked as spam candidate"

        elif action == "mark_duplicate":
            agent.audit.record("analyst_duplicate", f"Item: {item_id}")
            return "Marked as duplicate"

        elif action == "ask_missing_info_draft":
            return f"Drafted missing-info reply: {decision.suggested_reply[:100]}"

        elif action == "approve_for_digest":
            item = agent.queue.get(item_id)
            if item:
                item.approve("analyst")
                agent.audit.record("analyst_approve_digest", f"Item: {item_id}")
            return "Approved for digest"

        elif action == "generate_digest_draft":
            result = agent.run_daily_digest()
            return f"Digest draft: {result.get('queue_item_id', 'none')}"

        elif action == "escalate_to_operator":
            return "Escalated to operator"

        elif action == "archive_closed_lead":
            agent.audit.record("analyst_archive", f"Item: {item_id}")
            return "Archived closed lead"

        return f"Action '{action}' executed"

    def get_status(self) -> dict:
        return {
            "analyst_enabled": self.config.analyst_enabled,
            "autonomous_mode_enabled": self.config.autonomous_mode_enabled,
            "decisions_made": self._decision_count,
            "audit_summary": self.audit.get_summary(),
            "config": self.config.to_dict(),
        }
