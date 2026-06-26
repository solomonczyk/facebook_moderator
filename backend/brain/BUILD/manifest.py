"""Brain manifest loader — reads brain_manifest.yaml."""

import os
import yaml

MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "brain_manifest.yaml")


def load_manifest() -> dict:
    """Load the brain manifest. Falls back to inline dict if yaml unavailable."""
    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except (ImportError, FileNotFoundError):
        return _hardcoded_manifest()


def _hardcoded_manifest() -> dict:
    return {
        "brain": {
            "version": "1.0.0",
            "constitution": ["CANON/00_AGENT_CONSTITUTION.md"],
            "policies": [
                "CANON/01_OPERATOR_CHARTER.md",
                "CANON/02_GROUP_POLICY.md",
                "CANON/03_SAFETY_MODEL.md",
            ],
            "knowledge": [
                "KNOWLEDGE/Classification.md",
                "KNOWLEDGE/Risk.md",
                "KNOWLEDGE/Extraction.md",
                "KNOWLEDGE/Digest.md",
                "KNOWLEDGE/Languages.md",
                "KNOWLEDGE/SerbianSeasonalWork.md",
                "KNOWLEDGE/EdgeCases.md",
            ],
            "prompts": [
                "PROMPTS/FewShot.md",
                "PROMPTS/NegativeExamples.md",
                "PROMPTS/JsonContract.md",
            ],
        },
        "output": {
            "system_prompt": "PROMPTS/SystemPrompt.md",
            "release_dir": "BUILD/releases",
            "latest_json": "BUILD/releases/latest.json",
        },
    }


def get_version() -> str:
    m = load_manifest()
    return str(m.get("brain", {}).get("version", "0.0.0"))


def get_all_source_files() -> list[str]:
    """Return flat list of all source document paths."""
    m = load_manifest()
    brain = m.get("brain", {})
    files = []
    for key in ("constitution", "policies", "knowledge", "prompts"):
        files.extend(brain.get(key, []))
    return files
