# Moderation Policy — Sezonski rad Srbija

## Purpose

This document defines the moderation rules for the Facebook group **"Sezonski rad Srbija | Poslovi i iskustva radnika"**. It serves as the authoritative reference for human administrators and as the foundation for the AI Admin Copilot's system prompt.

All rules are designed around one core value: **trust**. The group must be a safe, useful place for seasonal workers to find jobs, share experiences, and help each other.

---

## 1. Group Scope

The group covers **seasonal work in Serbia** only. This includes:

- Agriculture (fruit picking, harvesting, planting)
- Construction (seasonal projects)
- Hospitality (summer/winter season)
- Manufacturing (seasonal production)
- Other temporary/seasonal employment in Serbia

Content NOT in scope:
- Permanent full-time employment (druge grupe postoje za to)
- Jobs outside Serbia
- Non-work-related content
- Commerce, sales, MLM, crypto, casino, loans

---

## 2. Verdict System

Every post must receive one of five verdicts:

### APPROVE
Publish without changes. Post is complete, relevant, safe, and contains no violations.

### APPROVE_WITH_EDITS
Post has value but needs changes before publishing. The admin or copilot edits the text to fix minor issues, remove unsafe language, or add missing structure.

### NEEDS_CLARIFICATION
Post is too vague or incomplete for a decision. The admin asks the author to provide missing information.

### REJECT
Post cannot be published. It violates group rules (spam, fraud, insults, off-topic, personal data that cannot be removed).

### ESCALATE
Post requires manual administrator review. It contains serious allegations, conflict, or legal risk that the copilot cannot resolve alone.

---

## 3. Post Type Classification

| Type | Definition | Typical Action |
|---|---|---|
| **vacancy** | Job offer from employer/recruiter | Check required fields |
| **worker_review** | Worker's personal experience | Check for insults, personal data, concreteness |
| **job_request** | Worker looking for work | Usually APPROVE, check for personal data |
| **question** | Question about seasonal work | Usually APPROVE |
| **warning** | Caution about employer/situation | Check for evidence, avoid defamation |
| **recommendation** | Positive endorsement | Usually APPROVE |
| **admin_post** | Group administration announcement | APPROVE (admins self-moderate) |
| **spam** | Unwanted commercial content | REJECT |
| **conflict** | Active dispute between parties | ESCALATE |
| **unclear** | Cannot determine content | NEEDS_CLARIFICATION |

---

## 4. Vacancy Requirements

Every vacancy MUST include these 12 fields:

1. Location (city/town)
2. Type of work
3. Start date
4. Number of workers needed
5. Pay amount
6. Payment method
7. Working hours
8. Accommodation (yes/no)
9. Food (yes/no)
10. Transport
11. Contact (phone/Viber/WhatsApp)
12. Worker registration status

### Suspicious Patterns

- Unrealistic pay without details
- No location
- No contact info
- Requests for advance payment
- "Easy money" / "brza zarada" language
- Directing to external chat groups
- Missing employer identity

---

## 5. Worker Review Requirements

Reviews should answer:
- Where did you work?
- What type of work?
- When did you work?
- What was promised?
- What actually happened?
- Were you paid?
- How was accommodation/food/treatment?
- Would you recommend?

### Safe Language for Negative Reviews

Never publish:
- Direct accusations of criminal behavior ("lopov", "prevarant")
- Insults or degrading language
- Information about other workers without their consent
- Personal data of employers (home address, private phone, ID numbers)

Always rewrite to:
- First-person experience ("po mom iskustvu")
- Specific, verifiable facts
- Neutral tone

---

## 6. Prohibited Content

The following content is NEVER allowed:

### Spam
- Unrelated product/service ads
- Casino, betting, gambling
- Loan/credit offers
- Cryptocurrency/NFT
- MLM / network marketing
- Repeated identical posts
- Links without context

### Fraud
- Advance fee requests
- Fake visa/document services
- "Guaranteed" unrealistic earnings
- Pyramid schemes
- Fake employer identities

### Hate & Abuse
- Ethnic/racial slurs
- Personal insults
- Threats of violence
- Harassment
- Degrading language

### Privacy Violations
- JMBG (citizen ID number)
- Passport/ID card numbers
- Private addresses
- Third-party phone numbers
- Private message screenshots
- Bank accounts
- Children's data

---

## 7. Language Policy

- **Primary language**: Serbian (Latin and Cyrillic)
- **Accepted languages**: Russian, Ukrainian, Hungarian, Romanian
- Non-Serbian posts should be translated to Serbian for the group
- The original language post + Serbian translation can be published together

---

## 8. Conflict Resolution

When a conflict arises (worker vs employer dispute):

1. ESCALATE immediately to human admin
2. Do NOT publish either party's claims without verification
3. Ask both parties for documentation privately
4. Never take sides publicly
5. If legal risk is present, consult a lawyer before publishing

---

## 9. Growth Policy

The group grows through quality, not spam.

**Allowed growth activities:**
- Engaging question posts
- Multilingual announcements
- Weekly content plans
- Soft personal invitations (manual, not mass)

**Forbidden growth activities:**
- Mass messaging
- Fake reviews or fake vacancies
- Aggressive cross-posting
- Bot-driven engagement
- Buying followers or engagement

---

## 10. Privacy & Legal

- The group is public on Facebook. Assume all posts are visible to everyone.
- Administrators do not verify employers. The group is a platform for information sharing, not an employment agency.
- Negative reviews must be factual and first-person. The group does not host "blacklists."
- Personal data of any person must not be published without their explicit consent.
- If law enforcement requests data, comply with applicable laws.

---

## Appendix A: Common Scam Patterns in Seasonal Work (Balkan Context)

1. **"Advance visa fee" scam**: Employer demands payment for visa processing before any contract is signed.
2. **"Phantom employer" scam**: Job ad with no company name, no address, only a WhatsApp number.
3. **"Fake agency" scam**: Intermediary charges workers for "registration" then disappears.
4. **"Bait and switch"**: Promises one salary/location, delivers completely different conditions.
5. **"Document harvesting"**: Asks for passport/ID scans before any real job discussion.

## Appendix B: Common Insult Patterns (Serbian/Bosnian/Croatian)

The AI copilot is trained to detect insults in the regional languages. Administrators should be aware of common patterns:

- Direct personal insults targeting intelligence, family, ethnicity
- Ethnic/nationalist slurs (common in Balkan online discourse)
- Gendered insults and threats
- Violence-adjacent language ("treba ga prebiti", "ubiti", "uništiti")

When in doubt about whether language crosses the line, consult a second admin.

## Appendix C: Decision Flowchart

```
Post received
    │
    ├─ Related to seasonal work in Serbia?
    │   └─ NO → REJECT
    │
    ├─ Contains spam/fraud/casino/loans/crypto/MLM?
    │   └─ YES → REJECT
    │
    ├─ Contains insults/threats/hate?
    │   └─ YES → REJECT
    │
    ├─ Contains others' personal data?
    │   └─ YES → APPROVE_WITH_EDITS or REJECT
    │
    ├─ Contains serious allegations (non-payment, threats, violence)?
    │   └─ YES → ESCALATE
    │
    ├─ Is a vacancy missing required fields?
    │   └─ YES → NEEDS_CLARIFICATION
    │
    ├─ Is a review emotionally charged or with minor issues?
    │   └─ YES → APPROVE_WITH_EDITS
    │
    └─ Everything is fine → APPROVE
```
