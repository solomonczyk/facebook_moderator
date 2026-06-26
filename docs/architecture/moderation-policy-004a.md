---
type: architecture
section: moderation
task: TASK-004A
date: 2026-06-26
---

# Moderation Policy

## Queue States

```
[New] → [Approved for Digest] → [Published]
  ↓           ↓
[Needs Review]  [Rejected]
  ↓
[Escalated → Manual Admin]
```

## Moderation Actions

| From | To | When |
|------|----|------|
| new | approved_for_digest | Lead is safe, relevant, has contact or clear action |
| new | needs_review | Missing critical info, unclear text, possible duplicate |
| new | rejected | Spam, wrong country, not seasonal, fraud, abuse |
| new | escalated | Serious allegations, legal risk, conflict |
| needs_review | approved_for_digest | After operator added missing info |
| needs_review | rejected | Confirmed unusable after review |
| escalated | approved_for_digest | After admin resolution |
| escalated | rejected | Confirmed too risky |

## What Triggers Escalation

1. Allegations of non-payment
2. Threats, violence, illegal activity claims
3. Named company/individual + serious accusations
4. Call for boycott or protest
5. Third-party personal data in post
6. Active worker-employer dispute
7. Legal risk to the platform
8. Coordinated reputation attack

## What Triggers Auto-Reject

1. Casino, betting, gambling
2. Loan/credit offers
3. Cryptocurrency/NFT
4. MLM / network marketing
5. Not seasonal work
6. Not in Serbia
7. Empty/unreadable content
8. Duplicate of already rejected item

## Digest Approval Rules

A lead can go into the public digest ONLY if:

- classification is good_lead, low_info_lead, or contact_only_lead
- moderation_status is approved_for_digest
- risk_level is low or medium (NOT high, NOT reject)
- duplicate_status is NOT duplicate (repeat_candidate allowed with marking)
- operator_verified is true (or marked as unverified in the post)

## Post Queue

Separate from moderation:

```
[Draft] → [Ready] → [Posted] → [Archived]
   ↓         ↓
[Rejected] [Rejected]
```

Operator manually publishes every post. No auto-posting.
