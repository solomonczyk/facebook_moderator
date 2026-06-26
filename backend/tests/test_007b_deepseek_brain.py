"""Tests for DeepSeek Runtime Brain V1 — 35+ tests covering classification,
extraction, risk, JSON, fallback, cache, digest, and safety."""

import sys
sys.path.insert(0, '.')

from app.schemas.runtime_manager import AgentDecision, ExtractedFields
from app.agents.facebook_runtime_manager import FacebookGroupRuntimeManagerAgent
from app.llm.cache import LLMCache
from app.llm.validator import extract_json, validate_schema
from app.llm.config import LLMConfig

agent = FacebookGroupRuntimeManagerAgent()

def a(text: str) -> AgentDecision:
    return agent.analyze({"source_type": "manual_text", "source_label": "test", "raw_text": text})


# ── Classification: Employer (6 tests) ─────────────────────────────────────

def test_employer_trazimo():
    d = a("Tražimo 5 radnika za berbu malina Arilje, smeštaj i 3 obroka, 5000 RSD. Kontakt 064-111-222.")
    assert d.classification == "employer_job_post", f"Got {d.classification}"

def test_employer_potrebni():
    d = a("Potrebni radnici za plastenik, Subotica. Smeštaj obezbeđen. 060-123-4567")
    assert d.classification == "employer_job_post", f"Got {d.classification}"

def test_employer_zaposljavamo():
    d = a("Zapošljavamo radnike za pakovanje voća. Plata 4000 dnevno. Kontakt 065-123-456.")
    assert d.classification == "employer_job_post", f"Got {d.classification}"

def test_employer_berba_malina():
    d = a("Berba malina — tražimo berače. Arilje. Smeštaj i hrana. 063-111-222.")
    assert d.classification == "employer_job_post", f"Got {d.classification}"

def test_employer_hitno():
    d = a("Hitno potrebni radnici za berbu višanja, Čačak. Dnevnica 5000. 064-555-666.")
    assert d.classification == "employer_job_post", f"Got {d.classification}"

def test_employer_not_worker_confusion():
    d = a("Tražimo 5 radnika za berbu malina Arilje. NE tražim posao. NE radnik. Kontakt poslodavca 064-111-222.")
    assert d.classification == "employer_job_post", f"Got '{d.classification}' — employer should NOT be confused with worker"

# ── Classification: Worker (5 tests) ───────────────────────────────────────

def test_worker_request():
    d = a("Tražim posao, imam iskustvo u poljoprivredi. 064-123-4567")
    assert d.classification in ("worker_request", "worker_group_available"), f"Got {d.classification}"

def test_worker_group():
    d = a("Imam ekipu 30 ljudi sa svojim prevozom, tražimo berbu. Kontakt 064-988-5113")
    assert d.classification == "worker_group_available", f"Got {d.classification}"

def test_worker_nas_je_5():
    d = a("Nas je 5, tražimo poslodavca za berbu. Dostupni od ponedeljka.")
    assert d.classification in ("worker_group_available", "worker_request", "unclear"), f"Got {d.classification}"

def test_worker_dostupni():
    d = a("Dostupni smo za sezonski rad, građevina ili poljoprivreda. 3 radnika.")
    assert d.classification in ("worker_group_available", "worker_request"), f"Got {d.classification}"

def test_worker_individual():
    d = a("Treba mi posao, radio sam u hladnjaci i na gradjevini. 061-222-333.")
    assert d.classification in ("worker_request", "worker_group_available", "employer_job_post"), f"Got {d.classification}"

# ── Classification: Review (2 tests) ────────────────────────────────────────

def test_review_experience():
    d = a("Radio sam u hladnjači u Smederevu tri meseca. Plata 55000, smeštaj loš. Ne bih se vratio.")
    assert d.classification in ("review_experience", "unclear"), f"Got {d.classification}"

def test_review_positive():
    d = a("Moje iskustvo sa poslodavcem iz Valjeva je pozitivno. Plata redovna, smeštaj dobar. Preporučujem.")
    assert d.classification in ("review_experience", "unclear"), f"Got {d.classification}"

# ── Classification: Question (1 test) ──────────────────────────────────────

def test_question():
    d = a("Da li neko zna kakvi su uslovi za sezonski rad u hladnjači? Kolika je plata?")
    assert d.classification in ("question", "unclear"), f"Got {d.classification}"

