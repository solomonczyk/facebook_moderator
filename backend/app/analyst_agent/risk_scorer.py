"""Risk scorer for analyst agent: evaluates risk of autonomous actions."""

from dataclasses import dataclass, field


@dataclass
class RiskAssessment:
    risk_level: str = "low"  # low, medium, high, reject
    score: int = 20  # 0-100
    flags: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)


def assess_risk(action: str, extracted_entities: dict, raw_text: str = "",
                item_flags: list | None = None) -> RiskAssessment:
    """Assess risk of executing an action autonomously."""

    assessment = RiskAssessment()
    item_flags = item_flags or []

    # High-risk actions always get high risk
    high_risk_actions = {"mark_spam_candidate"}
    if action in high_risk_actions:
        assessment.risk_level = "high"
        assessment.score = 80
        assessment.reasons.append(f"Action '{action}' is inherently high-risk")
        assessment.flags.append("high_risk_action")

    # Missing contact -> higher risk
    if not extracted_entities.get("has_contact", True):
        assessment.score += 15
        assessment.flags.append("missing_contact")
        assessment.reasons.append("Missing contact info")

    # Large worker groups -> higher impact
    count = extracted_entities.get("worker_count", 0)
    if count and count > 20:
        assessment.score += 10
        assessment.flags.append("large_group")
        assessment.reasons.append(f"Large group ({count} workers) — higher impact if wrong")

    # Spam flags -> high risk
    spam_flags = [f for f in item_flags if "spam" in f.lower()]
    if spam_flags:
        assessment.score += 20
        assessment.flags.extend(spam_flags)

    # No location -> higher risk
    if not extracted_entities.get("has_location", True):
        assessment.score += 10
        assessment.flags.append("missing_location")
        assessment.reasons.append("Missing location")

    # Determine final risk level
    if assessment.score >= 70:
        assessment.risk_level = "high"
    elif assessment.score >= 40:
        assessment.risk_level = "medium"
    else:
        assessment.risk_level = "low"

    return assessment
