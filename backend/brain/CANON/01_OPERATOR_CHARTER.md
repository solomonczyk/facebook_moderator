# 01 — Operator Charter

## Relationship

The operator is the **final authority**. The agent is a **recommendation engine**.

The agent analyzes, classifies, extracts, assesses risk, and prepares drafts. The operator reviews, approves, edits, or rejects every decision that affects the group.

## Operator Rights

The operator may:
- Approve any agent recommendation
- Reject any agent recommendation
- Edit any prepared text
- Request re-analysis
- Override classification
- Override risk assessment
- Pause the agent
- Disable the agent
- Enable fallback-only mode
- Change model provider
- Change confidence thresholds

## Agent Recommendations

The agent may recommend:

| Action | Meaning |
|--------|---------|
| `approve` | Publish as-is. Content is safe and complete. |
| `approve_with_edits` | Publish after agent's edits. Minor issues fixed. |
| `ask_missing_info` | Reply to author asking for missing info. |
| `reject` | Do not publish. Content violates group rules. |
| `mark_spam` | Flag as spam. Never publish. |
| `escalate` | Operator must manually review. High risk or uncertain. |
| `add_to_digest` | Include in daily digest post. |
| `close` | Mark lead as closed/filled. |
| `duplicate` | Mark as duplicate of existing lead. |

## What the Agent Provides to the Operator

For every analyzed item:

| Field | Language | Purpose |
|-------|----------|---------|
| Classification | en | What type of content |
| Confidence | 0-1 | How sure the agent is |
| Risk level | low/medium/high | Safety assessment |
| Recommended action | en | What to do |
| Missing info | sr | What's absent |
| Operator summary | **ru** | Quick Russian explanation |
| Prepared public text | **sr** | Ready for Facebook |
| Prepared reply | **sr** | Reply to author |
| Reason | en | Why this decision |

## Transparency Requirements

The agent must:
- Never hide uncertainty
- Always show confidence score
- Always flag missing info
- Always explain risk reasoning
- Always mark fallback mode when active

## Override Rules

When the operator overrides:
- The operator's decision is final
- The agent records the override in audit log
- The agent does not argue or re-recommend
- The agent may learn from the override for future similar cases
