"""Agent brain: classifies incoming content and extracts entities."""

import re
from dataclasses import dataclass, field
from enum import Enum


class ContentClass(str, Enum):
    EMPLOYER_JOB_POST = "employer_job_post"
    WORKER_LOOKING_FOR_JOB = "worker_looking_for_job"
    WORKER_GROUP_AVAILABLE = "worker_group_available"
    WORKER_QUESTION = "worker_question"
    EMPLOYER_QUESTION = "employer_question"
    EXPERIENCE_REVIEW = "experience_review"
    CONDITIONS_REPORT = "conditions_report"
    MISSING_INFO_UPDATE = "missing_info_update"
    LEAD_CONFIRMATION = "lead_confirmation"
    LEAD_CLOSED = "lead_closed"
    MARKET_CONTEXT = "market_context"
    SPAM = "spam"
    SUSPICIOUS = "suspicious"
    IRRELEVANT = "irrelevant"
    NEEDS_OPERATOR_REVIEW = "needs_operator_review"


@dataclass
class ClassificationResult:
    classification: ContentClass = ContentClass.NEEDS_OPERATOR_REVIEW
    confidence: float = 0.0
    extracted_entities: dict = field(default_factory=dict)
    record_actions: list[str] = field(default_factory=list)
    suggested_reply: str = ""
    suggested_public_post: str = ""
    recommended_action: str = "operator_review"
    risk_level: str = "medium"
    operator_approval_required: bool = True


# ── Classification Patterns ─────────────────────────────────────────────────

WORKER_LOOKING_PATTERNS = [
    r'tražim\s+posao', r'tražim\s+poso', r'potreban\s+posao', r'potreban\s+poso',
    r'trebam?\s+posao', r'treba\s+mi\s+posao', r'ima\s+li\s+(?:ko\s+)?posla',
    r'interesuje\s+(?:me\s+)?posao', r'interesuje\s+(?:me\s+)?poso',
    r'da\s+li\s+(?:neko\s+)?treba\s+radnik', r'da\s+li\s+(?:neko\s+)?traži\s+radnik',
]
WORKER_GROUP_PATTERNS = [
    r'imam\s+(?:\d+\s+)?(?:ljudi|radnika|ljude)', r'imam\s+grupu',
    r'(?:grupa|grupu|grupovova)\s+(?:od\s+)?\d+\s+(?:ljudi|radnika)',
    r'(?:moja\s+)?ekipa', r'moja\s+grupa', r'(?:nas|ima\s+nas)\s+(?:je\s+)?\d+',
    r'\d+\s+(?:ljudi|radnika|članova)', r'sa\s+(?:svojim\s+)?prevozom?\s+\d+\s+(?:ljudi|radnika)',
]
EMPLOYER_JOB_PATTERNS = [
    # Direct employer signals — check FIRST
    r'tražimo\s+radnik', r'tražimo\s+berač', r'tražimo\s+\d+\s+radnik',
    r'tražim\s+radnik', r'tražim\s+radnic', r'tražim\s+berač',
    r'potreban\s+radnik', r'potrebni\s+radnici', r'potrebne\s+radnice',
    r'potrebna\s+\d+\s+radnik', r'potrebno\s+\d+\s+radnik',
    r'trebaju\s+(?:mi\s+)?radnici', r'treba\s+nam\s+ekipa',
    r'zapošljavamo?', r'firma\s+traži', r'hitno\s+(?:potreb|traž)',
    # Job type signals — only when combined with contact or other employer signals
    r'za\s+berbu\s+(?:malina|višanja|jabuka|trešanja|borovnica|kupina|šljiva)',
    r'za\s+branje\s+(?:malina|višanja|jabuka|trešanja|borovnica)',
    r'radnike?\s+za\s+(?:berbu|branje|pakovanje|sortiranje)',
    r'radnice?\s+za\s+(?:berbu|branje|pakovanje|sortiranje)',
    r'na\s+farmi\s+traž',
]
EXPERIENCE_PATTERNS = [
    r'radio\s+sam', r'radila\s+sam', r'moje\s+iskustvo', r'lično\s+sam',
    r'bio\s+sam\s+na', r'bila\s+sam\s+na', r'preporučujem', r'ne\s+preporučujem',
]
SPAM_PATTERNS = [
    # High-risk spam
    r'kazino', r'casino', r'kripto', r'crypto', r'bitcoin',
    r'forex', r'trading', r'uplata\s+unapred', r'depozit',
    r'brza\s+zarada', r'pasivna\s+zarada', r'bez\s+ulaganja',
    r'laka\s+zarada', r'zaradite?\s+od\s+kuće', r'kladionica',
    r'kredit\s+online', r'mlm', r'online\s+kazino',
    r'bez\s+iskustva\s+puno\s+para', r'klikni', r'kliknite',
    # Suspicious
    r'garantovan\s+prihod', r'zagarantovan',
]


