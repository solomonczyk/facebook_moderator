"""Risk scorer: assigns risk level and flags based on lead content."""

import re
from .models import RiskLevel, RiskFlag, JobLead


SPAM_KEYWORDS = [
    'brza zarada', 'laka zarada', 'bez iskustva puno para',
    'garantovano', 'zagarantovano', 'klikni', 'kliknite',
    'kazino', 'kladionica', 'kredit', 'kripto',
    'mlm', 'mrežni marketing',
]

SUSPICIOUS_PAY_PATTERNS = [
    (re.compile(r'(?:zaradite|zaradi)\s*(?:od\s*)?\d+[.,]?\d*\s*€?\s*(?:dnevno|na dan)', re.IGNORECASE), 'too_good_to_be_true'),
]


def score_risk(lead: JobLead) -> tuple[RiskLevel, list[RiskFlag]]:
    flags: list[RiskFlag] = []

    # No contact at all
    if not lead.contact_phone and not lead.contact_inbox_only and not lead.contact_facebook:
        flags.append(RiskFlag.NO_CONTACT)

    # No location
    if not lead.location:
        flags.append(RiskFlag.UNKNOWN_LOCATION)

    # No pay info
    if not lead.pay_amount:
        flags.append(RiskFlag.NO_PAY_INFO)

    # Spam keywords in raw text
    if lead.raw_text:
        text_lower = lead.raw_text.lower()
        for kw in SPAM_KEYWORDS:
            if kw in text_lower:
                flags.append(RiskFlag.SPAM_KEYWORDS)
                break

    # Asks for payment
    payment_triggers = ['uplata', 'avans', 'depozit', 'uplati', 'platite', 'plati']
    if lead.raw_text and any(t in lead.raw_text.lower() for t in payment_triggers):
        flags.append(RiskFlag.ASKS_FOR_PAYMENT)

    # Asks for documents
    doc_triggers = ['pošalji dokumenta', 'pošaljite dokumenta', 'slikaj pasoš',
                    'slikajte pasoš', 'jmbg', 'ličnu kartu']
    if lead.raw_text and any(t in lead.raw_text.lower() for t in doc_triggers):
        flags.append(RiskFlag.ASKS_FOR_DOCUMENTS)

    # Foreign country
    if lead.country.lower() not in ('srbija', 'serbia', '', 'nepoznato'):
        flags.append(RiskFlag.FOREIGN_COUNTRY)

    # Too good to be true pay
    if lead.raw_text:
        for pattern, flag_name in SUSPICIOUS_PAY_PATTERNS:
            if pattern.search(lead.raw_text):
                flags.append(RiskFlag.TOO_GOOD_TO_BE_TRUE)
                break

    # Determine level
    if RiskFlag.ASKS_FOR_PAYMENT in flags or RiskFlag.TOO_GOOD_TO_BE_TRUE in flags:
        level = RiskLevel.HIGH
    elif RiskFlag.SPAM_KEYWORDS in flags:
        level = RiskLevel.REJECT
    elif len(flags) >= 3:
        level = RiskLevel.HIGH
    elif len(flags) >= 1:
        level = RiskLevel.MEDIUM
    else:
        level = RiskLevel.LOW

    return level, flags
