"""Tests for Memory Engine v1.0 — 45+ tests."""

import os, sys, json, tempfile, shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'memory', 'ENGINE'))

from memory_engine import MemoryEngine, MemoryContext, _hash_phone, _make_id

# Use temp dir for tests
tmpdir = tempfile.mkdtemp()
engine = MemoryEngine(db_dir=tmpdir)


# ── Employer Tests ──────────────────────────────────────────────────────────

def test_create_employer():
    eid = engine.create_employer({
        "names": ["Voćarstvo Jović"],
        "phones": ["064-111-222"],
        "regions": ["Valjevo"],
        "job_types": ["berba trešanja"],
        "source": "021.rs",
    })
    assert eid.startswith("emp_")

def test_find_employer():
    eid = engine.create_employer({
        "names": ["Test Employer"], "phones": ["060-999-888"], "source": "test",
    })
    emp = engine.find_employer(eid)
    assert emp is not None
    assert "Test Employer" in emp["names"]

def test_update_employer():
    eid = engine.create_employer({"names": ["Update Test"], "phones": ["061-000-111"], "source": "test"})
    result = engine.update_employer(eid, {"jobs_published": 5, "notes": "updated"}, "Andrii")
    assert result is not None
    assert result["jobs_published"] == 5
    assert len(result["_history"]) >= 2

def test_update_nonexistent():
    result = engine.update_employer("nonexistent", {"notes": "x"})
    assert result is None

def test_employer_trust_default():
    eid = engine.create_employer({"names": ["Trust Test"], "phones": ["062-111-333"], "source": "test"})
    emp = engine.find_employer(eid)
    assert emp["trust_score"] == 0.5

def test_employer_verified_boosts_trust():
    eid = engine.create_employer({"names": ["Verified Co"], "phones": ["063-444-555"], "source": "test", "verified": True})
    score = engine.calculate_trust(eid, "employer")
    assert score > 0.5

def test_employer_complaints_lower_trust():
    eid = engine.create_employer({"names": ["Bad Co"], "phones": ["064-666-777"], "source": "test", "complaints": 5})
    score = engine.calculate_trust(eid, "employer")
    assert score < 0.5

def test_trust_clamped_0_1():
    eid = engine.create_employer({"names": ["Extreme Co"], "phones": ["065-888-999"],
        "source": "test", "trust_signals": {"positive": ["a"]*50, "negative": []}, "verified": True})
    score = engine.calculate_trust(eid, "employer")
    assert 0.0 <= score <= 1.0

# ── Worker Tests ────────────────────────────────────────────────────────────

def test_create_worker():
    wid = engine.create_worker({"names": ["Marko"], "phones": ["066-111-222"], "source": "facebook"})
    assert wid.startswith("wrk_")

def test_find_worker():
    wid = engine.create_worker({"names": ["Jelena"], "phones": ["067-333-444"], "experience": ["branje malina"], "source": "telegram"})
    wrk = engine.find_worker(wid)
    assert wrk is not None
    assert "Jelena" in wrk["names"]

# ── Case Tests ──────────────────────────────────────────────────────────────

def test_create_case():
    cid = engine.create_case({
        "case_type": "complaint",
        "employer_id": "emp_test",
        "description": "Neisplaćena plata",
        "source": "facebook_report",
    })
    assert cid.startswith("case_")

def test_find_cases_by_employer():
    engine.create_case({"case_type": "fraud", "employer_id": "emp_123", "description": "Test", "source": "test"})
    cases = engine.find_cases(employer_id="emp_123")
    assert len(cases) >= 1

def test_find_cases_empty():
    cases = engine.find_cases(employer_id="never_seen")
    assert len(cases) == 0

# ── Knowledge Tests ─────────────────────────────────────────────────────────

def test_store_knowledge():
    kid = engine.store_knowledge({"category": "salary", "key": "Arilje malina dnevnica", "value": "5000-6000 RSD", "source": "market_data"})
    assert kid.startswith("knw_")

def test_query_knowledge():
    engine.store_knowledge({"category": "salary", "key": "test query", "value": "123", "source": "test"})
    results = engine.query_knowledge(category="salary")
    assert len(results) >= 1

def test_query_knowledge_by_key():
    engine.store_knowledge({"category": "crop", "key": "unique_key_xyz", "value": "test", "source": "test"})
    results = engine.query_knowledge(key="unique_key_xyz")
    assert len(results) >= 1

# ── Index Tests ─────────────────────────────────────────────────────────────