def classify(raw_text: str, source_group: str = "") -> ClassificationResult:
    """Classify raw text content and extract entities."""
    text = raw_text.lower().strip()
    result = ClassificationResult()

    # 1. SPAM — always check first
    for pattern in SPAM_PATTERNS:
        if re.search(pattern, text):
            result.classification = ContentClass.SPAM
            result.confidence = 0.95
            result.risk_level = "high"
            result.recommended_action = "reject"
            result.suggested_reply = "Ova objava ne može biti odobrena jer ne pripada temama grupe."
            return result

    # 2. SUSPICIOUS — check after spam
    suspicious_patterns = [
        r'uplata\s+unapred', r'depozit', r'JMBG', r'slika\s+pasoša',
        r'slika\s+lične\s+karte', r'dokumenta\s+unapred',
        r'pošaljite\s+(?:sliku|sken)', r'šaljite\s+(?:sliku|sken)',
        r'(?:2000|3000)\s*(?:€|EUR|evra)\s+dnevno',  # Too good to be true
    ]
    for pattern in suspicious_patterns:
        if re.search(pattern, text):
            result.classification = ContentClass.SUSPICIOUS
            result.confidence = 0.90
            result.risk_level = "high"
            result.recommended_action = "escalate"
            result.record_actions = []
            result.suggested_reply = "Ova objava zahteva dodatnu proveru pre objave."
            return result

    # 3. EMPLOYER — check BEFORE worker patterns
    for pattern in EMPLOYER_JOB_PATTERNS:
        if re.search(pattern, text):
            result.classification = ContentClass.EMPLOYER_JOB_POST
            result.confidence = 0.85
            result.record_actions = ["create_job_lead", "create_employer_profile"]
            result.recommended_action = "create_job_lead"
            result.extracted_entities["locations"] = _extract_locations(text)
            if re.search(r'(?:smeštaj|stan|smeštajem)', text):
                result.extracted_entities["accommodation"] = True
            if re.search(r'(?:hrana|hranu|obrok)', text):
                result.extracted_entities["food"] = True
            if re.search(r'(?:dnevnica|plata|RSD|dinara|evra|€)', text):
                result.extracted_entities["pay_mentioned"] = True
            result.risk_level = "low"
            return result

    # 3. WORKER GROUP — only after employer check passes
    for pattern in WORKER_GROUP_PATTERNS:
        if re.search(pattern, text):
            result.classification = ContentClass.WORKER_GROUP_AVAILABLE
            result.confidence = 0.85
            result.record_actions = ["create_worker_profile", "create_worker_lead"]
            result.recommended_action = "ask_for_missing_info"
            count_match = re.search(r'(\d+)\s*(?:ljudi|radnika|ljude|članova)', text)
            if count_match:
                result.extracted_entities["workers_count"] = int(count_match.group(1))
            locations = _extract_locations(text)
            if locations:
                result.extracted_entities["locations"] = locations
            if re.search(r'(?:svoj\w*|sopstveni|vlastiti)\s+(?:prevoz|kombi|auto)', text):
                result.extracted_entities["transport"] = "own_transport"
            result.extracted_entities["experience"] = _extract_experience(text)
            result.extracted_entities["contact_status"] = "missing" if not _has_contact(text) else "present"
            result.suggested_reply = _build_worker_group_reply(result.extracted_entities)
            result.risk_level = "low"
            return result

    # 4. WORKER LOOKING (individual)
    for pattern in WORKER_LOOKING_PATTERNS:
        if re.search(pattern, text):
            result.classification = ContentClass.WORKER_LOOKING_FOR_JOB
            result.confidence = 0.80
            result.record_actions = ["create_worker_profile"]
            result.recommended_action = "ask_for_missing_info"
            result.extracted_entities["locations"] = _extract_locations(text)
            result.extracted_entities["contact_status"] = "missing" if not _has_contact(text) else "present"
            result.suggested_reply = _build_worker_reply(result.extracted_entities)
            result.risk_level = "low"
            return result

    # Experience / review
    for pattern in EXPERIENCE_PATTERNS:
        if re.search(pattern, text):
            result.classification = ContentClass.EXPERIENCE_REVIEW
            result.confidence = 0.75
            result.record_actions = ["create_review"]
            result.recommended_action = "moderate_review"
            result.risk_level = "medium"
            return result

    # Default
    result.classification = ContentClass.NEEDS_OPERATOR_REVIEW
    result.confidence = 0.3
    result.recommended_action = "operator_review"
    return result