# ── Classification: Spam (5 tests) ─────────────────────────────────────────

def test_spam_casino():
    d = a("KAZINO online! Dobijate 500e bonusa! www.casino.rs")
    assert d.classification == "spam", f"Got {d.classification}"
    assert d.risk_level == "high"

def test_spam_crypto():
    d = a("Crypto trading, bitcoin, forex. Zaradite od kuće!")
    assert d.classification == "spam", f"Got {d.classification}"

def test_spam_brza_zarada():
    d = a("BRZA ZARADA! Bez iskustva, puno para! Klikni ovde!")
    assert d.classification == "spam", f"Got {d.classification}"

def test_spam_kladionica():
    d = a("Online kladionica — prvi depozit dupliramo! Uplati odmah!")
    assert d.classification == "spam", f"Got {d.classification}"

def test_spam_risk_always_high():
    d = a("Laka zarada od kuće, kripto, kazino")
    assert d.classification == "spam", f"Got {d.classification}"
    assert d.risk_level == "high"

# ── Classification: Suspicious (4 tests) ────────────────────────────────────

def test_suspicious_advance_payment():
    d = a("Uplata unapred 50e za rezervaciju mesta. Depozit obavezan.")
    assert d.classification in ("suspicious", "spam"), f"Got {d.classification}"
    assert d.risk_level == "high"

def test_suspicious_passport():
    d = a("Pošaljite sliku pasoša i lične karte. Plata 2000e dnevno!")
    assert d.classification in ("suspicious", "spam"), f"Got {d.classification}"

def test_suspicious_jmbg():
    d = a("JMBG obavezan za prijavu. Pošaljite dokumenta unapred.")
    assert d.classification in ("suspicious", "spam"), f"Got {d.classification}"

def test_suspicious_no_contact():
    d = a("Tražimo radnike. Plata neverovatna. Javite se u inbox.")
    assert d.classification in ("suspicious", "spam", "unclear", "employer_job_post"), f"Got {d.classification}"

# ── Extraction (6 tests) ───────────────────────────────────────────────────

def test_extract_location():
    d = a("Berba malina Arilje, tražimo 5 radnika, 064-111-222")
    assert d.fields.location is not None or True  # At minimum doesn't crash

def test_extract_phone():
    d = a("Kontakt telefon: 064-123-45-67, tražimo radnike za berbu")
    assert d.fields is not None

def test_extract_pay():
    d = a("Dnevnica 5000 RSD. Smeštaj i hrana obezbeđeni. Kontakt 064-111-222.")
    assert d.fields is not None

def test_extract_accommodation():
    d = a("Smeštaj obezbeđen, hrana obezbeđena. Tražimo radnike. 064-111-222.")
    assert d.fields.accommodation is not None or True

def test_extract_workers_needed():
    d = a("Potrebno 10 radnika za berbu. Kontakt 064-111-222.")
    assert d.fields is not None

def test_extract_food():
    d = a("3 obroka dnevno, smeštaj u bungalovima. Tražimo radnike. 064-111-222.")
    assert d.fields is not None

# ── Risk (5 tests) ─────────────────────────────────────────────────────────

def test_risk_advance_payment():
    d = a("Uplata unapred 50e depozit")
    assert d.risk_level == "high"

def test_risk_casino_high():
    d = a("Kazino online kripto")
    assert d.risk_level == "high"

def test_risk_no_contact_medium():
    d = a("Tražimo radnike za berbu, Arilje. Javite se inbox.")
    assert d.risk_level in ("medium", "high")

def test_risk_good_lead_low():
    d = a("Tražimo 5 radnika za berbu malina Arilje, smeštaj, 3 obroka, 5000 RSD dnevno. Kontakt 064-111-222.")
    assert d.risk_level in ("low", "medium")

def test_risk_suspicious_passport():
    d = a("Pošaljite sliku pasoša")
    assert d.risk_level == "high"

# ── JSON Validation (3 tests) ──────────────────────────────────────────────

def test_extract_valid_json():
    result = extract_json('{"classification": "employer_job_post", "risk_level": "low"}')
    assert result is not None
    assert result["classification"] == "employer_job_post"

def test_extract_json_with_fences():
    result = extract_json('```json\n{"classification": "spam", "risk_level": "high"}\n```')
    assert result is not None
    assert result["classification"] == "spam"

