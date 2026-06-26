---
title: Risk Policy
updated: 2026-06-26
---

# Risk Policy — Sezonski rad Srbija

## Risk Levels

### low
Use for: complete vacancies with all required fields, neutral or positive worker reviews with concrete facts, simple questions, admin posts.

**Criteria:**
- All required info present
- No emotional language
- No accusations
- No personal data of others
- No legal exposure

### medium
Use for: incomplete vacancies (missing 1–3 non-critical fields), emotionally charged reviews (but no insults), unclear authorship, posts needing minor edits.

**Criteria:**
- Missing some info
- Emotionally charged but not abusive
- Ambiguous claims
- Needs clarification before publishing
- Potential for dispute if published as-is

### high
Use for: accusations of non-payment, threats, personal data exposure, fraud indicators, conflict between parties, legal risk, spam, suspicious vacancies.

**Criteria:**
- Accusations against named individuals/companies
- Insults or hate speech present
- Personal data of others present
- Fraud indicators
- Active conflict between parties
- Potential legal liability for the group
- Casino, loans, crypto, MLM

---

## Risk Actions by Level

| Risk | Action |
|------|--------|
| **low** | Can be published after standard check. Operator confirms. |
| **medium** | Needs Admin Copilot review. Safe rewrite may be needed. Operator must confirm before publishing. |
| **high** | **ESCALATE.** Manual admin review mandatory. Never publish without admin approval. Document all decisions. |

---

## Escalation Criteria

ESCALATE immediately if:

1. Post alleges non-payment of wages.
2. Post alleges threats, violence, or illegal activity.
3. Post contains a named company + accusations.
4. Post calls for boycott or protest.
5. Post contains third-party personal data.
6. Post is part of an active worker-employer dispute.
7. Two or more people are arguing in the comments.
8. An employer disputes a negative review.
9. A worker claims an employer is threatening them.
10. There is any risk of legal action against the group.

---

## Conflict Handling

When a conflict arises:

1. **Do NOT publish either side's claims** without verification.
2. Contact both parties privately.
3. Ask for documentation (contracts, payment records, messages).
4. Never take sides publicly.
5. If legal risk is present, consult a lawyer before any publication.
6. Document everything in `moderation/queue/`.

---

## Suspicious Pattern Detection

Patterns that indicate fraud or scam:

| Pattern | Action |
|---------|--------|
| "Brza zarada" / "laka zarada" | REJECT |
| "Bez iskustva, puno para" | REJECT |
| Advance payment requested | REJECT |
| No employer name or identity | NEEDS_CLARIFICATION |
| Contact only via private message | NEEDS_CLARIFICATION / REJECT |
| Link to external chat group | REJECT |
| Casino, betting, loans, crypto | REJECT |
| Repeated identical posts | REJECT (spam) |
| Request for documents via DM | REJECT |

---

## Legal Risk Reduction

For all published content:

1. Remove absolute accusations ("lopov", "prevarant").
2. Rewrite as first-person experience ("po mom iskustvu").
3. Remove third-party personal data.
4. Add disclaimer where appropriate.
5. Document the safe rewrite process.

---

## Documentation Requirements

For every escalated or high-risk case:

- Create a file in `moderation/queue/`.
- Document: who, what, when, evidence provided, decision rationale.
- If not published: document why.
- If published: document safe version + operator approval.
- Move to `moderation/resolved/` when resolved.
