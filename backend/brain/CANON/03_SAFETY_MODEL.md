# 03 — Safety Model

## Risk Levels

### LOW

Content is safe. Complete or mostly complete. No red flags. Standard seasonal work content.

**Publishable**: Yes, with disclaimer if needed.

### MEDIUM

Content has some missing info, emotional language, or unclear elements. Not dangerous but needs attention.

**Publishable**: Yes, with edits and missing info clearly marked.

### HIGH

Content has red flags: advance payment, document requests, no contact, unrealistic pay, suspicious intermediary, or potential scam.

**Publishable**: NO. Escalate to operator.

## When to Publish

PUBLISH when:
- Classification is employer_job_post, worker_request, worker_group_available, review_experience, or question
- Risk is low or medium
- Content is not spam or suspicious
- At minimum: has contact OR location OR clear next action
- Disclaimer is included
- Forbidden words are absent

## When to Escalate

ESCALATE when:
- Content asks for advance payment or deposit
- Content requests passport/ID photos or JMBG
- Content mentions crypto, casino, forex, betting
- Content contains threats, abuse allegations
- Content has suspicious intermediary patterns
- Unrealistic pay ("2000e dnevno", "10000 RSD dnevno" without explanation)
- No location AND no contact
- Confidence is below 0.60
- The agent is unsure about classification

## When to Reject

REJECT when:
- Spam, casino, crypto, forex, betting, loans
- MLM, network marketing
- Hate speech, insults, personal attacks
- Personal data exposure (JMBG, passport, private address)
- Not about seasonal work in Serbia
- Empty or unreadable content

## When to Mark Spam

MARK SPAM when:
- Explicit casino/crypto/forex/betting keywords
- "Brza zarada", "laka zarada", "bez iskustva puno para"
- Repeated identical content
- Links to external sites without job context
- Obvious scam patterns

Spam is NEVER published. Spam is NEVER a digest candidate.

## High-Risk Signals

| Signal | Risk | Action |
|--------|------|--------|
| Advance payment required | HIGH | Escalate |
| Deposit requested | HIGH | Escalate |
| JMBG requested | HIGH | Escalate |
| Passport photo requested | HIGH | Escalate |
| ID card photo requested | HIGH | Escalate |
| Crypto/casino/forex | HIGH | Reject/Mark spam |
| No location AND no contact | HIGH | Escalate |
| Unrealistic pay | HIGH | Escalate |
| Suspicious intermediary | HIGH | Escalate |
| Document collection before contract | HIGH | Escalate |
| Non-Serbia job pretending local | HIGH | Escalate |

## Worker Safety Concerns

The agent must be especially careful with:
- Jobs requiring workers to travel to remote locations without clear address
- Jobs asking workers to pay for "registration" or "visa processing"
- Jobs offering accommodation but not describing it
- Jobs with no employer name or company info
- Jobs directing to external chat groups without explanation

## Confidence Rules

- Confidence < 0.60 → escalate regardless of classification
- Confidence 0.60–0.80 → approve_with_edits or ask_missing_info
- Confidence > 0.80 → approve (if all other checks pass)

## Digest Safety

Spam and suspicious content must NEVER become digest candidates. High-risk content must NEVER be published.
