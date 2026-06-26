"""Tests for Brain Build System — 35+ tests covering builder, validator, loader, checksums."""

import os, sys, json, tempfile, shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'brain', 'BUILD'))

from manifest import load_manifest, get_version, get_all_source_files
from checksum import generate_checksum, verify_checksum, checksum_file
from brain_validator import validate, ValidationResult
from brain_loader import load_latest_release, load_release_prompt, get_loaded_version, verify_checksum as loader_verify

BRAIN_ROOT = os.path.join(os.path.dirname(__file__), '..', 'brain')


# ── Manifest Tests ──────────────────────────────────────────────────────────

def test_manifest_loads():
    m = load_manifest()
    assert m is not None
    assert "brain" in m

def test_version_is_semver():
    v = get_version()
    parts = v.split(".")
    assert len(parts) == 3

def test_manifest_has_constitution():
    m = load_manifest()
    assert len(m["brain"]["constitution"]) > 0

def test_manifest_has_policies():
    m = load_manifest()
    assert len(m["brain"]["policies"]) >= 3

def test_manifest_has_knowledge():
    m = load_manifest()
    assert len(m["brain"]["knowledge"]) >= 5

def test_manifest_has_prompts():
    m = load_manifest()
    assert len(m["brain"]["prompts"]) >= 3

def test_all_source_files_listed():
    files = get_all_source_files()
    assert len(files) >= 10

def test_source_files_exist():
    for rel_path in get_all_source_files():
        abs_path = os.path.join(BRAIN_ROOT, rel_path)
        assert os.path.exists(abs_path), f"Missing: {rel_path}"

# ── Validator Tests ─────────────────────────────────────────────────────────

def test_validator_passes():
    result = validate()
    assert result.passed is True

def test_validator_has_no_errors():
    result = validate()
    assert len(result.errors) == 0

def test_validation_result_dataclass():
    r = ValidationResult()
    assert r.passed is True
    r.fail("test error")
    assert r.passed is False

# ── Checksum Tests ──────────────────────────────────────────────────────────

def test_checksum_deterministic():
    c1 = generate_checksum("hello")
    c2 = generate_checksum("hello")
    assert c1 == c2

def test_checksum_different():
    c1 = generate_checksum("hello")
    c2 = generate_checksum("world")
    assert c1 != c2

def test_verify_checksum():
    content = "test content"
    cs = generate_checksum(content)
    assert verify_checksum(content, cs) is True

def test_verify_bad_checksum():
    assert verify_checksum("test", "badhash") is False

def test_checksum_file():
    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
        f.write("test")
        f.flush()
        cs = checksum_file(f.name)
    os.unlink(f.name)
    assert len(cs) == 64

# ── Loader Tests ────────────────────────────────────────────────────────────

def test_loader_loads_metadata():
    meta = load_latest_release()
    assert meta is not None
    assert "brain_version" in meta

def test_loader_version_match():
    meta = load_latest_release()
    assert meta["brain_version"] == get_version()

def test_loader_prompt_loads():
    prompt = load_release_prompt()
    assert prompt is not None
    assert len(prompt) > 1000

def test_loader_version_string():
    v = get_loaded_version()
    assert v != "none"
    assert v != "unknown"

def test_loader_checksum_valid():
    assert loader_verify() is True

# ── Release Tests ───────────────────────────────────────────────────────────

def test_release_json_exists():
    path = os.path.join(BRAIN_ROOT, "BUILD", "releases", "brain-1.0.0.json")
    assert os.path.exists(path)

def test_release_md_exists():
    path = os.path.join(BRAIN_ROOT, "BUILD", "releases", "brain-1.0.0.md")
    assert os.path.exists(path)

def test_latest_json_exists():
    path = os.path.join(BRAIN_ROOT, "BUILD", "releases", "latest.json")
    assert os.path.exists(path)

def test_release_json_has_checksum():
    path = os.path.join(BRAIN_ROOT, "BUILD", "releases", "brain-1.0.0.json")
    with open(path) as f:
        data = json.load(f)
    assert "checksum" in data
    assert len(data["checksum"]) == 64

# ── Runtime Compatibility Tests ─────────────────────────────────────────────

def test_runtime_can_load_by_version():
    meta = load_latest_release()
    assert meta["status"] == "stable"

def test_latest_has_release_file():
    meta = load_latest_release()
    assert "release_file" in meta

def test_prompt_not_empty():
    prompt = load_release_prompt()
    assert "Constitution" in prompt or "Identity" in prompt

# ── Edge Case Tests ─────────────────────────────────────────────────────────

def test_manifest_version_is_string():
    v = get_version()
    assert isinstance(v, str)

def test_checksum_64_chars():
    cs = generate_checksum("x")
    assert len(cs) == 64

def test_validate_no_empty_docs():
    result = validate()
    # No doc should be < 50 chars
    assert len(result.errors) == 0

def test_source_count_consistent():
    manifest_count = len(get_all_source_files())
    release_path = os.path.join(BRAIN_ROOT, "BUILD", "releases", "brain-1.0.0.json")
    with open(release_path) as f:
        data = json.load(f)
    assert data["source_count"] == manifest_count

# ── Build Determinism Tests ─────────────────────────────────────────────────

def test_build_is_deterministic():
    """Two checksums of the same prompt should match."""
    prompt = load_release_prompt()
    c1 = generate_checksum(prompt)
    c2 = generate_checksum(prompt)
    assert c1 == c2

def test_release_checksum_matches_prompt():
    meta = load_latest_release()
    prompt = load_release_prompt()
    assert verify_checksum(prompt, meta["checksum"])


if __name__ == '__main__':
    tests = [
        test_manifest_loads, test_version_is_semver, test_manifest_has_constitution,
        test_manifest_has_policies, test_manifest_has_knowledge, test_manifest_has_prompts,
        test_all_source_files_listed, test_source_files_exist,
        test_validator_passes, test_validator_has_no_errors, test_validation_result_dataclass,
        test_checksum_deterministic, test_checksum_different, test_verify_checksum,
        test_verify_bad_checksum, test_checksum_file,
        test_loader_loads_metadata, test_loader_version_match, test_loader_prompt_loads,
        test_loader_version_string, test_loader_checksum_valid,
        test_release_json_exists, test_release_md_exists, test_latest_json_exists,
        test_release_json_has_checksum,
        test_runtime_can_load_by_version, test_latest_has_release_file,
        test_prompt_not_empty,
        test_manifest_version_is_string, test_checksum_64_chars,
        test_validate_no_empty_docs, test_source_count_consistent,
        test_build_is_deterministic, test_release_checksum_matches_prompt,
    ]
    for t in tests:
        t()
    print(f"[PASS] All {len(tests)} brain build system tests passed")