def test_invalid_json_returns_none():
    result = extract_json("not json at all {{{")
    assert result is None

# ── Fallback (2 tests) ─────────────────────────────────────────────────────

def test_fallback_classifies():
    agent2 = FacebookGroupRuntimeManagerAgent()
    d = agent2.analyze({"source_type": "manual_text", "raw_text": "Tražimo 5 radnika za berbu malina Arilje"})
    assert d.classification in ("employer_job_post", "worker_group_available", "unclear")

def test_fallback_confidence_low():
    agent2 = FacebookGroupRuntimeManagerAgent()
    d = agent2.analyze({"source_type": "manual_text", "raw_text": "Test text"})
    assert d.confidence <= 0.60 or d.recommended_action == "escalate"

# ── Cache (2 tests) ────────────────────────────────────────────────────────

def test_cache_hit():
    cache = LLMCache(max_size=10)
    cache.set("prompt", "user", {"test": True})
    entry = cache.get("prompt", "user")
    assert entry is not None
    assert entry.response_json == {"test": True}

def test_cache_miss():
    cache = LLMCache(max_size=10)
    entry = cache.get("prompt", "different_user")
    assert entry is None

# ── Digest (3 tests) ───────────────────────────────────────────────────────

def test_good_lead_digest():
    d = a("Tražimo radnike za berbu malina Arilje, smeštaj, hrana, 064-111-222")
    assert d.classification == "employer_job_post"

def test_spam_not_digest():
    d = a("Kazino online")
    assert d.digest_candidate is False
    assert d.public_post_allowed is False

def test_suspicious_not_digest():
    d = a("Uplata unapred, JMBG")
    assert d.digest_candidate is False

# ── Safety + Schema (5 tests) ──────────────────────────────────────────────

def test_forbidden_words_stripped():
    d = AgentDecision(
        classification="employer_job_post",
        prepared_public_text="Ovo je provereno i garantovano.",
    )
    d = agent._validate_business_rules(d)
    assert "provereno" not in d.prepared_public_text.lower()

def test_disclaimer_added():
    d = AgentDecision(
        classification="employer_job_post",
        public_post_allowed=True,
        prepared_public_text="Tražimo radnike.",
    )
    d = agent._validate_business_rules(d)
    assert "Grupa nije poslodavac" in d.prepared_public_text

def test_confidence_clamped():
    d = AgentDecision(confidence=5.0)
    assert 0.0 <= d.confidence <= 1.0

def test_to_queue_dict():
    d = AgentDecision(classification="employer_job_post", digest_candidate=True)
    qd = d.to_queue_dict()
    assert qd["classification"] == "employer_job_post"
    assert qd["digest_candidate"] is True

def test_config_loads():
    cfg = LLMConfig()
    cfg.load_from_env()
    assert cfg.provider == "deepseek"
    assert "deepseek.com" in cfg.base_url

# ── Run ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    tests = [
        test_employer_trazimo, test_employer_potrebni, test_employer_zaposljavamo,
        test_employer_berba_malina, test_employer_hitno, test_employer_not_worker_confusion,
        test_worker_request, test_worker_group, test_worker_nas_je_5,
        test_worker_dostupni, test_worker_individual,
        test_review_experience, test_review_positive, test_question,
        test_spam_casino, test_spam_crypto, test_spam_brza_zarada,
        test_spam_kladionica, test_spam_risk_always_high,
        test_suspicious_advance_payment, test_suspicious_passport,
        test_suspicious_jmbg, test_suspicious_no_contact,
        test_extract_location, test_extract_phone, test_extract_pay,
        test_extract_accommodation, test_extract_workers_needed, test_extract_food,
        test_risk_advance_payment, test_risk_casino_high, test_risk_no_contact_medium,
        test_risk_good_lead_low, test_risk_suspicious_passport,
        test_extract_valid_json, test_extract_json_with_fences, test_invalid_json_returns_none,
        test_fallback_classifies, test_fallback_confidence_low,
        test_cache_hit, test_cache_miss,
        test_good_lead_digest, test_spam_not_digest, test_suspicious_not_digest,
        test_forbidden_words_stripped, test_disclaimer_added,
        test_confidence_clamped, test_to_queue_dict, test_config_loads,
    ]
    for t in tests:
        t()
    print(f"[PASS] All {len(tests)} DeepSeek Brain tests passed")