def test_phone_index():
    eid = engine.create_employer({"names": ["PhoneIdx"], "phones": ["069-000-001"], "source": "test"})
    results = engine.search_phone("069-000-001")
    assert len(results) >= 1

def test_phone_index_empty():
    results = engine.search_phone("000-000-000")
    assert len(results) == 0

def test_name_index():
    engine.create_employer({"names": ["UniqueNameXYZ"], "phones": ["068-999-000"], "source": "test"})
    results = engine.search_name("UniqueNameXYZ")
    assert len(results) >= 1

def test_location_index():
    engine.create_employer({"names": ["LocCo"], "phones": ["068-111-000"], "regions": ["Arilje"], "source": "test"})
    results = engine.search_location("Arilje")
    assert len(results) >= 1

# ── Duplicate Detection Tests ───────────────────────────────────────────────

def test_detect_duplicate_by_phone():
    engine.create_employer({"names": ["DupPhone"], "phones": ["070-111-222"], "source": "test"})
    results = engine.detect_duplicate(phones=["070-111-222"])
    assert len(results) >= 1

def test_detect_duplicate_by_name():
    engine.create_employer({"names": ["DupName Co"], "phones": ["070-333-444"], "source": "test"})
    results = engine.detect_duplicate(names=["DupName Co"])
    assert len(results) >= 1

def test_detect_duplicate_none():
    results = engine.detect_duplicate(phones=["999-999-999"])
    assert len(results) == 0

# ── Memory Context Tests ────────────────────────────────────────────────────

def test_context_known_employer():
    eid = engine.create_employer({"names": ["CtxEmp"], "phones": ["071-111-222"], "source": "test", "complaints": 2})
    ctx = engine.get_context(phones=["071-111-222"])
    assert ctx.known_employer is not None
    assert ctx.employer_complaints == 2

def test_context_unknown():
    ctx = engine.get_context(phones=["888-888-888"])
    assert ctx.known_employer is None

def test_context_duplicate():
    engine.create_employer({"names": ["DupCtx"], "phones": ["071-333-444"], "source": "test"})
    ctx = engine.get_context(phones=["071-333-444"])
    assert ctx.duplicate_lead is True

# ── History Tests ───────────────────────────────────────────────────────────

def test_employer_history_preserved():
    eid = engine.create_employer({"names": ["HistCo"], "phones": ["072-111-222"], "source": "test"})
    engine.update_employer(eid, {"notes": "v2"}, "Andrii")
    engine.update_employer(eid, {"notes": "v3"}, "Andrii")
    emp = engine.find_employer(eid)
    assert len(emp["_history"]) >= 3

def test_worker_history_preserved():
    wid = engine.create_worker({"names": ["HistWrk"], "phones": ["072-333-444"], "source": "test"})
    wrk = engine.find_worker(wid)
    assert len(wrk["_history"]) >= 1

# ── Hash Tests ──────────────────────────────────────────────────────────────

def test_phone_hash_deterministic():
    assert _hash_phone("064-123-4567") == _hash_phone("0641234567")

def test_phone_hash_different():
    assert _hash_phone("064-111-1111") != _hash_phone("064-222-2222")

def test_id_generation():
    eid = _make_id("emp")
    assert eid.startswith("emp_")
    assert len(eid) > 8

# ── Validation Tests ────────────────────────────────────────────────────────

def test_validator_passes():
    from memory_validator import validate
    ok, errors = validate()
    assert ok is True
    assert len(errors) == 0

# ── Trust Model Tests ───────────────────────────────────────────────────────

def test_trust_positive_signals():
    eid = engine.create_employer({"names": ["PosCo"], "phones": ["073-111-222"],
        "source": "test", "trust_signals": {"positive": ["verified_contact", "multiple_jobs"], "negative": []}})
    score = engine.calculate_trust(eid, "employer")
    assert score > 0.5

def test_trust_negative_signals():
    eid = engine.create_employer({"names": ["NegCo"], "phones": ["073-333-444"],
        "source": "test", "trust_signals": {"positive": [], "negative": ["complaint", "spam"]}})
    score = engine.calculate_trust(eid, "employer")
    assert score < 0.5

def test_trust_zero_complaints():
    eid = engine.create_employer({"names": ["ZeroCo"], "phones": ["073-555-666"], "source": "test", "complaints": 0, "fraud_reports": 0})
    score = engine.calculate_trust(eid, "employer")
    assert score >= 0.5

# ── Append-Only Tests ───────────────────────────────────────────────────────

