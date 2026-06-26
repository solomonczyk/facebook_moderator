# Risk Policy

## Risk Levels

| Level | Meaning | Publish? | Digest? |
|-------|---------|----------|---------|
| low | Safe, standard content | Yes | Yes |
| medium | Some missing info, emotional | Yes with edits | Yes with warnings |
| high | Red flags, possible scam | NO | NO |

## Risk Flags

| Flag | Description |
|------|-------------|
| no_contact | No phone, no Viber, no WhatsApp, no inbox |
| advance_payment | Asks for money before work starts |
| document_request | Asks for passport/ID/JMBG |
| crypto_casino | Casino, crypto, forex, betting |
| too_good_to_be_true | Unrealistic pay for unskilled work |
| unknown_intermediary | Unclear who is offering the job |
| no_location | No city/region mentioned |
| no_pay_info | Pay not mentioned |
| outside_serbia | Job location outside Serbia |
| inbox_only | Contact only via Facebook inbox |
| suspicious_link | External link without context |

## Confidence Rules

| Confidence | Action |
|-----------|--------|
| < 0.60 | Escalate to operator |
| 0.60 – 0.80 | Approve with edits or ask missing info |
| > 0.80 | Approve (if risk is low/medium) |

## Spam Rules

Spam and suspicious content must NEVER become digest candidates.
High-risk content must NEVER be published without operator approval.