def _extract_locations(text: str) -> list[str]:
    known = [
        "arilje", "ivanjica", "guča", "čajetina", "požega", "užice", "kosjerić",
        "valjevo", "čačak", "kraljevo", "kruševac", "niš", "leskovac", "vranje",
        "beograd", "novi sad", "subotica", "sombor", "odžaci", "srem",
        "sremska mitrovica", "šid", "erdevik", "ruma", "pančevo", "zrenjanin",
        "šabac", "loznica", "bajina bašta", "prijepolje", "vojvodina",
    ]
    found = []
    for loc in known:
        if loc in text:
            found.append(loc.title())
    return found


def _has_contact(text: str) -> bool:
    return bool(re.search(r'0\d{1,2}[\s/-]?\d{2,4}[\s/-]?\d{2,4}[\s/-]?\d{2,4}', text))


def _extract_experience(text: str) -> str:
    if re.search(r'(?:dugogodišnje|višegodišnje)\s+iskustvo', text):
        return "long_term_experience"
    if re.search(r'(?:poljoprivred|poljuprivred|berb|branje|građevin)', text):
        return "agricultural_or_manual"
    return "unspecified"


def _build_worker_group_reply(entities: dict) -> str:
    count = entities.get("workers_count", "?")
    reply = f"Hvala na javljanju! Da bismo vas povezali sa poslodavcima, molimo navedite:\n\n"
    reply += "- Vrsta posla koji tražite (berba, građevina, pakovanje...)\n"
    reply += "- Datum kada ste dostupni\n"
    reply += "- Očekivana dnevnica ili dogovor\n"
    reply += "- Da li vam treba smeštaj i hrana\n"
    reply += "- Kontakt telefon / Viber / WhatsApp\n"
    if count and count != "?":
        reply += f"\nGrupa od {count} ljudi — to je odlično za veće poslodavce."
    return reply


def _build_worker_reply(entities: dict) -> str:
    reply = "Hvala na javljanju! Da bismo vam pomogli da nađete posao, molimo navedite:\n\n"
    reply += "- Vrsta posla koji tražite\n"
    reply += "- Gde ste tačno (mesto/grad)\n"
    reply += "- Kada ste dostupni\n"
    reply += "- Da li vam treba smeštaj\n"
    reply += "- Kontakt telefon / Viber / WhatsApp\n"
    return reply