def test_original_values_preserved():
    eid = engine.create_employer({"names": ["Original"], "phones": ["074-111-222"], "source": "test", "jobs_published": 1})
    engine.update_employer(eid, {"jobs_published": 10})
    emp = engine.find_employer(eid)
    # Original creation is in history
    assert emp["jobs_published"] == 10  # Updated value
    assert any("created" in h["action"] for h in emp["_history"])

# ── Schema Compliance Tests ─────────────────────────────────────────────────

def test_employer_has_required_fields():
    eid = engine.create_employer({"names": ["SchemaTest"], "phones": ["075-111-222"], "source": "test"})
    emp = engine.find_employer(eid)
    required = ["employer_id", "names", "phones", "trust_score", "source", "created_at"]
    for field in required:
        assert field in emp, f"Missing: {field}"

def test_worker_has_required_fields():
    wid = engine.create_worker({"names": ["SchemaWrk"], "phones": ["075-333-444"], "source": "test"})
    wrk = engine.find_worker(wid)
    required = ["worker_id", "names", "phones", "trust_score", "source", "created_at"]
    for field in required:
        assert field in wrk, f"Missing: {field}"

def test_case_has_required_fields():
    cid = engine.create_case({"case_type": "complaint", "description": "test", "source": "test"})
    case = engine._read("cases", cid)
    required = ["case_id", "case_type", "status", "source", "created_at"]
    for field in required:
        assert field in case, f"Missing: {field}"

def test_knowledge_has_required_fields():
    kid = engine.store_knowledge({"category": "test", "key": "k", "value": "v", "source": "test"})
    entry = engine._read("knowledge", kid)
    required = ["entry_id", "category", "key", "value", "source", "created_at"]
    for field in required:
        assert field in entry, f"Missing: {field}"

# ── Edge Case Tests ─────────────────────────────────────────────────────────

def test_multiple_phones_same_employer():
    eid = engine.create_employer({"names": ["MultiPhone"], "phones": ["080-111-111", "080-222-222"], "source": "test"})
    results = engine.search_phone("080-111-111")
    assert len(results) >= 1
    results2 = engine.search_phone("080-222-222")
    assert len(results2) >= 1

def test_memory_context_no_phones():
    ctx = engine.get_context()
    assert ctx.known_employer is None
    assert ctx.duplicate_lead is False

def test_knowledge_query_empty():
    results = engine.query_knowledge(category="nonexistent_category")
    assert len(results) == 0

def test_create_case_with_worker():
    wid = engine.create_worker({"names": ["CaseWorker"], "phones": ["081-111-222"], "source": "test"})
    cid = engine.create_case({"case_type": "complaint", "worker_id": wid, "description": "test", "source": "test"})
    cases = engine.find_cases(worker_id=wid)
    assert len(cases) >= 1

def test_update_employer_append_names():
    eid = engine.create_employer({"names": ["Name1"], "phones": ["082-111-222"], "source": "test"})
    engine.update_employer(eid, {"names": ["Name2"]})
    emp = engine.find_employer(eid)
    assert "Name2" in emp["names"]

# ── Run ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    tests = [
        test_create_employer, test_find_employer, test_update_employer,
        test_update_nonexistent, test_employer_trust_default,
        test_employer_verified_boosts_trust, test_employer_complaints_lower_trust,
        test_trust_clamped_0_1,
        test_create_worker, test_find_worker,
        test_create_case, test_find_cases_by_employer, test_find_cases_empty,
        test_store_knowledge, test_query_knowledge, test_query_knowledge_by_key,
        test_phone_index, test_phone_index_empty, test_name_index, test_location_index,
        test_detect_duplicate_by_phone, test_detect_duplicate_by_name,
        test_detect_duplicate_none,
        test_context_known_employer, test_context_unknown, test_context_duplicate,
        test_employer_history_preserved, test_worker_history_preserved,
        test_phone_hash_deterministic, test_phone_hash_different, test_id_generation,
        test_validator_passes,
        test_trust_positive_signals, test_trust_negative_signals,
        test_trust_zero_complaints,
        test_original_values_preserved,
        test_employer_has_required_fields, test_worker_has_required_fields,
        test_case_has_required_fields, test_knowledge_has_required_fields,
        test_multiple_phones_same_employer, test_memory_context_no_phones,
        test_knowledge_query_empty, test_create_case_with_worker,
        test_update_employer_append_names,
    ]
    for t in tests:
        t()
    print(f"[PASS] All {len(tests)} memory engine tests passed")
    shutil.rmtree(tmpdir)
